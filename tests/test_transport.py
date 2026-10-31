import unittest
from pathlib import Path
from unittest.mock import Mock

from photocraft_ai.bridge import ControlClient, ControlError


class TransportTests(unittest.TestCase):
    def test_copy_is_not_replayed_after_lost_acknowledgement(self):
        client = ControlClient(12345, Path('unused'))
        client._sock = Mock()
        client._last = float('inf')
        client._exchange = Mock(side_effect=ConnectionError('lost acknowledgement'))
        client.close = Mock()
        with self.assertRaises(ControlError):
            client.run('layer.copyToDocument', document=0, source=1, layers=[1])
        self.assertEqual(client._exchange.call_count, 1)

    def test_inspection_can_retry(self):
        client = ControlClient(12345, Path('unused'))
        client._sock = Mock()
        client._last = float('inf')
        client._exchange = Mock(side_effect=[ConnectionError('closed'), {'ok': True, 'result': {'width': 10}}])
        client.close = Mock()
        self.assertEqual(client.run('document.inspect'), {'width': 10})
        self.assertEqual(client._exchange.call_count, 2)


if __name__ == '__main__':
    unittest.main()
