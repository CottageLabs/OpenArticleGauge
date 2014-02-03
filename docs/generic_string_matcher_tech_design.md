#Generic string matcher technical design

We learned [from the requirements](generic_string_matcher_requirements.md)
that we need to build 4 things: user license statement form, an
administrative interface, a list of supported statements and finally, a
plugin which has dynamic configuration and matches strings from there to
incoming HTML pages.

We'll focus on the user-facing components first, since that'll best
inform the technical design of the plugin itself later on.

##"Configurations"
A configuration is a bundle of data: license statements mapped to
licenses, list of URL-s where those license statements can be found and
the publisher who publishes the journals given by the URL-s.

```json
{
    "publisher": "PLoS",
    "journal_urls": [
        "www.plosone.org",
        "www.plosntds.org"
    ],
    "licenses": [
        {
        "This article is available under CC-BY.":
            {
                "license_type": "cc-by",
                "version": "",
                "example_article_url": "http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0031314"
            }
        },
        {
        "This article is available under CC-BY-NC v.3.0.":
            {
                "license_type": "cc-by-nc",
                "version": "3.0",
                "example_article_url": "http://a_url"
            }
        }
    ]
}
```

##Public user-facing form to manage license statements
"Let OpenArticleGauge recognise new license statements"

```
    -----------------
    Publisher name
    -----------------
    Journal URL (+) (e.g.: www.plosone.org. Folders work too
    (http://aprendeenlinea.udea.edu.co/revistas/index.php/red) as long
    as all articles in the journal can be found under that folder.)
    -----------------
    License statement   License   Version (optional)      Example article URL
    v
    v   [textarea]      [drop     [version text input]    [URL text input]          (+)
    v                   down]

                        Submit
```

All fields are mandatory unless noted otherwise above.

The + button on the URL field would add up to 10 new fields, after which
it would continue adding them, but also append a message to the page
telling the user to raise an issue on github if they need to add
licenses for lots of URL-s.

Same for the + button on the license statement row of inputs.

When editing records, add an additional tickbox before the License
statement column called "Active?".

When entering URL-s, users should be informed if a configuration
matching those URL-s already exists, like on Stackoverflow where you get
similar questions while typing in your own. Will need to clarify what to
do if only 1 out of multiple entered URL-s is matched by another
configuration.

##Administrative interface
The requirements seem to be "list all configurations", "allow sorting",
"allow searching". This sounds like facetview to me, with each record
having a link to a page presenting with a prepopulated form just like
the one above.

Again, users need to have a list too, and it'd be bad to give admins the
ability to search and sort and NOT give that to the users who are far
less familiar with the data. We should clarify this.

##Public user-facing list of supported statements.
A faceted search has proven itself to be a great UI method for searching
and we can do it more quickly than other ways of building lists (e.g.
tabular). + we'd have no search then.

We should think a bit about where to integrate this list on the OAG
overall interface so that it's easily discoverable. Maybe have a
Publishers menu on the top?

This will need to let users search by publisher name and URL in some
obvious way, so that publishing staff can check their journals are
supported by OAG.

##The plugin

###Datastore choice
The dynamic persistent datastore for the plugin should be Elasticsearch
as we're already using it, this info won't take much resources to hold
in there, and it gives us cool searching abilities which we will utilise
both in the UI and in the plugin itself.

###Read the configuration
To start, the plugin will read the user-submitted configurations every
single time it runs (we may change this if it causes performance
trouble).

###Match the configurations to the URL of the article
When it runs, it will have the URL of the article available. So
when retrieving configurations, it should ask  elasticsearch for those
which have URL-s which match the incoming article URL. Alternatively, it
can fetch all the configs and look to see if any of their URL-s match
the beginning of the article's URL. (www.plosone.org may match
www.plosone.org/article)

We strip http:// from all URL-s. We may need to do the same for www too
(not other subdomains obviously). What if an article resolves to
plosone.org/article but the config holds www.plosone.org - it won't
match.

It's also possible that multiple configs match (it gets hairy here). If
so, the plugin will need to pick the order in which they run - current
proposition is to run the more specific match first (longer URL in the
config).

###The generic plugin should reuse the OAG workflow, not make its own
But, if a config results in a match, does the chain stop or not? (It
does for the current Ubiquitous plugin, not for publisher-specific
ones.)

Richard raised an important point here - the plugin should NOT decide at
all what to do beyond the order of running the configs. This is because
we already wrote this logic in the OAG workflow module. So we should
reuse it, not duplicate it, since maintainance will be terrible if we
duplicate this complex bit of logic.

###This is how we can achieve the reuse of workflow logic
So, Generic should create plugins on-the-fly out of matching
configurations and hand them to the OAG workflow. They will all be
version 1.0, and will take (e.g.) the slugified name of the publisher as
the plugin name. (Which means we should probably use this as a unique ID
for all configs, to prevent hairy problems at this step if somebody
    submits PLoS and I submit plos).

Note: slugify means turning "Oxford Journals" into "oxford-journals",
basically.

###Other notes on workflow logic reuse and its impact
This reuse of workflow logic will also allow us to use all current
license management tools like the invalidation of licenses in a much
better way. Instead of invalidating all licenses done by "generic" we
will be able to invalidate all done by "plos" instead.
