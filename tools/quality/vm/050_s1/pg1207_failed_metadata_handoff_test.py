import ast
import hashlib
import json
import pathlib
import tempfile
import unittest
from pg1207_failed_metadata_handoff import payload


class MetadataRecoveryTest(unittest.TestCase):
    def test_actual_generated_binary_writer_exclusive_and_rechecks(self):
        s=payload();t=ast.parse(s)
        node=next(n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='WRITER_SOURCE'for x in n.targets))
        env={};exec(ast.literal_eval(node.value),env)
        with tempfile.TemporaryDirectory(prefix='pg1207-durable-json-')as tmp:
            root=pathlib.Path(tmp);literal=b'{"result":0,"rawExported":false}'
            env['save'](root,'after.private.json',literal)
            self.assertEqual((root/'after.private.json').read_bytes(),literal)
            self.assertEqual(json.loads((root/'after.private.json').read_bytes()),{'result':0,'rawExported':False})
            self.assertEqual((root/'after.private.json').stat().st_mode&0o777,0o600)
            for value in [None,'{"result":0}',{},True]:
                with self.assertRaises(ValueError):env['save'](root,'bad.private.json',value)
            with self.assertRaises(FileExistsError):env['save'](root,'after.private.json',literal)
        self.assertFalse('json.dump(' in s)
        self.assertTrue("not pathlib.Path('/proc/553547').exists()" in s)
        self.assertTrue('signals==1' in s)
        self.assertEqual(hashlib.sha256(b'python3\x00-B\x00-\x00').hexdigest(),'5a5cff3ba9f3379bceb96da8fda3ef4a6ab51547f4b5cd0c1d9305e99b4c2ad0')


if __name__=='__main__':unittest.main()
