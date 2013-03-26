""" invalidation of uknown licences for plugins which have been added or changed """

"""
Usage:

1/ Remove all unknown licenses:

invalidate.py -a -u

2/ Remove all unknown licenses from a specific handler

invalidate.py -h handler_name -v handler_version -u

3/ Remove all licenses of a specific type from a specific handler

invalidate.py -h handler_name -v handler_version -t license_type

Definition of options:

-a - all handlers of all versions (optional)
-u - the unknown license (required if -t is not specified)
-h - the name of the handler (required if -a is not specified)
-v - the version of the handler (optional).  If omitted, all versions of the handler will be dealt with.  Must only be present if -h is specified
-t - the type of license to be removed (required if -u is not specified)

"""

import models, json

ES_PAGE_SIZE = 100

def invalidate_license(license_type, handler=None, handler_version=None, reporter=None):
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
        first = False
        # do the query
        response = models.Record.query(q=query)
        
        # get the important numbers for paging
        total = response.get("hits", {}).get("total", 0)
        page_size = len(response.get("hits", {}).get("hits", []))
        end_of_current_page = query["from"] + page_size
        
        if first:
            reporter("total number of relevant records found: " + str(total))
        
        # process the response from the query
        _process_response(response, license_type, handler, handler_version, reporter)
        
        if total > end_of_current_page:
            query["from"] = query["from"] + query["size"]
        else:
            break

def _process_response(response, license_type, handler, handler_version, reporter):
    # extract the records
    records = [hit.get("_source") for hit in response.get("hits", {}).get("hits", [])]
    
    # for each record go through all of its licences and delete any which meet the criteria provided
    for record in records:
        reporter("processing id: " + str(record.get("id")))
        keep = []
        for license in record.get("license", []):
            type_match = license.get("type") == license_type
            handler_match = license.get("provenance", {}).get("handler") == handler if handler is not None else True
            version_match = license.get("provenance", {}).get("handler_version") == handler_version if handler_version is not None else True
            if not (type_match and handler_match and version_match):
                keep.append(license)
        diff = len(record.get('license', [])) - len(keep) 
        record['license'] = keep
        reporter("removed " + str(diff) + " licenses from " + str(record.get("id")))
    
    # now push the records back to the index
    models.Record.bulk(records)

def stdout_reporter(msg):
    print msg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--all", help="speficy that all handlers should be dealt with by this invalidation operation.  Must be present if -h is not specified", action="store_true")
    parser.add_argument("-p", "--plugin", help="the handler whose license to invalidate. Must be present if -a is not specified")
    parser.add_argument("-v", "--version", help="the version of the handler whose license to invalidate (must only be present if -h is specified")
    parser.add_argument("-u", "--unknown", help="short cut for specifying the unknonw license as the target license to remove.  Must be present if -t is not specified", action="store_true")
    parser.add_argument("-t", "--type", help="explicitly specify the type of the license to be removed (use with caution).  Must be present if -u is not specified")

    args = parser.parse_args()

    # -a and -h are mutually exclusive
    if args.all and args.plugin is not None:
        print "Cannot specify -a and -p in the same command"
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
    
    # and send off to the routine that invalidates licenses
    invalidate_license(license_type, handler, handler_version, stdout_reporter)


    





