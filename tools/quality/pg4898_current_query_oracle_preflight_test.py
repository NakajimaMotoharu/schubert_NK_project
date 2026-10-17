import unittest
from pyflakes.api import check,checkPath
import pg4898_current_query_oracle_preflight as role


class Applicability(unittest.TestCase):
    def test_current_exact_private_before_only_no_old_namespace_or_key_export(self):
        raw=role.payload();self.assertEqual(0,check(raw,'<actual current applicability>'))
        for marker in (role.current.AFTER,role.current.context(),role.current.BOM,'now+datetime.timedelta(hours=2)',"'rootStartIssued':False","'plaintextLogged':False","'dbOrClockChanged':False"):
            self.assertIn(marker,raw)
        self.assertIn(r"KEY[:]=b'\0'*len(KEY)",raw)
        self.assertNotIn('pg4728-ssc299-publication-independent-post-v1',raw)
        self.assertNotIn('f1f6743f8ebe099a8804623f5efef263fa046ca66c46004ade5d469f755fbd80',raw)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
