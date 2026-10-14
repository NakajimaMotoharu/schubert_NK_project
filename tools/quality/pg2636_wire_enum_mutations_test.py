import unittest
from pyflakes.api import check
from pg2636_wire_enum_mutations import SERVER, NAMES, FILES


class SemanticMutations(unittest.TestCase):
    def test_all18_types_and_rejected36_are_separate_from_pt(self):
        self.assertEqual(18,len(set(NAMES)))
        self.assertEqual(20,len(FILES))
        self.assertEqual(0,check('INPUT={}\n'+SERVER,'<whole isolated semantic mutation namespace>'))
        for marker in ['len(vectors)==37','mutationsRejected', 'org.opentest4j.AssertionFailedError',
                       "not list(out.rglob('*.exec'))", "normal['tests']==82"]:
            self.assertIn(marker,SERVER)
        self.assertNotIn('-javaagent',SERVER)


if __name__=='__main__':unittest.main()
