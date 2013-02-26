#IsItOpenAccess

IsItOpenAccess is a service for determining the licence status of journal publications, providing an end-user interface for looking up lists of identifiers, and an API for inclusion into third-party software systems.

##Installation

###Redis

You need to install [Redis](http://redis.io), and start it as per the Redis documentation

###Elasticsearch

You need to install [Elasticsearch](http://www.elasticsearch.org/), and start it as per the documentation

###IsItOpenAccess Application

Configure the application, if necessary:

    isitopenaccess/config.py
    isitopenaccess/celeryconfig.py

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

**Note** you may want to modify the shell scripts with paths to the log files you want it to use

###Web Application

Start the web application with:

    python isitopenaccess/app.py

