from lxml import etree
import StringIO
import unittest

from clic.clicdb import ClicDb
from clic.text import text
from clic.errors import UserError

class TestText(unittest.TestCase):
    def test_fetch_by_book(self):
        """
        Fetch by book
        """
        cdb = ClicDb()
        out = [x for x in text(cdb, corpora=['AgnesG'])][1:]

        self.assertEqual(out[0][0], 'AgnesG')
        self.assertEqual(out[0][1], 1)

        # non-word markup was stripped, others not
        self.assertIn("""<qs eid="169" offset="15011" wordOffset="2745"/>,-- \'<w o="77">Yes</w>, <w o="82">I</w> <w o="84">will</w>, <w o="90">Mary</w> <w o="95">Ann</w>,""", out[2][2])

        # Fetch some details, proving we've parsed something useful
        tree = etree.parse(StringIO.StringIO(out[2][2]))
        self.assertEqual(tree.xpath('/div')[0].get('book'), 'AgnesG')
        self.assertEqual(tree.xpath('/div')[0].get('num'), '3')