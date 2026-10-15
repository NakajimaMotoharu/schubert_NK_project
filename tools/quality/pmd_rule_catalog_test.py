"""Literal primary-vendor alias fixtures, no blanket applicability decisions."""
import unittest
from pmd_rule_catalog import definitions


class Catalog(unittest.TestCase):
    def test_single_canonical_definition_and_explicit_alias_resolve(self):
        resources={'a.xml':b'<ruleset><rule name="R" ref="b.xml/R" deprecated="true"/></ruleset>','b.xml':b'<ruleset><rule name="R" class="fixture.Real"><description>Independent primary contract.</description><priority>3</priority></rule></ruleset>'}
        actual,aliases=definitions(resources,{'R'});self.assertEqual('b.xml/R',actual['R']['canonical']);self.assertEqual('fixture.Real',actual['R']['attributes']['class']);self.assertEqual([{'alias':'a.xml/R','target':'b.xml/R','canonical':'b.xml/R'}],aliases)

    def test_unknown_cyclic_multiple_or_non_deprecated_alias_refused(self):
        bad=[{'a.xml':b'<ruleset><rule name="R" ref="missing.xml/R" deprecated="true"/></ruleset>'},
             {'a.xml':b'<ruleset><rule name="R" ref="a.xml/R" deprecated="true"/></ruleset>'},
             {'a.xml':b'<ruleset><rule name="R" class="fixture.A"/></ruleset>','b.xml':b'<ruleset><rule name="R" class="fixture.B"/></ruleset>'},
             {'a.xml':b'<ruleset><rule name="R" ref="b.xml/R"/></ruleset>','b.xml':b'<ruleset><rule name="R" class="fixture.B"/></ruleset>'},{}]
        for resources in bad:
            with self.assertRaises(ValueError):definitions(resources,{'R'})


if __name__=='__main__':unittest.main()
