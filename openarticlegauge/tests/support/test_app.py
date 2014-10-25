from flask import Flask, Response
from time import sleep
app = Flask(__name__)

@app.route('/')
def hello_world():
    def generate():
        for char in 'H' * 2:
            yield char
            sleep(65)

    return Response(generate())

if __name__ == '__main__':
    app.run()
