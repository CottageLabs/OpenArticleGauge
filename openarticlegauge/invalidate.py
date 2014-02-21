""" invalidation of uknown licences for plugins which have been added or changed """

"""
Usage:

1/ Remove all unknown licenses:

invalidate.py -a -u

2/ Remove all unknown licenses from a specific handler

invalidate.py -p handler_name -v handler_version -u

3/ Remove all licenses of a specific type from a specific handler

invalidate.py -p handler_name -v handler_version -t license_type

4/ Remove all licenses which were not applied by a handler, but because no handler was able to identify a licence for that item

invalidate.py -e -u

Definition of options:

-e - license has /no/ handlers (required if -a or -p is not specified)
-a - all handlers of all versions AND those which have no handlers (required if -e or -p is not specified)
-p - the name of the handler (required if -a or -e is not specified)
-v - the version of the handler (optional).  If omitted, all versions of the handler will be dealt with.  Must only be present if -p is specified
-t - the type of license to be removed (required if -u is not specified)
-u - the unknown license (required if -t is not specified)

"""
from openarticlegauge import models
import json

ES_PAGE_SIZE = 100

def invalidate_license(license_type=None, handler=None, handler_version=None, treat_none_as_missing=False, reporter=None):
    """
    Invalidate all licences with the specified licence type.  The handler and handler_version may
    be left unset, or set to a specific value.  If left unset then treat_none_as_missing may be used
    to expressly indicate whether a None value for the handler is a wildcard or implies that there
    is no handler specified
    
    arguments
    license_type -- the type of the licence as would appear in the bibjson record in bibjson['license'][n]['type']
        common values include failed-to-obtain-licence, cc-by, cc0, etc, but there are a long list of possible options
    handler -- the name of the handler which assigned the licence
    handler_version -- the version of the named handler which assigned the licence (should be a string, e.g. "1.0.2")
    treat_none_as_missing -- if True, then if handler=None then this will look for licences which do not have a handler associated with them
                             if False, then if handler=None then this will look for any value (other than None) in the handler field
    reporter -- a callback function which can be used to report on the progress of this method.  Used for command line or logging integration
    
    """
    
    # the reporter is a callback which handles messages of the progress of this operation.  If none
    # is specified we operate silently
    if reporter is None:
        reporter = lambda x: None
    
    if license_type is None and handler is None:
        msg = "can't execute without at least license type or handler"
        reporter(msg)
        return None
    
    # report on the operation we are going to carry out
    msg = "invalidating license type '" + license_type + "' for "
    if handler is None:
        msg += "all versions of all handlers"
    else:
        msg += "handler '" + handler + "'"
        if handler_version is not None:
            msg += ", version " + handler_version
        else:
            msg += " (all versions)"
    reporter(msg)
    
    # assemble an initial ElasticSearch query object
    query = {
        "filter" : { 
            "and" : [
                {"term" : {"license.type.exact" : license_type}}
            ]
        }
    }
    if handler is not None:
        query['filter']['and'].append({"term" : {"license.provenance.handler.exact" : handler}})
    if handler_version is not None:
        query['filter']['and'].append({"term" : {"license.provenance.handler_version.exact" : handler_version}})
    
    # report on the query
    reporter("using initial search query: " + json.dumps(query))
    
    # now delegate to invalidate_license_by_query
    invalidate_license_by_query(query, license_type=license_type, handler=handler, handler_version=handler_version, treat_none_as_missing=treat_none_as_missing, reporter=reporter)

def invalidate_license_by_query(query, license_type=None, handler=None, handler_version=None, treat_none_as_missing=None, reporter=None):
    """
    The query is used to select the records which are affected, the license_type, hander and handler_version are used to 
    determine which license(s) to remove from the selected record
    
    Use this with immense caution.
    
    The query provides a result set to which the license_type, handler and handler_version will be applied to filter out
    licences that match.  This means you have to be very clear about what your query is achieving, especially in the case that
    an item has more than one licence.  Licences are NOT nested objects in ES, and so if you ask for records which have licence.type=cc-by
    and licence.provenance.handler=plugin_a, you will not necessarily guarantee that they match in the same licence object
    in the list of items.
    
    """
    # the reporter is a callback which handles messages of the progress of this operation.  If none
    # is specified we operate silently
    if reporter is None:
        reporter = lambda x: None
    
    # set us up for paging
    query["size"] = ES_PAGE_SIZE
    query["from"] = 0
    
    # page through the results and do the invalidation
    first = True
    while True:
        # do the query
        response = models.Record.query(q=query)
        
        # get the important numbers for paging
        total = response.get("hits", {}).get("total", 0)
        page_size = len(response.get("hits", {}).get("hits", []))
        end_of_current_page = query["from"] + page_size
        
        if first:
            reporter("total number of relevant records found: " + str(total))
            first = False
        reporter("processing records " + str(query["from"]) + " - " + str(end_of_current_page))
        
        # process the response from the query
        # FIXME: we still need the parameters for license_type, handler, handler_version
        _process_response(response, license_type, handler, handler_version, treat_none_as_missing, reporter)
        
        if total > end_of_current_page:
            query["from"] = query["from"] + query["size"]
        else:
            break

