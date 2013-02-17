#IsItOpenAccess

IsItOpenAccess is a service for determining the licence status of journal publicatios, providing an end-user interface for looking up lists of identifiers, and an API for inclusion into third-party software systems.

##Installation

Install [Redis](http://redis.io)

Install the project requirements using pip (recommended to also use a virtualenv):

    pip install -e .
    
or with setuptools:

    python setup.py install

Configure the queue backend for celery (access permissions, etc)

Check that you can start the celery backend (in IsItOpenAccess/src):

    sh start_celery_in_cmdline.sh

You should see something like this:

     -------------- celery@TheBebop v3.0.13 (Chiastic Slide)
    ---- **** ----- 
    --- * ***  * -- [Configuration]
    -- * - **** --- . broker:      amqp://guest@localhost:5672//
    - ** ---------- . app:         __main__:0x2d3c5d0
    - ** ---------- . concurrency: 8 (processes)
    - ** ---------- . events:      OFF (enable -E to monitor this worker)
    - ** ---------- 
    - *** --- * --- [Queues]
    -- ******* ---- . celery:      exchange:celery(direct) binding:celery
    --- ***** ----- 
    
    [Tasks]
        . workflow.detect_provider
        . workflow.provider_licence
        . workflow.store_results

      (... etc)

(NB Ctrl-C will shut the celery instance down.)

You should be able to start up the web API at this point by running 'python app.py'

