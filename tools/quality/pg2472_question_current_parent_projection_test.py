import ast
import hashlib
import json
import unittest
from unittest.mock import Mock
from pyflakes.api import check
import pg2472_question_current_parent_projection as projection
import pg2457_question_current_parent_projection as historical
import pg2458_question_current_owned_sources as owned
import pg2460_question_current_owned_dispatch as dispatch
import pg2464_question_current_owned_post as stopped
import pg2466_question_current_native_catalog as catalog
import pg2468_question_current_native_qualification as qualification
import pg2470_question_current_a01 as a01


class SourceBinding(unittest.TestCase):
    def test_actual_whole_reader_source_bom_hash_schema_negatives(self):
        fields={key:'fixed'for key in projection.ROOT_FIELDS}
        fields['Id']='schubert-nk-morning-controller.service'
        value={'source':projection.SOURCE,'manifestSha256':projection.BOM,
               'units':{'schubert-nk-morning-controller.service':fields}}
        raw=json.dumps(value,sort_keys=True).encode();digest=hashlib.sha256(raw).hexdigest()
        script=projection.payload(digest)
        nodes=[n for n in ast.parse(script).body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        code=compile(ast.Module(body=nodes,type_ignores=[]),'<actual projection pure IO fixture>','exec')
        def run(content):
            obj=Mock(read_bytes=lambda:content)
            ns={'hashlib':hashlib,'json':json,'pathlib':Mock(Path=lambda p:obj),'print':lambda *a:None}
            exec(code,ns);return ns
        self.assertEqual(fields,run(raw)['fields'])
        with self.assertRaises(AssertionError):run(b'foreign')
        for field,bad in [('source','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'),('source',None),
                          ('manifestSha256','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c'),('manifestSha256',None)]:
            changed={**value,field:bad};blob=json.dumps(changed,sort_keys=True).encode()
            new=projection.payload(hashlib.sha256(blob).hexdigest())
            # Trust the digest as a fixture input; independently mutate exactly
            # Source/BOM to prove the tuple guard, not merely the hash guard.
            self.assertIn('before[\'manifestSha256\']==BOM',new)
            env={'hashlib':hashlib,'json':json,'pathlib':Mock(Path=lambda p:Mock(read_bytes=lambda:blob)),'print':lambda *a:None}
            negative=[n for n in ast.parse(new).body if not isinstance(n,(ast.Import,ast.ImportFrom))]
            with self.assertRaises(AssertionError):exec(compile(ast.Module(body=negative,type_ignores=[]),'<negative source/BOM fixture>','exec'),env)
        self.assertIn("SOURCE='3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'",historical.payload('a'*64))
        self.assertEqual(0,check(script,'<whole current projection>'))
        for broken in [{**fields,'Id':'foreign'},{**fields,'Job':None},{**fields,'foreign':'fixed'},
                       {k:v for k,v in fields.items()if k!='MainPID'},
                       {**{k:v for k,v in fields.items()if k!='MainPID'},'foreign':'fixed'}]:
            changed={**value,'units':{'schubert-nk-morning-controller.service':broken}}
            blob=json.dumps(changed,sort_keys=True).encode();new=projection.payload(hashlib.sha256(blob).hexdigest())
            ns={'hashlib':hashlib,'json':json,'pathlib':Mock(Path=lambda p:Mock(read_bytes=lambda:blob)),'print':lambda *a:None}
            nodes=[n for n in ast.parse(new).body if not isinstance(n,(ast.Import,ast.ImportFrom))]
            with self.assertRaises(AssertionError):exec(compile(ast.Module(body=nodes,type_ignores=[]),'<negative shape fixture>','exec'),ns)

    def test_all_current_consumer_binding_roles_nonmatching_old_history_is_not_rewritten(self):
        self.assertIn('pg2472-question-current-parent-projection-v1.safe.json',__import__('inspect').getsource(owned.sources))
        self.assertNotIn('pg2457-question-current-parent-projection-v1.safe.json',__import__('inspect').getsource(owned.sources))
        self.assertTrue(callable(projection.main))
        for raw in [dispatch.STAGE,qualification.server(),a01.code()]:
            self.assertTrue(projection.SOURCE in raw)
            self.assertTrue('3d69f5af'not in raw)
        self.assertTrue(callable(stopped.emit));self.assertTrue(callable(catalog.catalog_source))
        self.assertEqual(projection.SOURCE,qualification.entry().__globals__['SOURCE'])


if __name__=='__main__':unittest.main()
