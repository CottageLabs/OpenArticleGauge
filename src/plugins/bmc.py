def page_licence(record):
    """
    To respond to the provider identifier: http://www.biomedcentral.com
    
    This should determine the licence conditions of the BMC article and populate
    the record['bibjson']['license'] (note the US spelling) field.
    """
    # 1. get content
    import requests
    r = requests.get(record['provider'])
    
    # 2. see if required string is in content 
    test_for = "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited."

    # 3. return appropriate license.
    if test_for in r.content:
        record['bibjson']['license'] = 'CC-BY 2.0'

