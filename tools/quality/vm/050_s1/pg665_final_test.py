"""BOOT665001 exact post closure, immutable current pins and fresh readonly resources."""
import ast
import unittest
from pg665_final import source


class Test(unittest.TestCase):
    def test_binding_and_complete_scope(self):
        raw=source();ast.parse(raw)
        for value in ('8767e53ccfc2ea3f434689674dad7395feaef31cec48d53a92bc6fd7eed81c08','fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98',
                      '65bfe1da3b9e454997f1d899fea9510e',"'2142585'","'11164505'","'119175'",'0.1.0-PG631',
                      "len(initial)==20","all(b[key]==initial[key]for key in b)",'manager.RefUnit(u)','manager.UnrefUnit(u)',
                      'extra();snapshot();extra();snapshot()',"'newMetadataScopesNormal':True","'formalAccepted':False"):
            self.assertIn(value,raw)
        for value in('0.1.0-PG548','969d8ded','c0592572','907340','signal.pidfd','daemon-reload','reset-failed'):
            self.assertNotIn(value,raw)
        self.assertIn("not p.name.endswith('.retired.private')",raw)


if __name__=='__main__':unittest.main()
