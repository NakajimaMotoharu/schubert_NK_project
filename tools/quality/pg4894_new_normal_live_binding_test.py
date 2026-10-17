import unittest
import inspect
from pyflakes.api import check,checkPath
import pg4894_new_normal_live_binding as role


class Binding(unittest.TestCase):
    def test_actual_source_new_once_and_historical_negative_uuid_not_authority(self):
        raw=role.body();self.assertEqual(0,check('SOURCE="x"\nDIGEST="x"\nEXPECTED={}\n'+raw,'<actual fresh binding>'))
        self.assertEqual(role.entry.SLOT,role.ONCE);self.assertNotIn('pg4736-new-normal-root-once-v1',raw)
        self.assertIn("'ONCE':ONCE",inspect.getsource(role.main))
        self.assertIn('0.1.0-PG4860',raw)
        self.assertIn('fff841d9-2554-4680-b17d-9548bfa79cbb',raw);self.assertIn('7ab6c953-b2fc-47ae-be96-26a3196ca76d',raw)
        self.assertIn("unit['InvocationID']!='b414b0e1e5ac47e8b5fb8c5ae3d94348'",raw)
        self.assertEqual(role.entry.SOURCE,role.SOURCE)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
