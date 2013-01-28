import plugins

# List of plugins that will run in order to detect the type of an identifier.
# All plugins will run
type_detection = [
    plugins.doi.type_detect_verify,
    plugins.pmid.type_detect_verify
]

# list of plugins that can be used to canonicalise all the different 
# identifier types.  Key is the identifier type as detected with type_detection,
# value is the plugin to be used
canonicalisers = {
    "doi" : plugins.doi.canonicalise,
    "pmid" : plugins.pmid.canonicalise
}

provider_detection = {
    "doi" : [plugins.doi.doi_provider], 
    "pmid" : [plugins.pmid.pmid_provider]
}

site_detection = {
    "http://www.plos.com/" : plugins.plos.plos_site,
    "bmc" : plugins.bmc.bmc_site
}

page_detection = {
    "http://www.plos.com/" : plugins.plos.plos_page,
    "bmc" : plugins.bmc.bmc_page
}
