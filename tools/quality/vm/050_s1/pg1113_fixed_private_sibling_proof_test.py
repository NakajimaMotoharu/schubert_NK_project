"""Private byte fixtures with explicitly simulated Root uid/gid; no Root authority."""
import hashlib
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
from pg1113_fixed_private_sibling_proof import NAMES,proof


class Siblings(unittest.TestCase):
    def test_full_closure_byte_mode_and_extra_entry_rejection(self):
        with tempfile.TemporaryDirectory(prefix='pg1113-sibling-fixture-')as tmp:
            root=Path(tmp);expected={}
            for n in NAMES:
                d=root/n;d.mkdir(mode=0o700);expected[n]={}
                if 'observer'in n:
                    p=d/'fixed.py';p.write_bytes(b'independent literal\n');p.chmod(0o400)
                    expected[n]['fixed.py']=hashlib.sha256(b'independent literal\n').hexdigest()
            original=Path.lstat
            def fixture_stat(path,*a,**kw):
                s=original(path,*a,**kw)
                return types.SimpleNamespace(**{k:getattr(s,k)for k in (
                  'st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')},st_uid=0,st_gid=0)
            with patch.object(Path,'lstat',fixture_stat):
                self.assertEqual(expected,proof(root,expected))
                p=root/NAMES[0]/'fixed.py';p.chmod(0o600)
                with self.assertRaises(ValueError):proof(root,expected)
                p.chmod(0o400);p.chmod(0o600);p.write_bytes(b'foreign bytes\n');p.chmod(0o400)
                with self.assertRaises(ValueError):proof(root,expected)
                p.chmod(0o600);p.write_bytes(b'independent literal\n');p.chmod(0o400)
                (root/NAMES[1]/'unknown').touch()
                with self.assertRaises(ValueError):proof(root,expected)
            with self.assertRaises(ValueError):proof(root,expected) # Real host uid is not Root.
    def test_null_missing_and_unknown_proofs_refuse(self):
        for root,expected in ((None,{}),(Path('/fixture'),None),(Path('/fixture'),{})):
            with self.assertRaises(ValueError):proof(root,expected)


if __name__=='__main__':unittest.main()
