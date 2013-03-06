#How To Write a Page Licence Plugin Test

If you've written a plugin to scrape or extract a licence from a content provider's url.  We provide a skeleton test case to help you rapidly build your tests for your plugin, to ensure that it will work with the main IIOA application.

Make a copy of

    test_provider_skeleton.py

and use this as the basis for your new tests.  This implements 3 essential tests:

1. That your plugin will recognise provider URLs that it should
2. That your plugin will not respond to provider URLs that it should not
3. That your plugin can interpret pages that it will encounter, and successfully extract licences from them

At the top of that file are a set of instructions on how to customise the test for quick deployment.  In summary these steps are:

* import your plugin as "plugin" (here, replace "plos" with your plugin module's name)

    from isitopenaccess.plugins import plos as plugin

* set a list of urls which your plugin should be able to support

    SUPPORTED_URLS = ["http://www.plosone.org/1234", "www.plosbiology.org/fakjsskjdaf"]

* set a list of urls which your plugin should NOT support

    UNSUPPORTED_URLS = ["http://www.biomedcentral.com/", "askjdfsakjdhfsa"]

* a list of test files and a template licence object that should be extracted from that file (see below for more details on how to do format the licence object)

    RESOURCE_AND_RESULT = {
        "path/to/file" : {<licence object>}
    }

##Resource Files

When building unit tests for your page licence plugins, copies of HTML/XML/whatever format documents that you expect to recieve from the content provider's page can be placed in the tests/resources directory.

When you construct the RESOURCE_AND_RESULT object, you need to provide the path to the resource file, which you can do with an absolute path to a known location like

    RESOURCE_AND_RESULT = {
        "/home/user/myresources/testfile.html" : {<licence object>}
    }

If you place the file in the tests/resources directory, you can construct the correct path as follows:

    RESOURCE_AND_RESULT = {
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "testfile.html") : {<licence object>}
    }

##Licence Object for Comparison

In the RESOURCE_AND_RESULT object, you need to specify the parts of the licence object that you want to test.  This is done by providing a partial licence object which contains the values to be checked; the test_provider_skeleton.py file will automatically compare the licence retrieved from the resource file (see above) with the partial licence object for comparison.

The full specification of an IIOA licence object is:

    {
        "status": "active",
        "maintainer": "",
        "description": "",
        "family": ""
        "title": "Creative Commons Attribution",
        "domain_data": true/false,
        "url": "http://www.opendefinition.org/licenses/cc-by",                
        "version": "",
        "domain_content": true/false,
        "is_okd_compliant": true/false,
        "is_osi_compliant": true/false,
        "domain_software": true/false,
        "type": "cc-by",
        "jurisdiction": "",
        "open_access": true/false,
        "BY": true/false,
        "NC": true/false,
        "ND": true/false,
        "SA": true/false,
        "provenance": {
            "category": "page_scrape",
            "description": "how the content was acquired ...",
            "agent": "IsItOpenAccess Service/0.1 alpha",
            "source": "http://www.plosbiology.org/article/info%3Adoi%2F10...",
            "date": "2013-02-16T21:51:54.669040"
        }
    }

You will most likely only want to test a sub-set of these, depending on which fields your plugin sets.  The example provided in test_provider_skeleton.py is for a PLOS page, and consists of the following sub-set of the fields:

    {
        "id" : None,            # there should be no id field
        "version": "",          # version should be the empty string
        "type": "cc-by",        # type is cc-by
        "jurisdiction": "",     # jurisdiction should be the empty string
        "open_access": True,    # open_access is True
        "BY": True,             # BY is True
        "NC": False,            # NC is False
        "ND": False,            # ND is False
        "SA": False,            # SA is false
        "provenance": {
            "category": "page_scrape", # category is page_scrape
            "description": 'License decided by...', # description is a long string
            "agent": config.agent, # agent is from configuration
            "source": "http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001406", # source is the url where we look this record up
            "date": -1 # date is not null (but we don't know the exact value)
        }
    }

Notice that there are some fields which have a value of None and others that have a value of -1.  The rules for how the comparison licence is compared with the result licence are:

* if a key has a value, there resulting object's value must match exactly
* if a key has been omitted, it will not be tested
* if a key's value is the empty string, the resulting object's key's value must be the empty string
* if a key's value is None, the resulting object MUST NOT have the key or MUST be the empty string
* if a key's value is -1, the resulting object MUST have the key

##Running the Test

Tests can be run using nosetests.  In the "isitopenaccess" module directory, run:

    nosetests -v tests/test_provider_skeleton.py
    
(substituting the name of your test, obviously)


