
import unittest
from unittest.mock import MagicMock, patch
from edr.utils.sseclient import SSEClient, Event

class TestSSEClient(unittest.TestCase):
    @patch('edr.utils.sseclient.requests.get')
    def test_connect_and_iter(self, mock_get):
        mock_resp = MagicMock()
        # Simulate a stream of data
        mock_resp.iter_content.return_value = iter([
            b"data: message 1\n\n",
            b"id: 2\nevent: update\ndata: message 2\n\n"
        ])
        mock_resp.raise_for_status.return_value = None
        mock_resp.encoding = 'utf-8' # Important for decoding
        mock_get.return_value = mock_resp

        client = SSEClient("http://example.com/stream", retry=0)
        
        # Manually call next() to avoid infinite retry loop in __next__
        # The list() constructor would loop until StopIteration, but SSEClient catches it and retries.
        
        event1 = next(client)
        self.assertEqual(event1.data, "message 1")
        
        event2 = next(client)
        self.assertEqual(event2.id, "2")
        self.assertEqual(event2.event, "update")
        self.assertEqual(event2.data, "message 2")

    def test_event_parsing(self):
        raw = "id: 123\nevent: test\nretry: 1000\ndata: payload\n"
        event = Event.parse(raw)
        self.assertEqual(event.id, "123")
        self.assertEqual(event.event, "test")
        self.assertEqual(event.retry, 1000)
        self.assertEqual(event.data, "payload")

    def test_event_dump(self):
        event = Event(data="payload", id="123", event="test", retry=1000)
        dumped = event.dump()
        self.assertIn("id: 123", dumped)
        self.assertIn("event: test", dumped)
        self.assertIn("retry: 1000", dumped)
        self.assertIn("data: payload", dumped)

if __name__ == '__main__':
    unittest.main()
