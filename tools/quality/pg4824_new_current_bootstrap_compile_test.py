import ast
import tempfile
import unittest
from pathlib import Path
import pg4824_new_current_bootstrap_compile as role


class NestedGraph(unittest.TestCase):
    def test_actual_compiler_shape(self):
        raw=role.source();ast.parse(raw)
        self.assertIn("(target/name).parent.mkdir(parents=True,exist_ok=True,mode=0o700)",raw)
        self.assertIn("f.relative_to(target).as_posix()",raw)
        self.assertIn("target.rglob('*')",raw)
        self.assertIn('pg4824-frozen-v1.safe.json',raw)
        self.assertNotIn('pg4822-',raw)

    def test_independent_nested_inventory(self):
        with tempfile.TemporaryDirectory()as root:
            p=Path(root);names=['Simple.class','dev/codex/Fixture.class']
            for name in names:
                q=p/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b'fixture')
            self.assertEqual({f.relative_to(p).as_posix()for f in p.rglob('*')if f.is_file()},set(names))
            self.assertEqual({f.relative_to(p).as_posix()for f in p.rglob('*')if f.is_dir()},{'dev','dev/codex'})


if __name__=='__main__':unittest.main()
