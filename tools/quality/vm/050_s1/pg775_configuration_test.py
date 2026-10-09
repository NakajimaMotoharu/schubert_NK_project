"""Independent literal config set/ordered-field distinction; no PID1 mutation."""
import ast
import unittest
from pg775_configuration import FIELDS,configuration_value
from pg775_failure_full import source


class Test(unittest.TestCase):
    def test_normal_unordered_and_ordered_reject(self):
        value={k:''for k in FIELDS};value.update(Id='literal.service',Requires='b.service a.service',After='c.service a.service',ExecStart='/fixed literal')
        raw=''.join(k+'='+v+'\n'for k,v in value.items());got=configuration_value(raw)
        value.update(Requires='a.service b.service',After='a.service c.service')
        self.assertEqual(got,configuration_value(''.join(k+'='+v+'\n'for k,v in reversed(list(value.items())))))
        for key in FIELDS:
            bad=dict(value);bad[key]+=' unexpected'
            with self.subTest(key=key):self.assertNotEqual(got,configuration_value(''.join(k+'='+v+'\n'for k,v in bad.items())))
        for bad in (None,raw[:-1],raw+'foreign=x\n',raw+'Id=duplicate\n',raw.replace('Requires=b.service a.service','Requires=b.service b.service'),raw.replace('After=c.service a.service','After=c.service  a.service'),raw.replace('Id=literal.service\n','')):
            with self.subTest(bad=type(bad).__name__),self.assertRaises(ValueError):configuration_value(bad)

    def test_payload_complete_and_isolated_same_contract(self):
        raw=source();p=next(ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets));tree=ast.parse(p)
        self.assertIn('pg775-failure-full758-v1',p);self.assertNotIn('pg774-failure-full758-v1',p)
        self.assertIn('configuration_value(command(',p)
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='configuration_value'or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIELDS'for t in n.targets)]
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<literal isolated config>','exec'),env)
        raw=''.join(k+'=\n'for k in FIELDS);self.assertEqual(configuration_value(raw),env['configuration_value'](raw))


if __name__=='__main__':unittest.main()
