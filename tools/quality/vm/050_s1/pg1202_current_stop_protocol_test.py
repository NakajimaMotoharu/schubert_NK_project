"""Run current generated stop control against independent literal fault matrix.

PT-DEP-1202001..003. No VM actions; exact new actual constants are explicitly
transcribed in test vectors, never calculated by production/helper methods.
"""
import ast
import sys
import types
import unittest
from pathlib import Path
from pg1198_current_stop_binding import generate
from pg1198_current_stop_binding_test import fixture
from pg1200_current_stop_preflight import payload
from pg1201_current_stop_dispatch import STAGE, archive_members

R=Path(__file__).resolve().parent


class CurrentProtocolTest(unittest.TestCase):
    def test_actual_generated_stop_control_full_fault_vectors(self):
        generated=generate(fixture())
        for name in ['pg1198_durable','pg1198_native_owned_stop']:
            m=types.ModuleType(name);m.__file__=str(R/(name+'.py'));sys.modules[name]=m
            exec(compile(generated[name+'.py'],m.__file__,'exec'),m.__dict__)
        raw=(R/'pg611_native_owned_stop_test.py').read_text()
        # Independent actual values, not reading EXPECTED/generator mappings.
        for a,b in [('pg611_native_owned_stop','pg1198_native_owned_stop'),
                    ('cc9ed8747f4f450ea1888de1e42c8441','cbca87383b244090b77cbf029677cdd6'),
                    ('1460173','528966'),('fd0cd00933ce43b88634c43faef7a0ef','1037150931c04cb6b64b249c0cf916c3'),
                    ('1454010','526861'),('866af4c303904f1e998a5a50f6ccc716','898429f0e6a64d4fa7a6c07e4473fe8a'),
                    ('1451527','525675'),('4db7f8a4637a4b9f909de4d319677179','bfae0cf915c74f7bbf35a7a1ec4f8cd9'),
                    ('1304653','441175'),('1a7bc5e9a7734bbb9a657bf11fac7dbe','c874395201b94ae7b144e3a6bb2d3b8e'),
                    ('5a1acaa0c35e484c979401e3b6dfb36a','a14cc600a4fd4f2e9d8c4731ad9d754b'),
                    ('86324628081','51232132518'),('86324627857','51232132294'),('88064628082','52972132519'),
                    ('87864','81094'),('87863','81093')]:
            raw=raw.replace(a,b)
        env={'__name__':'independent_current_stop_fault_vectors','__file__':str(R/'pg1202_current_stop_protocol_test.py')}
        exec(compile(raw,'<literal current control vectors>','exec'),env)
        self.assertGreater(env['count'],250)
        h=sys.modules['pg1198_native_owned_stop']
        before=env['b']('schubert-nk-expiry-cleanup.service')
        before.update(MainPID='0',ActiveState='active',SubState='exited',ExecMainCode='1',ExecMainStatus='0',ExecMainExitTimestampMonotonic='200')
        after=dict(before,ActiveState='inactive',SubState='dead')
        self.assertTrue(h.normal_terminal(before,after))
        self.assertFalse(h.normal_terminal(before,dict(after,InvocationID='foreign')))

    def test_current_preflight_closure_and_no_mutations(self):
        raw=payload();ast.parse(raw)
        self.assertTrue('actual==sealed_current' in raw)
        self.assertFalse('SAVE.mkdir(' in raw)
        self.assertFalse('privateProofHashes' in raw)
        self.assertFalse('systemctl\',\'stop' in raw)
        self.assertTrue('manager.UnrefUnit(u)' in raw)

    def test_stage_archive_nested_security_contract(self):
        ast.parse(STAGE)
        env={};node=next(n for n in ast.parse(STAGE).body if isinstance(n,ast.FunctionDef)and n.name=='archive_members')
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual stage archive oracle>','exec'),env)
        f=env['archive_members'];files={'top.class','dev/x.class','payload-sha256.json'}
        good=[('top.class','file'),('dev','dir'),('dev/x.class','file'),('payload-sha256.json','file')]
        f(good,files)
        for bad in [good+good[:1],good[:-1],good+[('extra','dir')],good+[('../outside','file')],good+[('/outside','file')],good+[('link','unsupported')],good+[('dev/./x','file')]]:
            with self.assertRaises(ValueError):f(bad,files)
        self.assertTrue('os.fsync(fd)' in STAGE)


if __name__=='__main__':unittest.main()
