""" invalidation of uknown licences for plugins which have been added or changed """

"""
Usage:

1/ Remove all unknown licenses:

invalidate.py -a -u

2/ Remove all unknown licenses from a specific handler

invalidate.py -h handler_name -v handler_version -u

3/ Remove all licenses of a specific type from a specific handler

invalidate.py -h handler_name -v handler_version -t license_type

4/ Remove all licenses which were not applied by a handler, but because no handler was able to identify a licence for that item

invalidate.py -e -u

Definition of options:

-e - license has /no/ handlers (required if -a or -p is not specified)
-a - all handlers of all versions AND those which have no handlers (required if -e or -p is not specified)
-p - the name of the handler (required if -a or -e is not specified)
-v - the version of the handler (optional).  If omitted, all versions of the handler will be dealt with.  Must only be present if -h is specified
-t - the type of license to be removed (required if -u is not specified)
-u - the unknown license (required if -t is not specified)

"""
from isitopenaccess import models
import json

ES_PAGE_SIZE = 100

def invalidate_license(license_type, handler=None, handler_version=None, treat_none_as_missing=False, reporter=None):
    # the reporter is a callback which handles messages of the progress of this operation.  If none
    # is specified we operate silently
    if reporter is None:
        reporter = lambda x: None
    
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
        },
        "size" : ES_PAGE_SIZE,
        "from" : 0
    }
    if handler is not None:
        query['filter']['and'].append({"term" : {"license.provenance.handler.exact" : handler}})
    if handler_version is not None:
        query['filter']['and'].append({"term" : {"license.provenance.handler_version.exact" : handler_version}})
    
    # report on the query
    reporter("using initial search query: " + json.dumps(query))
    
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
        _process_response(response, license_type, handler, handler_version, treat_none_as_missing, reporter)
        
        if total > end_of_current_page:
            query["from"] = query["from"] + query["size"]
        else:
            break

def _process_response(response, license_type, handler, handler_version, treat_none_as_missing, reporter):
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

    parser.add_argument("-e", "--empty", help="specify that the invalidation option should look for cases where no handler or handler version is available.  Must be present if -h or -p is not specified", action="store_true")
    parser.add_argument("-a", "--all", help="speficy that all handlers should be dealt with by this invalidation operation.  Must be present if -h or -e is not specified", action="store_true")
    parser.add_argument("-p", "--plugin", help="the handler whose license to invalidate. Must be present if -a or -e is not specified")
    parser.add_argument("-v", "--version", help="the version of the handler whose license to invalidate (must only be present if -h is specified")
    parser.add_argument("-u", "--unknown", help="short cut for specifying the unknonw license as the target license to remove.  Must be present if -t is not specified", action="store_true")
    parser.add_argument("-t", "--type", help="explicitly specify the type of the license to be removed (use with caution).  Must be present if -u is not specified")

    args = parser.parse_args()

    # -a, -h and -e are mutually exclusive
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


    





