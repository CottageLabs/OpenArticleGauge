from isitopenaccess.plugins import common as cpl # Common Plugin Logic

def supports(provider):
    """
    Does the page_license plugin support this provider
    """
    base_urls = ['www.cell.com']
    
    work_on = cpl.clean_urls(provider.get("url", []))
    
    for url in work_on:
        for bu in base_urls:
            if url.startswith(bu):
                return True
                
    return False

fail_why = '''It is currently not possible to obtain the license information of a Cell Reports article automatically.
The website makes heavy use of Javascript to update its pages dynamically.
Instead of just hiding text and using Javascript to show as appropriate (as users use the navigation menus), the website actually fetches previously unavailable content onto the page (using AJAX).
A user needs to click on the "Related Info" tab (#relatedinfo) which loads all the content for the sub-tabs "Acknowledgements", "Licensing Information" and "Publication Info.".
Intriguingly enough, the site does use the widely applied technique of simply hiding the content of tabs which are not currently selected, but only *for the sub-tabs*.
If the user selects the "Licensing Information" sub-tab at this point, they can finally see what we believe is intended to be the real license for the article.

Furthermore, if Javascript is disabled, there is NO way to get to the licensing information as far as we can tell.

Perusing this example page: http://www.cell.com/cell-reports/fulltext/S2211-1247%2812%2900426-3
DOI: 10.1016/j.celrep.2012.11.027

If Javascript is disabled, two copyright statements can be found on the page:
1. "2013 The Authors All rights reserved."
2. "Copyright &#169; 2013 <a target="Elsevier" href="http://www.elsevier.com">Elsevier Inc.</a> All rights reserved."
Besides the fact that those two may be in conflict and that the second one is nowhere to be found in the "enhanced" Javascript view, they may also be incorrect.

As far as we can tell (with Javascript turned on), the intention is that this should be an Open Access article available under a version of the CC-BY-NC-ND license.
This means that, contrary to those statements, not all copyright rights are reserved.

Of course, even we, as human users, cannot be sure of what the licensing status of this article actually is, since the licensing information we receive depends on whether we turn on Javascript in our browsers.

Since the Javascript operations are possible, but prohibitively difficult for a machine to perform, we are forced to mark all content by this publisher as NOT Open Access.
'''

fail_suggested_solution = '''Ideally, metadata can be embedded in the HTML of the page itself, as well as displayed to the user.
A less resource-intensive (for the publisher) solution might be to publish the license for ALL articles on Cell Reports as part of their "Summary" pages and make sure that is available in the "basic" (no-Javascript) view.

Another less resource-intensive solution is to get rid of the AJAX fetching previously unavailable content - make sure all the relevant text is on the page, then use Javascript to hide/show content as appropriate (as the user peruses the navigation menus). This is not recommended as it still leaves the website highly reliant on Javascript (which could be problematic for human users), but at least makes it possible to determine the status of an article with certainty (provided the issue described below is resolved).

For any of these solutions to be effective, the multiple copyright statements viewable in "basic" (no-Javascript) mode have to be taken care of. Are "all rights reserved", who does the copyright belong to (Elsevier or the authors?); or is this actually an Open Access article available under CC-BY-NC-ND?
'''

def page_license(record):
    """
    To respond to the provider identifier: http://www.cell.com
    
    This will always fail since we can't get the license for this publisher.
    It populates the record['bibjson']['license'] (note the US spelling) field.
    """
    source_url = None
    source_urls = record.get('provider', {}).get("url", [])
    if len(source_urls) > 0:
        source_url = source_urls[0]
    cpl.describe_license_fail(record, source_url, fail_why, fail_suggested_solution)
