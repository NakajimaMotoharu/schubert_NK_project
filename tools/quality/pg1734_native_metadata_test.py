"""YKT926 actual generated guard/preflight definitions, independent stat vectors."""
import ast
import inspect
import stat
from types import SimpleNamespace
import unittest
from pg1734_bootstrap_native_catalog import main as catalog_main
from pg1719_current_bootstrap_sources import PREFLIGHT

FIELDS=['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']

class MetadataTest(unittest.TestCase):
    def test_native_exact_emitted_metadata_definition(self):
        node=next(n for n in ast.walk(ast.parse(inspect.getsource(catalog_main)))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='new'for t in n.targets))
        ns={};exec(ast.literal_eval(node.value).split('\nraw=')[0],ns);measure=ns['metadata9']
        before={k:i+1 for i,k in enumerate(FIELDS)};before['st_atime_ns']=10
        self.assertEqual(measure(SimpleNamespace(**before)),tuple(range(1,10)))
        self.assertEqual(measure(SimpleNamespace(**before)),measure(SimpleNamespace(**{**before,'st_atime_ns':11})))
        for k in FIELDS:
            with self.subTest(field=k):self.assertNotEqual(measure(SimpleNamespace(**before)),measure(SimpleNamespace(**{**before,k:before[k]+1})))
    def test_future_preflight_readonly_atime_and_nine_rejections(self):
        defs=[n for n in ast.parse(PREFLIGHT).body if isinstance(n,ast.FunctionDef)and n.name in ('metadata9','read','require')]
        self.assertEqual(len(defs),3)
        ns={'stat':stat,'os':SimpleNamespace(listxattr=lambda p:[])}
        exec(compile(ast.Module(body=defs,type_ignores=[]),'<actual future ABI preflight read>','exec'),ns)
        before={'st_dev':28,'st_ino':33,'st_uid':0,'st_gid':0,'st_mode':stat.S_IFREG|0o400,'st_nlink':1,'st_size':4,'st_mtime_ns':100,'st_ctime_ns':100,'st_atime_ns':99}
        class File:
            def __init__(self,after):self.after=after;self.count=0
            def lstat(self):self.count+=1;return SimpleNamespace(**(before if self.count==1 else self.after))
            def read_bytes(self):return b'wire'
        self.assertEqual(ns['read'](File({**before,'st_atime_ns':101})),b'wire')
        for k in FIELDS:
            with self.subTest(field=k),self.assertRaises(ValueError):ns['read'](File({**before,k:before[k]+1}))

if __name__=='__main__':unittest.main()
