import unittest
from unittest.mock import MagicMock
from unittest.mock import Mock
import freezerdb


class TestFreezerDB(unittest.TestCase):

    def setUp(self):
        self.fake_conn = MagicMock()
        self.db = freezerdb.FreezerDB(self.fake_conn)

    def test_initdb(self):
        self.db.init_db()
        self.assertTrue(self.fake_conn.cursor.called)
        c = self.fake_conn.cursor()
        self.assertTrue(c.execute.called_once_with(freezerdb.FreezerDB.ALBUM_CREATE_QUERY))

if __name__ == '__main__':
    unittest.main()