def _process_response(response, license_type, handler, handler_version, treat_none_as_missing, reporter):
    """
    Process the Elasticsearch response object by taking all the records therein and deleting
    the licences consistent with the arguments.
    
    arguments:
    response -- Elastic search response object containing bibjson records as the individual results
    license_type -- the type of licence to remove
    handler -- the handler to remove (can be None)
    handler_version -- the handler_version to remove (can be None)
    treat_none_as_missing -- if True, then if handler=None then this will look for licences which do not have a handler associated with them
                             if False, then if handler=None then this will look for any value (other than None) in the handler field
    reporter -- a callback function which can be used to report on the progress of this method.  Used for command line or logging integration
    
    """
    # extract the records
    records = [hit.get("_source") for hit in response.get("hits", {}).get("hits", [])]
    
    # for each record go through all of its licences and delete any which meet the criteria provided
    for record in records:
        reporter("processing id: " + str(record.get("id")))
        keep = []
        for license in record.get("license", []):
            type_match = license.get("type") == license_type
            handler_match = _handler_match(license, handler, treat_none_as_missing)
            version_match = license.get("provenance", {}).get("handler_version") == handler_version if handler_version is not None else True
            if not (type_match and handler_match and version_match):
                keep.append(license)
        diff = len(record.get('license', [])) - len(keep) 
        record['license'] = keep
        reporter("removed " + str(diff) + " licenses from " + str(record.get("id")))
    
    # now push the records back to the index
    models.Record.bulk(records)

def _handler_match(license, handler, treat_none_as_missing):
    """
    Determine if the supplied license matches the handler and the treat_none_as_missing treatment
    
    arguments:
    license -- the license extracted from the bibjson record
    handler -- the name of the handler to match (can be None)
    treat_none_as_missing -- if True, then if handler=None then this will look for licences which do not have a handler associated with them
                             if False, then if handler=None then this will look for any value (other than None) in the handler field
    
    returns:
    True if the handler matches the licence or if it is None and treat_none_as_missing is True and there is no handler in the licence
    False otherwise
    
    """
    
    # This method is a bit painful.  Here is the truth table:
    #
    # license handler   handler             treat_none_as_missing   match?      reason
    # not None          matching text       True                    True        text matches
    #                                       False                   True        text matches
    #                   not matching text   True                    False       text does not match
    #                                       False                   False       text does not match
    #                   None                True                    False       no match, but license handler exists, so match is False because license is not missing
    #                                       False                   True        
    # None              not matching text   True                    False
    #                                       False                   False
    #                   None                True                    True
    #                                       False                   True
    #
    # A one line implementation is no doubt possible, but virtually incomprehendible, so
    # we break it down a bit
    
    prov_handler = license.get("provenance", {}).get("handler")
    
    # this line meets all but the last two cases of the above truth table
    if prov_handler is not None:
        match = prov_handler == handler if handler is not None else not treat_none_as_missing
    else:
        match = False if handler is not None else True
    
    return match

def stdout_reporter(msg):
    print msg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--empty", help="specify that the invalidation option should look for cases where no handler or handler version is available.  Must be present if -p is not specified", action="store_true")
    parser.add_argument("-a", "--all", help="speficy that all handlers should be dealt with by this invalidation operation.  Must be present if -p or -e is not specified", action="store_true")
    parser.add_argument("-p", "--plugin", help="the handler whose license to invalidate. Must be present if -a or -e is not specified")
    parser.add_argument("-v", "--version", help="the version of the handler whose license to invalidate (must only be present if -p is specified")
    parser.add_argument("-u", "--unknown", help="short cut for specifying the unknonw license as the target license to remove.  Must be present if -t is not specified", action="store_true")
    parser.add_argument("-t", "--type", help="explicitly specify the type of the license to be removed (use with caution).  Must be present if -u is not specified")

    args = parser.parse_args()

    # -a, -p and -e are mutually exclusive
    if args.all and args.plugin is not None:
        print "Cannot specify -a and -p  in the same command"
        exit()
        
    if args.all and args.empty:
        print "Cannot specify -a and -e in the same command"
        exit()
    
    if args.plugin and args.empty:
        print "Cannot specify -p and -e in the same command"
        exit()

    # must have one or other of -a or -p
    if not args.all and args.plugin is None:
        print "Must specify either -a or -p"
        exit()

    # -v requires -p to be specified
    if args.plugin is None and args.version is not None:
        print "Must specify -p if using the -v argument"
        exit()

    # -a and -v are mutually exclusive (shouldn't ever get triggered)
    if args.all and args.version is not None:
        print "Cannot specify -a and -v in the same command"
        exit()

    # -u and -t are mutually exclusive    
    if args.unknown and args.type is not None:
        print "Cannot specify -u and -t in the same command"
        exit()
        
    # must have one or other of -u or -t
    if not args.unknown and args.type is None:
        print "Must specify either -u or -t"
        exit()

    # now figure out the real values
    license_type = "failed-to-obtain-license" if args.unknown else args.type
    handler = args.plugin
    handler_version = args.version
    treat_none_as_missing = args.empty
    
    # and send off to the routine that invalidates licenses
    invalidate_license(license_type, handler, handler_version, treat_none_as_missing, stdout_reporter)


    





