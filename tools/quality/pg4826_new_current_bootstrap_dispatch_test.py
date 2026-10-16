"""Literal tar and request guards; no SSH/start or source-generated expected values."""
import ast
import hashlib
import inspect
import pathlib
import tarfile
import unittest
import pg4826_new_current_bootstrap_dispatch as role


class ClosedStage(unittest.TestCase):
    def contracts(self):
        nodes=[n for n in ast.parse(role.STAGE).body if isinstance(n,ast.FunctionDef)]
        ns={'pathlib':pathlib};exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<pure tar contracts>','exec'),ns)
        return ns

    def member(self,name,kind=tarfile.REGTYPE):
        value=tarfile.TarInfo(name);value.type=kind;return value

    def test_nested_and_flat_exact(self):
        ns=self.contracts();files={'Flat.class':'a'*64,'dev/codex/Fixture.class':'b'*64}
        names,dirs=ns['inventory'](files)
        self.assertEqual(names,{'Flat.class','dev/codex/Fixture.class','payload-sha256.json'})
        self.assertEqual(dirs,{'dev','dev/codex'})
        items=[self.member(n,tarfile.DIRTYPE)for n in ('.','dev','dev/codex')]+[self.member(n)for n in names]
        ns['members'](items,files)
        for bad in [self.member('/evil'),self.member('../evil'),self.member('Extra.class'),self.member('Flat.class',tarfile.SYMTYPE),self.member('Flat.class',tarfile.LNKTYPE),self.member('dev',tarfile.REGTYPE),items[-1]]:
            with self.assertRaises(ValueError):ns['members'](items+[bad],files)
        with self.assertRaises(ValueError):ns['members'](items[:-1],files)
        for name in ('/x','../x','a/../x','a//x','a/./x','a\\x',''):
            with self.assertRaises(ValueError):ns['inventory']({name:hashlib.sha256(b'x').hexdigest()})

    def test_actual_once_and_five_phase_guards(self):
        raw=inspect.getsource(role.main)
        self.assertLess(raw.index('already reserved'),raw.index('authenticate_host()'))
        self.assertLess(raw.index("'.requested').open('x')"),raw.index("commands.append"))
        self.assertIn("if action=='execute'",raw)
        self.assertIn("actual new verify first",raw)
        self.assertNotIn('reset-failed',raw);self.assertNotIn('systemctl start',raw)
        self.assertIn("len(value['phases'])==5",inspect.getsource(role.fixed))


if __name__=='__main__':unittest.main()
