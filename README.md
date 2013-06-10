#OpenArticleGauge

OpenArticleGauge (OAG) is a service for determining the licence status of journal publications, providing an end-user interface for looking up lists of identifiers, and an API for inclusion into third-party software systems.

##Installation

###Redis

You need to install [Redis](http://redis.io), and start it as per the Redis documentation

###Elasticsearch

You need to install [Elasticsearch](http://www.elasticsearch.org/), and start it as per the documentation

###OpenArticleGauge Application

Configure the application, if necessary:

    openarticlegauge/config.py
    openarticlegauge/celeryconfig.py

####Non-Python requirements

OpenArticleGauge requires lxml, a Python library which is written in C.
You need to install lxml's dependencies.  Just make sure you install
libxml2 development and header files and libxslt development and header
files using your Linux distribution's package manager.

If you are on Windows, try http://lxml.de/installation.html#ms-windows .

Here is an example on a Debian-based system:

    sudo apt-get update
    sudo apt-get install libxml2-dev libxslt-dev

####Installing the application

Then install the project requirements using pip (recommended to also use a virtualenv):

    pip install -e .
    
or with setuptools:

    python setup.py install

###Celery

Start the celery backend

    sh bin/start_celery_in_cmdline.sh

or start the daemon with

    sh bin/start_celery_daemon.sh
    
if you start the daemon, you can stop it with

    sh bin/stop_celery_daemon.sh

**Note**: you may want to modify the shell scripts with paths to the log files you want it to use

###Web Application

Start the web application with:

    python openarticlegauge/app.py

**Note**: You may not get any feedback on the standard output. Check
oag.log at the root of the repository (where this readme is).

##Invalidating Licences

You may wish to remove from the archive particular licence statements associated with identifiers.  For example, if a plugin has been added or updated which changes the way that licences for a given provider are detected, you may wish to remove any previous licence statements applied by that plugin, or only particular licence statements (such as those where a licence was not detected).  To do this, use the invalidate.py script.

    python invalidate.py --help

Some commonly useful options would be

###Remove all unknown licenses:

    python invalidate.py -a -u

###Remove all unknown licenses from a specific handler

    python invalidate.py -h handler_name -v handler_version -u

###Remove all licenses of a specific type from a specific handler

    python invalidate.py -h handler_name -v handler_version -t license_type
    

