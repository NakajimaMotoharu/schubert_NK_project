"""Independent full-value transition mutations and generated scope/operation ordering."""
import ast
import copy
import unittest
import pg1489_publication_recovery_sources as s

def require(v):
    if not v:raise ValueError('independent transition refused')

class RecoverySourceTest(unittest.TestCase):
    def namespace(self):
        raw=s.refs();tree=ast.parse(raw)
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'validate_current','exec_record'}]
        self.assertEqual(len(nodes),2)
        import re
        ns={'require':require,'ORDER':s.ORDER,'STOPPED':[],'STOP_RECEIPTS':{},'RETIRED':False,'re':re}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pure independent transition>','exec'),ns);return ns
    def fixture(self):
        root='/run/schubert-nk/startup';epoch='b6e5cc96-3279-4cb8-a7f5-6584a3ac62c4'
        return {'source':'public-golden-source','boot':'public-golden-boot','rows':{'golden':[{'id':1,'state':'kept'}]},'durable':{'original':'golden-sha'},'artifacts':{'fixed.jar':'golden-sha'},'brokerActor':{'pid':41805,'fds':{'1':'golden-file'}},'configuration':{n:{'ExecStart':'fixed','declaration':'fixed'}for n in s.ORDER},'units':{n:{'Id':n,'status':'active'}for n in s.ORDER},'pid1CohortObservations':{n:{'pid1':['start-done-fixed']}for n in s.ORDER},'runtime':{'startup':{root:{'metadata':[28,100,0,0,16832,2,100,20,20],'sha256':None},root+'/epoch.current':{'metadata':[28,101,0,0,33152,1,100,20,20],'sha256':'INVALID-fixed'},root+'/'+epoch+'.permit':{'metadata':[28,102,0,0,33152,1,100,20,20],'sha256':'permit-fixed'},root+'/permit-start.intent':{'metadata':[28,103,0,0,33152,1,0,20,20],'sha256':'empty-fixed'}},'native':{'fixed':'kept'}}}
    def test_unchanged_and_stopped_and_only_intent_retired(self):
        ns=self.namespace();expected=self.fixture();ns['expected_current']=expected
        ns['validate_current'](copy.deepcopy(expected))
        value=copy.deepcopy(expected)
        for name in s.ORDER:
            ns['STOPPED'].append(name);value['units'][name]={'Id':name,'status':'inactive'}
            value['pid1CohortObservations'][name]={'pid1':['fixed-start','genuine-stop']}
            ns['STOP_RECEIPTS'][name]={'after':copy.deepcopy(value['units'][name])}
            if name=='artemis.service':value['brokerActor']=None
            ns['validate_current'](copy.deepcopy(value))
        tree=value['runtime']['startup'];root='/run/schubert-nk/startup';del tree[root+'/permit-start.intent'];tree[root]['metadata'][6:]=[90,21,21];ns['RETIRED']=True
        ns['validate_current'](copy.deepcopy(value))
        for mutation in [lambda v:v['rows']['golden'][0].update(state='changed'),lambda v:v['durable'].update(original='changed'),lambda v:v['artifacts'].update(**{'fixed.jar':'changed'}),lambda v:v.update(source='foreign'),lambda v:v.update(boot='foreign'),lambda v:v['runtime']['native'].update(fixed='changed'),lambda v:v['runtime']['startup'][root+'/epoch.current'].update(sha256='ISSUED-forged'),lambda v:v['runtime']['startup'][root].get('metadata').__setitem__(1,999),lambda v:v['configuration'][s.ORDER[0]].update(declaration='changed')]:
            bad=copy.deepcopy(value);mutation(bad)
            with self.assertRaises(ValueError):ns['validate_current'](bad)
    def test_marker_absence_before_stops_and_wrong_order_refused(self):
        ns=self.namespace();v=self.fixture();ns['expected_current']=copy.deepcopy(v)
        del v['runtime']['startup']['/run/schubert-nk/startup/permit-start.intent']
        with self.assertRaises(ValueError):ns['validate_current'](v)
        ns['STOPPED']=[s.ORDER[1]]
        with self.assertRaises(ValueError):ns['validate_current'](self.fixture())
    def test_generated_bindings_and_mutation_scope(self):
        java=s.java();refs=s.refs();compile(refs,'<full candidate>','exec')
        self.assertIn('"recover".equals(args[0])',java)
        self.assertIn('Pg1487PublicationOnlyIntent.retire(startup,invalid,ORIGINAL',java)
        self.assertNotIn('RootFailedStartRecovery',java);self.assertNotIn('.revoke(',java);self.assertNotIn('.invalidate(',java)
        self.assertLess(java.index('"stop-expiry","stop-artemis","stop-cleanup"'),java.index('Pg1487PublicationOnlyIntent.retire'))
        self.assertIn('age<1800',refs);self.assertIn("['994']*4",refs);self.assertIn("['979']*4",refs)
        self.assertNotIn("['systemctl','start'",refs);self.assertNotIn('.unlink(',refs)
        tree=ast.parse(refs);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='stop_one');code=ast.unparse(f)
        self.assertLess(code.index("save(unit + '.stop-reserved.private'"),code.index('subprocess.run'))
        self.assertEqual(code.count('subprocess.run'),1)
        self.assertIn('broker_witness(before, after, raw)',code)

if __name__=='__main__':unittest.main()
