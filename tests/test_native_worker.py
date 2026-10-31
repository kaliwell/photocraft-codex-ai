import json
from http.server import ThreadingHTTPServer
import threading
import unittest
from unittest.mock import Mock
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from photocraft_ai.native import NativeWorker, handler


class NativeHttpTests(unittest.TestCase):
    def setUp(self):
        self.worker = NativeWorker(None)
        self.token = 'a' * 64
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler(self.worker, self.token))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path, data=None, authorized=True, origin=None):
        headers = {}
        if authorized:
            headers['Authorization'] = 'Bearer ' + self.token
        if origin:
            headers['Origin'] = origin
        request = Request(self.base + path, data=None if data is None else json.dumps(data).encode(), headers=headers)
        return urlopen(request, timeout=3)

    def test_authentication_is_required_before_any_job_starts(self):
        self.worker.submit = Mock()
        with self.assertRaises(HTTPError) as error:
            self.request('/generate', {'mode': 'remove'}, authorized=False)
        self.assertEqual(error.exception.code, 401)
        self.worker.submit.assert_not_called()

    def test_browser_origin_is_rejected_even_with_token(self):
        with self.assertRaises(HTTPError) as error:
            self.request('/generate', {'mode': 'remove'}, origin='https://example.com')
        self.assertEqual(error.exception.code, 403)
        self.assertFalse(self.worker.snapshot()['busy'])

    def test_bad_mode_cannot_start_generation(self):
        with self.assertRaises(HTTPError) as error:
            self.request('/generate', {'mode': 'arbitrary-command', 'prompt': 'test'})
        self.assertEqual(error.exception.code, 400)
        self.assertFalse(self.worker.snapshot()['busy'])

    def test_cancel_signals_active_worker(self):
        with self.request('/cancel', {}) as response:
            self.assertEqual(response.status, 202)
        self.assertTrue(self.worker.cancel.is_set())

    def test_state_endpoint_reports_service_errors(self):
        self.worker.update(error=True, message='document changed', busy=False)
        with self.request('/state') as response:
            data = json.load(response)
        self.assertTrue(data['error'])
        self.assertEqual(data['message'], 'document changed')


class NativeModeTests(unittest.TestCase):
    def test_generate_keeps_selection_edges_while_edits_feather(self):
        for mode, radius in [('generate', 0), ('fill', 12), ('remove', 12)]:
            with self.subTest(mode=mode):
                service = Mock()
                service.lock = threading.Lock()
                target = Mock(index=0)
                target.name = 'test'
                service.bridge.active_image.return_value = target
                service.bridge._revision.return_value = 7
                worker = NativeWorker(service)
                worker._run({'mode': mode, 'prompt': 'a cup',
                             'document': {'index': 0, 'name': 'test', 'revision': 7}})
                self.assertFalse(worker.snapshot()['error'], worker.snapshot())
                self.assertEqual(service.prepare.call_args.kwargs['feather_px'], radius)
                service.apply.assert_called_once()


if __name__ == '__main__':
    unittest.main()
