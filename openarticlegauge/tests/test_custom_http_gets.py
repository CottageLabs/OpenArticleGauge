from unittest import TestCase
from openarticlegauge import util
from openarticlegauge.tests.support import helpers

class TestCustomHttp(TestCase):

    def setUp(self):
        self.ls = helpers.LiveServer(port=helpers.get_first_free_port())
        self.ls.spawn_live_server()
        self.app_url = self.ls.get_server_url()

    def tearDown(self):
        self.ls.terminate_live_server()

    def test_01_http_get_normal(self):
        resp = util.http_get(self.app_url + "/normal")
        assert resp
        assert resp.text == "okay"

    def test_02_http_get_timeout(self):
        resp = util.http_get(self.app_url + "/timeout")
        assert resp
        assert resp.text == "okay"

    def test_03_http_get_long_timeout(self):
        resp = util.http_get(self.app_url + "/long_timeout")
        assert not resp

    def test_04_http_stream_get_normal(self):
        r, content, downloaded_bytes = util.http_stream_get(self.app_url + "/stream/normal")
        assert r
        assert downloaded_bytes == 2
        assert content == "HH"

    def test_05_http_stream_get_timeout(self):
        r, content, downloaded_bytes = util.http_stream_get(self.app_url + "/stream/timeout")
        assert r
        assert downloaded_bytes == 2
        assert content == "HH"

    def test_06_http_stream_get_long_timeout(self):
        r, content, downloaded_bytes = util.http_stream_get(self.app_url + "/stream/long_timeout")
        assert r
        assert content is not None
        assert content == "H" #the sleep happens after the first character/byte has been transmitted
        assert downloaded_bytes == 1

