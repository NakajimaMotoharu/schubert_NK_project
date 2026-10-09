"""Independent argv/principal-vs-volatile status contract; no VM or SQL execution."""
import ast
import unittest
from pg781_retained_capture import source


class Test(unittest.TestCase):
    def test_fixed_psql_and_private_capture(self):
        raw=source();p=next(ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        tree=ast.parse(p);call=next(n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='check_output')
        args=ast.literal_eval(call.args[0]);self.assertEqual(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],args[:-2])
        self.assertIn('select coalesce(jsonb_agg(',args[-1]);self.assertIn("'[]'::jsonb",args[-1]);self.assertNotIn('update ',args[-1]);self.assertNotIn('delete ',args[-1])
        self.assertIn('serverAdvisoryHeld',p);self.assertIn('sessions==[]',p)
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='stable');env={}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<literal actor principal>','exec'),env)
        keys=('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid')
        value={'pid':7,'ticks':11,'argvSha256':'literal','status':''.join(k+': 0\n'for k in keys)+'VmRSS: 100\n'}
        self.assertEqual(env['stable'](value),env['stable']({**value,'status':value['status'].replace('VmRSS: 100','VmRSS: 200')}))
        for field in keys:
            bad={**value,'status':value['status'].replace(field+': 0',field+': foreign')};self.assertNotEqual(env['stable'](value),env['stable'](bad))


if __name__=='__main__':unittest.main()
