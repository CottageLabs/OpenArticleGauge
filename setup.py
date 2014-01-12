from setuptools import setup, find_packages

setup(
    name = 'openarticlegauge',
    version = '0.0.1',
    packages = find_packages(),
    install_requires = [
        "Flask==0.9",
        "Jinja2==2.6",
        "Werkzeug==0.8.3",
        "amqp==1.0.6",
        "anyjson==0.3.3",
        "argparse==1.2.1",
        "billiard==2.7.3.19",
        "celery==3.0.13",
        "kombu==2.5.4",
        "python-dateutil==1.5",
        "wsgiref==0.1.2",
        "Flask-Login==0.1.3",
        "Flask-WTF==0.8.3",
        "requests==1.1.0",
        "redis",
        "lxml",
        "beautifulsoup4",
        "nose==1.3.0"
		]
)

