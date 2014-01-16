#Generic string matcher requirements
##Why did we want to do this in the first place?

1. You have to be able to contribute code in order to contribute
licensing statements to the current OAG. This prevents most
crowdsourcing as well as authoritative information from non-technical
people working at publishers from making it into OAG.

2. It's not easy to edit licensing statements, but OAG is not very
useful without at least *most* of them being accurate. There's not that
much use in something which returns "could not determine license" all
the time. On the other hand the original developers cannot spend that
much time
rejigging licensing statements, but their time is probably
best used in other ways on the service (or elsewhere).

3. Too many plugins which do the same basic thing is just plain harder
to maintain, each with their own tests and so forth. It all boils down
to 2 functions:
    - "can you, the plugin, tell me more about this article - here's the
      URL" (usually 1 line of config and 5 lines of code repeated in all
      such plugins)
    - "match these license statements against the content of this page"
      (15-20 lines of config info and 1 line of code repeated in all
      such plugins)

##So what exactly do we want?
1. (from #1 and #2 above) Easy way of submitting new license statements,
editing old ones and deactivating old ones. (Maybe your company finally
fixed that pervasive typo.) "Easy" for non-technical people too. So, an
HTML form with as much help as we can afford in the dev time we have
(autocompletes if applicable, good use of colour, good prompts and
labels, validation without losing what the user has already input if
there is an error).

2. Replace all those string matching plugins with a single one,
generic_string_matcher . It should be able to read configuration from
a dynamic persistent data store. Basically, it should match a certain
URL to a list of license statements. Each of those statements will
correspond to a license recognised by OAG. Optionally a "version" can be
provided.

    This needs to integrate well with the rest of the system, possibly not a
    trivial thing.

3. An administrative interface. Opening up the service in this way means
that mistakes or even abuse can happen, so there should be a way of
fixing such situations. The needs of this are a bit different to
requirement 1, e.g. we'll probably need a list of all license statements
in the service, perhaps a search through them (to find URL-s when
asked). It can probably reuse the form that users would see for editing
the records.

    Also, we don't necessarily do application support to that level -
    administering license statements properly may turn out to require a
    (semi-)dedicated person, so this should be usable by people who are not
    Cottage Labs developers.

4. Display the configurations in a list on the public user interface.
One of the things we wanted to do with the service was display a list of
plugins, so if this one replaces several plugins, it needs to be able to
"talk" about what publishers it supports and so on.

##Technical design
[See the generic string matcher tech design doc.](generic_string_matcher_tech_design.md)
