from flask import Flask, Response
from time import sleep
import sys
import argparse
import logging
app = Flask(__name__)

@app.route('/stream/normal')
def stream_normal():
    def generate():
        for char in 'H' * 2:
            yield char

    return Response(generate())

@app.route('/stream/timeout')
def stream_timeout():
    def generate():
        for char in 'H' * 2:
            yield char
            sleep(5)

    return Response(generate())

@app.route('/stream/long_timeout')
def stream_long_timeout():
    def generate():
        for char in 'H' * 2:
            yield char
            sleep(31)

    return Response(generate())

@app.route('/timeout')
def static_timeout():
    sleep(5)
    return "okay"

@app.route('/long_timeout')
def static_long_timeout():
    #Requests timeout after 30 seconds, this ensures retries
    sleep(31)
    return "okay"

@app.route('/normal')
def static_normal():
    return "okay"

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int)
    parser.add_argument('--no-logging', dest='logging', action='store_false')
    parser.set_defaults(logging=True)
    return parser.parse_args(args)


if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])  # the path to this file would've been the 1st arg to the interpreter
    if not opts.port:
        print "Please specify port with --port"
        sys.exit(1)
    if not opts.logging:
        logger = logging.getLogger('werkzeug')
        logger.setLevel(logging.ERROR)
    app.run(port=opts.port)

