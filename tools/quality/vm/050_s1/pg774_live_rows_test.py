"""Independent finite append golden/unknown/change/missing/null/duplicate refusal."""
import ast
import copy
import unittest
from pg774_live_rows import preserved
from pg774_failure_full import source


def fixture():
    old={name:[{'id':7,'literal':'must-preserve'}]for name in ('schubert.app_logs','schubert_web_session.web_http_sessions','schubert_web_session.web_log_outbox')}
    old.update({'other.'+str(i):[]for i in range(21)})
    new=copy.deepcopy(old)
    for name,count in [('schubert.app_logs',56),('schubert_web_session.web_http_sessions',55),('schubert_web_session.web_log_outbox',56)]:
        new[name].extend({'id':100+i,'literal':'new-private'}for i in range(count))
    return old,new


class Test(unittest.TestCase):
    def test_normal_and_all_refusals(self):
        a,b=fixture();self.assertTrue(preserved(a,b))
        self.assertFalse(preserved(None,b));self.assertFalse(preserved(a,None))
        for key in a:
            bad=copy.deepcopy(b);bad[key].append({'id':9999});self.assertFalse(preserved(a,bad))
        for action in ('delete','modify','duplicate','null','missing-table','foreign-table'):
            bad=copy.deepcopy(b)
            if action=='delete':bad['schubert.app_logs'].pop(0)
            elif action=='modify':bad['schubert.app_logs'][0]['literal']='wrong'
            elif action=='duplicate':bad['schubert.app_logs'][1]=copy.deepcopy(bad['schubert.app_logs'][0])
            elif action=='null':bad['schubert.app_logs'][1]=None
            elif action=='missing-table':bad.pop('other.0')
            else:bad['foreign']=[]
            with self.subTest(action=action):self.assertFalse(preserved(a,bad))

    def test_generated_payload_uses_same_pure_contract_and_full_equality_after_capture(self):
        raw=source();p=next(ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets));ast.parse(p)
        self.assertIn('pg774-failure-full758-v1',p);self.assertNotIn('pg773-failure-full758-v1',p)
        self.assertIn('preserved(expected_rows,allrows)',p);self.assertIn('rows()==allrows',p)
        functions=[n for n in ast.parse(p).body if isinstance(n,ast.FunctionDef)and n.name=='preserved']
        assigns=[n for n in ast.parse(p).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='APPENDS'for t in n.targets)]
        self.assertEqual(1,len(functions));self.assertEqual(1,len(assigns))
        env={'json':__import__('json')};exec(compile(ast.Module(body=assigns+functions,type_ignores=[]),'<isolated finite contract>','exec'),env)
        a,b=fixture();self.assertTrue(env['preserved'](a,b))
        b['schubert.app_logs'][0]['literal']='wrong';self.assertFalse(env['preserved'](a,b))


if __name__=='__main__':unittest.main()
