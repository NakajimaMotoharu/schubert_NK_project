"""New current source and actual generation reader, previous good/failed runs rejected."""
import unittest
from pyflakes.api import check,checkPath
import pg4738_new_normal_live_binding as binding


class Binding(unittest.TestCase):
    def test_new_source_release_and_previous_cohorts_never_selected(self):
        raw=binding.body()
        self.assertEqual(0,check('SOURCE="x"\nDIGEST="x"\nEXPECTED={}\n'+raw,'<new actual live>'))
        self.assertIn('PG4702',raw);self.assertNotIn('PG3976',raw)
        for value in ['3c71efc3-5bc0-4e31-8477-96e229a60806','e0c44d1b-a451-4ad7-b602-b04215d3e0eb','9a28ccb26bff42a4900dae95ade7a471']:
            self.assertIn("!='"+value+"'",raw)
        self.assertNotIn('systemctl\',\'start',raw)
        for path in [binding.__file__,__file__]:self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
