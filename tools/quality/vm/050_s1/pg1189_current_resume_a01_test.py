import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import Mock
from pg1189_current_resume_a01 import code
from pg876_public_artifact_check import check


class ResumeA01Test(unittest.TestCase):
    def test_actual_current_guard_untouched_shared_driver_and_oracle(self):
        s = code();ast.parse(s)
        for part in ['d5b00104280028d9ea81b44c1d1c805f3c2861ed','pg1183-parent-watch-v1.private.jsonl','pg1182-canonical-runtime-post-v1.safe.json','pg1184-canonical-resume-once-v1.safe.json','canonical-resume-once-v1','cbca8738-3b24-4090-b77c-bf029677cdd6','0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',"issued['MainPID']=='430851'",'a14cc600a4fd4f2e9d8c4731ad9d754b','1800000000','NativeNkA01Capture','122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d',"'fullGate':False"]:
            self.assertTrue(part in s, part)
        for old in ['pg957-ordinary-once-v1','pg954-ordinary-before-v1','pg956-parent-watch','40ef6e894573d2ffab1d1732124960f9c98d5f97']:
            self.assertFalse(old in s, old)

    def test_independent_current_schema_dif001_and_secret_negatives(self):
        root = Path(__file__).resolve().parents[4]
        baseline = json.loads((root/'program/characterization/baseline/current/artifacts/CHR-A01.json').read_bytes())
        literal = copy.deepcopy(baseline);literal['title'] = 'schubert NK - ログイン'
        check(literal, baseline)
        for key, value in [('title','wrong'),('csrf','raw'),('passwordValue','raw'),('passwordAutocomplete','foreign'),('unknown','raw')]:
            bad = copy.deepcopy(literal);bad[key] = value
            with self.assertRaises(AssertionError):check(bad, baseline)
        bad = copy.deepcopy(literal);bad['securityHeaders']['set-cookie'] = 'raw'
        with self.assertRaises(AssertionError):check(bad, baseline)

    def test_actual_generated_guard_normal_and_each_runtime_binding_negative(self):
        # Standard SHA-256 abc golden vector is independent of release or tool code.
        sha = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
        self.assertEqual(hashlib.sha256(b'abc').hexdigest(), sha)
        ns = {'__name__': 'data'};exec(code(), ns)
        text = ns['GUARD'].replace('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d', sha)
        parsed = ast.parse(text);nodes = [n for n in parsed.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
        bytecode = compile(ast.Module(body=nodes,type_ignores=[]), '<actual cold GUARD>', 'exec')
        fixed = {'boot':'cbca8738-3b24-4090-b77c-bf029677cdd6','pid':'430851','inv':'a14cc600a4fd4f2e9d8c4731ad9d754b','start':'51172132518','age':1_000_000,'release':'/opt/schubert-nk/releases/0.1.0-PG1068','manifest':b'abc','childPid':'123'}
        def execute(value):
            class Entry:
                def __init__(self,p):self.p=p
                def __truediv__(self,name):return Entry(self.p+'/'+name)
                def readlink(self):return value['release']
                def read_text(self):return value['boot']+'\n'
                def read_bytes(self):
                    if self.p.endswith('RELEASE-MANIFEST.json'):return value['manifest']
                    if self.p.endswith('external-start-issued.private.json'):
                        return b'{"InvocationID":"a14cc600a4fd4f2e9d8c4731ad9d754b","MainPID":"430851","ExecMainStartTimestampMonotonic":"51172132518"}'
                    raise AssertionError('unexpected fixture read')
            def output(cmd,**kwargs):
                unit=cmd[2];parent=unit=='schubert-nk-morning-controller.service'
                return 'InvocationID='+str(value['inv'] if parent else '1'*32)+'\nMainPID='+str(value['pid'] if parent else value['childPid'])+'\nExecMainStartTimestampMonotonic='+str(value['start'])+'\n'
            env={'pathlib':Mock(Path=Entry),'subprocess':Mock(check_output=output),'hashlib':hashlib,'json':json,'time':Mock(monotonic_ns=lambda:51172132518*1000+value['age']),'print':lambda *a:None}
            exec(bytecode,env)
        execute(fixed)
        for key,value in [('boot','cc9ed874-7f4f-450e-a188-8de1e42c8441'),('pid','0'),('pid','430852'),('inv','f'*32),('start','51172132519'),('age',1_800_000_000_000),('release','/opt/foreign'),('manifest',b'foreign'),('childPid','0')]:
            with self.subTest(key=key),self.assertRaises(AssertionError):execute(dict(fixed,**{key:value}))


if __name__ == '__main__':unittest.main()
