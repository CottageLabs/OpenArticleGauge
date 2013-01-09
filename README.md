#IsItOpenAccess

IsItOpenAccess is a service for determining the licence status of journal publicatios, providing an end-user interface for looking up lists of identifiers, and an API for inclusion into third-party software systems.

##Installation

Install a suitable backend for [Celery](http://celeryproject.org) such as [RabbitMQ](http://www.rabbitmq.com/) or [Redis](http://redis.io)

    sudo apt-get install rabbitmq-server

Install the project requirements using pip (recommended to also use a virtualenv):

    pip install -r requirements.txt

Configure the queue backend for celery (access permissions, etc)

> [Celery instructions for RabbitMQ](http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#setting-up-rabbitmq)

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
      . slavedriver.webfetch.plos_lookup
      (... etc)


