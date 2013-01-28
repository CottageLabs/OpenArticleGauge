import plugins

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
