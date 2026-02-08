import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edrrealtime import EDRRealtimeUpdates, RemoteThread, EDRSEEReader # EDR_INTERNAL

class TestEDRRealtimeUpdates(unittest.TestCase):
    def setUp(self):
        self.mock_callback = MagicMock()
        
        # Patch globally for the test class scope to catch _reset() re-instantiations
        self.remote_patch = patch('edrrealtime.RemoteThread')
        self.reader_patch = patch('edrrealtime.EDRSEEReader')
        
        self.mock_remote_class = self.remote_patch.start()
        self.mock_reader_class = self.reader_patch.start()
        
        self.realtime = EDRRealtimeUpdates(self.mock_callback, "test_kind", "http://endpoint", lambda: "auth")

    def tearDown(self):
        self.reader_patch.stop()
        self.remote_patch.stop()

    def test_init(self):
        self.mock_remote_class.assert_called()
        self.mock_reader_class.assert_called()

    def test_start_calls_thread_start(self):
        # The mock instance created during init
        mock_instance = self.mock_remote_class.return_value
        mock_instance.is_alive.return_value = False
        
        self.realtime.start()
        # start calls _reset which calls RemoteThread() again
        # So we should check if the NEW instance had start called, OR check if the class was called.
        
        # When _reset is called, RemoteThread(...) is called.
        # This returns self.mock_remote_class.return_value (the same mock) by default behavior of return_value,
        # unless side_effect is set.
        # So self.realtime.remote_thread should be the same mock object (or a new one if return_value generates new ones? No, usually same).
        
        # Actually checking that start() was called on the return value.
        self.mock_remote_class.return_value.start.assert_called()

    def test_shutdown(self):
        self.realtime.shutdown()
        # EDRSEEReader mock
        self.realtime.disp.close.assert_called()
        # RemoteThread mock
        self.realtime.remote_thread.close.assert_called()
        self.realtime.remote_thread.join.assert_called()

class TestRemoteThread(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.authenticator = lambda: "secret"
        # We want to test logic, so we shouldn't patch RemoteThread itself here, 
        # but we need to prevent network calls.
        self.thread = RemoteThread(self.queue, "http://endpoint", self.authenticator)

    @patch('edrrealtime.ClosableSSEClient')
    def test_run_processes_messages(self, MockSSE):
        # Setup mock SSE stream
        msg1 = MagicMock()
        msg1.event = "put"
        msg1.data = '{"data": "stuff"}'
        
        msg2 = MagicMock()
        msg2.event = "cancel" # Should trigger break
        msg2.data = ""

        mock_client = MockSSE.return_value
        # The code iterates over 'self.sse' which is the client.
        mock_client.__iter__.return_value = iter([msg1, msg2])
        
        self.thread.run()
        
        # Verify messages in queue
        self.assertEqual(self.queue.qsize(), 2)
        item1 = self.queue.get()
        self.assertEqual(item1.event, "put")
        item2 = self.queue.get()
        self.assertEqual(item2.event, "cancel")

class TestEDRSEEReader(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.callback = MagicMock()
        # Prevent thread start in init
        with patch('edrrealtime.EDRSEEReader.setup_see_thread') as mock_setup:
            self.reader = EDRSEEReader(self.queue, self.callback, "test_kind")
            self.mock_setup = mock_setup

    def test_thread_logic_put(self):
        # Manually instantiate the inner thread class to test its logic
        see_thread = EDRSEEReader.EDRSEEThread(self.queue, self.callback, "test_kind")
        
        # Add messages
        msg_put = MagicMock()
        msg_put.event = "put"
        msg_put.data = '{"path": "/foo", "data": "bar"}'
        self.queue.put(msg_put)
        
        self.queue.put(False) # Stop signal
        
        see_thread.run()
        
        self.callback.assert_called_with("test_kind", "bar")

    def test_thread_logic_initial_update(self):
        see_thread = EDRSEEReader.EDRSEEThread(self.queue, self.callback, "test_kind")
        
        msg_init = MagicMock()
        msg_init.event = "put"
        msg_init.data = '{"path": "/", "data": {"a": 1, "b": 2}}'
        self.queue.put(msg_init)
        self.queue.put(False)
        
        see_thread.run()
        
        # Sorted keys logic means a then b
        calls = [unittest.mock.call("test_kind", 1), unittest.mock.call("test_kind", 2)]
        self.callback.assert_has_calls(calls)

if __name__ == '__main__':
    unittest.main()
