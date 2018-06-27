import unittest
from couchreq import couchreq

class CReqTestCase(unittest.TestCase):

    def setUp(self):
        self.creq = couchreq.Couchreq()

    def tearDown(self):
        pass


    def testEmptyCreateDb(self):
        self.assertFalse(self.creq.create_db(None),'create_db without dbname')

if __name__ == '__main__':
    unittest.main()
