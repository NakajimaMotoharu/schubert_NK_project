"""Actual both read entry functions and unchanged stop scope; literal18 schema."""
import ast
import unittest
from pg1833_readonly_parent_state_sources import sources


class Scope(unittest.TestCase):
    def fixture(self):
        return {'Id':'schubert-nk-morning-controller.service','LoadState':'loaded','ActiveState':'failed','SubState':'failed','Result':'exit-code','MainPID':'0','ControlPID':'0','Job':'','InvocationID':'b5a12ee25dc44ec49b08f5d084b4052f','ExecMainCode':'1','ExecMainStatus':'10','ExecMainStartTimestampMonotonic':'81404764713','ExecMainExitTimestampMonotonic':'83018952135','Type':'oneshot','Restart':'no','RemainAfterExit':'no','KillMode':'control-group','SendSIGKILL':'no'}

    def actual(self,raw):
        text=sources()['pg1833_native_owned_stop.py'];tree=ast.parse(text);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['parent_state','show']]
        def require(v):
            if not v:raise ValueError('guard refused')
        def unique(items):
            result={}
            for k,v in items:
                if k in result:raise ValueError('duplicate refused')
                result[k]=v
            return result
        calls=[]
        def command(args):calls.append(args);return raw
        ns={'FIELDS':frozenset(self.fixture()),'ORDER':['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service'],'command':command,'require':require,'unique':unique}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual readonly vs stop scope>','exec'),ns);return ns,calls

    def test_actual_readonly_parent_and_root_stop_show_refusal(self):
        fixture=self.fixture();raw=('\n'.join(k+'='+v for k,v in fixture.items())+'\n').encode();ns,calls=self.actual(raw)
        self.assertEqual(fixture,ns['parent_state']());self.assertEqual(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property='+','.join(sorted(fixture))],calls[0])
        for unit in ['schubert-nk-morning-controller.service','foreign.service']:
            with self.assertRaises(ValueError):ns['show'](unit)
        self.assertEqual(1,len(calls))

    def test_actual_parent_parser_rejects_missing_duplicate_extra_bad(self):
        fixture=self.fixture();good=('\n'.join(k+'='+v for k,v in fixture.items())+'\n').encode()
        for raw in [good.replace(b'Job=\n',b''),good+b'Job=\n',good+b'Unknown=\n',good.rstrip(b'\n'),good.replace(b'Job=\n',b'Job\n')]:
            ns,_=self.actual(raw)
            with self.subTest(rawSha=len(raw)),self.assertRaises(ValueError):ns['parent_state']()


if __name__=='__main__':unittest.main()
