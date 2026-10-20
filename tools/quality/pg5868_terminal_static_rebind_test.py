import unittest
import pg5868_terminal_static_rebind as target


class Conservative474RebindTest(unittest.TestCase):
    def test_changed_receivers_never_imported(self):
        raw=target.reader_source()
        self.assertIn('len(used)!=474 or len(held)!=8',raw)
        self.assertIn("currentWholeCaseRefs=[]",raw)
        self.assertIn("historicalPtImportedAsCurrent=False",raw)
        self.assertIn("current!=before",__import__('inspect').getsource(target.previous.previous.bind_one))
        self.assertNotIn('PG5848-protocol-expression-static-v1',raw)


if __name__=='__main__':unittest.main()
