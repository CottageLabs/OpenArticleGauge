import socket
import time
import sys
import subprocess
from openarticlegauge.tests.support.test_app import app

def get_first_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))  # let OS pick the first available port
    free_port = sock.getsockname()[1]  # which port did the OS pick?
    sock.close()
    return free_port


class LiveServer(object):
    def __init__(self, port):
        self.app = app
        self.port = port
        self._process = None

    def get_server_url(self):
        """
        Return the url of the test server
        """
        return 'http://localhost:{0}'.format(self.port)

    def spawn_live_server(self):
        # sys.executable is the full, absolute path to the current Python interpreter
        # This is used so that the new process with the test app in it runs properly in a virtualenv.
        self._process = subprocess.Popen([sys.executable, 'support/test_app.py', '--port', str(self.port), '--no-logging'])

        # we must wait for the server to start listening
        time.sleep(1)

    def terminate_live_server(self):
        if self._process:
            self._process.terminate()
