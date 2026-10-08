"""BOOT666001 independent coverage-session role/generation/window/type vectors."""
import hashlib
import unittest
from pg666_native import session_valid


class Test(unittest.TestCase):
    def test_exact_single_role_invocation_and_window(self):
        m={'lowerMs':1000,'upperMs':2000};v={'sessions':1,'sessionIdSha256':hashlib.sha256(b'BOOTSTRAP-65bfe1da3b9e454997f1d899fea9510e-ordinary').hexdigest(),'startMs':1000,'dumpMs':2000}
        self.assertTrue(session_valid(v,m))
        for key,bad in({'sessions':True,'sessionIdSha256':hashlib.sha256(b'API-65bfe1da3b9e454997f1d899fea9510e-ordinary').hexdigest(),'startMs':999,'dumpMs':2001}).items():
            self.assertFalse(session_valid({**v,key:bad},m),key)
        for key in v:
            x=dict(v);del x[key];self.assertFalse(session_valid(x,m))
        self.assertFalse(session_valid(None,m));self.assertFalse(session_valid({**v,'dumpMs':999},m))


if __name__=='__main__':unittest.main()
