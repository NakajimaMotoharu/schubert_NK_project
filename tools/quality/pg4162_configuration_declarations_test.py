import ast
import re
import unittest
from pg4058_original_read_profile import contracts
from pg4162_configuration_declarations import same_configurations


class DeclarationTest(unittest.TestCase):
    def fixture(self):
        raw=contracts();tree=ast.parse(raw);nodes=[]
        for n in tree.body:
            if isinstance(n,ast.FunctionDef)and n.name=='exec_record':nodes.append(n)
            elif isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CONFIG_CONTRACT'for t in n.targets):nodes.append(n)
            elif isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='exec':nodes.append(n)
        ns={'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<qualified declaration kernel>','exec'),ns)
        fields=ns['CONFIG_CONTRACT']['FIELDS']
        value={k:''for k in fields};value['Id']='caddy.service'
        value['ExecStart']='{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
        before={'unit'+str(i):dict(value)for i in range(10)};after={k:dict(v)for k,v in before.items()}
        return ns,before,after

    def test_only_runtime_exec_information_may_change(self):
        ns,before,after=self.fixture()
        after['unit0']['ExecStart']=after['unit0']['ExecStart'].replace('stop_time=[n/a]','stop_time=[Fri 2026-10-16 09:23:00 UTC]').replace('pid=0','pid=761848').replace('code=(null)','code=exited')
        self.assertNotEqual(before,after)
        self.assertTrue(same_configurations(before,after,ns['CONFIG_CONTRACT']['same'],ns['exec_record']))

    def test_all_static_fields_argv_path_ignore_flags_and_missing_extra_refused(self):
        ns,before,unused=self.fixture()
        for key in ns['CONFIG_CONTRACT']['FIELDS']:
            after={k:dict(v)for k,v in before.items()};after['unit0'][key]='foreign'
            with self.subTest(field=key):self.assertFalse(same_configurations(before,after,ns['CONFIG_CONTRACT']['same'],ns['exec_record']))
        for old,new in [('/usr/bin/caddy','/tmp/foreign'),(' --config ',' --foreign '),('ignore_errors=no','ignore_errors=yes')]:
            after={k:dict(v)for k,v in before.items()};after['unit0']['ExecStart']=after['unit0']['ExecStart'].replace(old,new)
            self.assertFalse(same_configurations(before,after,ns['CONFIG_CONTRACT']['same'],ns['exec_record']))
        for value in [None,{},{'unit0':before['unit0']}]:
            with self.assertRaises(ValueError):same_configurations(before,value,ns['CONFIG_CONTRACT']['same'],ns['exec_record'])
        self.assertFalse(same_configurations(before,before,lambda *a:1,ns['exec_record']))


if __name__=='__main__':unittest.main()
