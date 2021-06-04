import unittest

from src import REST


class TestKeywords(unittest.TestCase):
    def setUp(self) -> None:
        self.library = REST.REST()
        return super().setUp()

    def test_set_ssl_verify(self):
        self.assertTrue(self.library.request["sslVerify"])
        self.library.set_ssl_verify(False)
        self.assertFalse(self.library.request["sslVerify"])

    def test_set_log_level(self):
        self.assertEqual(self.library.log_level, "WARN")
        self.library.set_log_level("INFO")
        self.assertEqual(self.library.log_level, "INFO")
        self.library.set_log_level("NOT ACCEPTABLE")
        self.assertEqual(self.library.log_level, "WARN")
