import ast
import unittest
import pg3778_hygiene_unused_held_post as p


class Held(unittest.TestCase):
    def test_full_fields_preserved_and_success_output_after_refs_closed(self):
        raw=p.payload();tree=ast.parse(raw);self.assertIsInstance(tree.body[-2],ast.Try);self.assertIsInstance(tree.body[-1],ast.Expr)
        for s in ["for unit in expected['units']",'manager.LoadUnit(unit)','manager.RefUnit(unit)','manager.UnrefUnit(unit)','bus.close()','cfg==oldcfg','all24TablesEqualTwice','native34Preserved','candidate187SignatureVerified','newTenReferencesReturnedNormally']:self.assertIn(s,raw)
        for s in ['start-unit','stop-unit','daemon-reload','poweroff','pg_restore']:self.assertNotIn(s,raw)


if __name__=='__main__':unittest.main()
