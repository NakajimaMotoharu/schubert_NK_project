"""Actual generated archive primitive/strict schemas/real bytes independent vectors."""
import ast
import hashlib
import unittest
from pg1616_current_ordinary_native_catalog_v2 import catalog_source
from pg1617_current_ordinary_native_qualification_v2 import source

class ArchiveSchemaTest(unittest.TestCase):
    def test_generated_primitive_actual_bytes_and_every_key(self):
        raw=catalog_source();tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='archive_record')
        import re
        env={'hashlib':hashlib,'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual archive-byte guard>','exec'),env)
        body=b'independent native archive fixture';value={'bytes':34,'sha256':hashlib.sha256(body).hexdigest()}
        self.assertEqual(len(body),34);env['archive_record'](value,body)
        for bad in [None,{},dict(value,extra=1),{'size':34,'sha256':value['sha256']},dict(value,bytes=None),dict(value,bytes=True),dict(value,bytes=0),dict(value,bytes=16777217),dict(value,sha256='raw'),dict(value,sha256='a'*64)]:
            with self.assertRaises(ValueError):env['archive_record'](bad,body)
        for data in [None,'not-bytes',body+b'x',b'x'*34]:
            with self.assertRaises(ValueError):env['archive_record'](value,data)
        self.assertNotIn("v['size']",raw);self.assertIn("archive_record(v,p.read_bytes())",raw)
        self.assertIn('pg1616-current-ordinary-native-catalog-v2',source());self.assertIn('PG1617',source())

if __name__=='__main__':unittest.main()
