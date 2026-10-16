"""Independent actual-before58 vectors and unchanged full terminal/24/seal bindings."""
import ast
import copy
import unittest
from pyflakes.api import check,checkPath
import pg4584_current_admission_image as admission
import pg4586_current_independent_acceptance as acceptance


def fixture():
    names=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
    row={'Id':'fixture','LoadState':'loaded','ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':'','InvocationID':'1'*32,'ControlGroup':'/fixture','Result':'success','ExecMainCode':'1','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'1','ExecMainExitTimestampMonotonic':'2','Type':'notify','KillMode':'control-group','SendSIGKILL':'no','RemainAfterExit':'no','Restart':'no'}
    return {'units':{name:dict(row,Id=name)for name in names},'actors':{},'database':{'rows':{str(i):[]for i in range(24)},'peers':[],'locks':[]},'flocks':[],
      'durable':{'backup':{'fixture':'literal'}},'native':{str(i)+'.exec':{'sha256':'a'*64}for i in range(58)},
      'startup':{},'runtime':{},'configuration':{name:{'fixture':'literal'}for name in names}}


class CurrentAcceptance(unittest.TestCase):
    def test_field_only_actual_before_projection(self):
        value=fixture();original=copy.deepcopy(value);pub={'unitFilesActual':{'fixture-unit':[1,2]}}
        got=admission.project(value,pub)
        self.assertEqual({'rows':{str(i):[]for i in range(24)},'durable':{'backup':{'fixture':'literal'}},'oneTimeRuntime':{},'configuration':value['configuration'],'unitFilesActual':{'fixture-unit':[1,2]},'native':{str(i)+'.exec':{'sha256':'a'*64}for i in range(58)}},got)
        self.assertEqual(original,value)

    def test_null_missing_extra_and_old_native_count_refused(self):
        for value in [None,{},dict(fixture(),invented=True)]:
            with self.subTest(kind=type(value)),self.assertRaises(ValueError):admission.project(value,{})
        for key in ['actors','flocks','peers','locks','rows','native']:
            v=fixture()
            if key in ['peers','locks']:v['database'][key]=[{'foreign':True}]
            elif key=='rows':v['database']['rows'].pop('0')
            elif key=='native':v['native'].pop('0.exec')
            else:v[key]=['foreign']
            with self.subTest(key=key),self.assertRaises(ValueError):admission.project(v,{})

    def test_missing_extra_and_live_actual_unit_refused(self):
        for name,change in [('missing',lambda v:v['units'].pop('caddy.service')),('pid',lambda v:v['units']['caddy.service'].update(MainPID='12')),('control',lambda v:v['units']['caddy.service'].update(ControlPID='12')),('job',lambda v:v['units']['caddy.service'].update(Job='10')),('fields',lambda v:v['units']['caddy.service'].pop('Id')),('uncaptured',lambda v:v.update(detailedActors={})),('same-count-foreign',lambda v:(v['units']['caddy.service'].pop('LoadState'),v['units']['caddy.service'].update(foreign='loaded'))),('wrong-type',lambda v:v['units']['caddy.service'].update(MainPID=0)),('config-missing',lambda v:v['configuration'].pop('caddy.service'))]:
            value=fixture();change(value)
            with self.subTest(name=name),self.assertRaises(ValueError):admission.project(value,{})

    def test_complete_actual_factories_no_lifecycle_and_correct_source(self):
        observed={'boot':'79a3260ae16d42bf942ab914ed144c28','invocation':'1'*32,'job':'1','start':1,'rootPid':123,
          'run':'11111111-2222-4333-8444-555555555555','cutoff':'2026-10-17T00:00:00Z','activation':'22222222-3333-4444-8555-666666666666'}
        for label,raw in [('before',admission.payload(observed)),('terminal',acceptance.terminal_payload(observed)),('rows',acceptance.rows_payload(observed,'0'*64)),('seal',acceptance.seal_payload(observed,'0'*64))]:
            with self.subTest(label=label):
                self.assertEqual(0,check(raw,label));compile(raw,label,'exec')
                self.assertIn('964e96e45bb588e7e75798b5adf425cbd9985427',raw)
                self.assertIn('93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',raw)
                self.assertNotIn('pg4240-typed-bom-fresh-noargs-once-v1',raw)
                self.assertNotIn('pg4246-fresh-current-live-binding-v1',raw)
                for forbidden in ["'--no-block'","'daemon-reload'","'poweroff'","'--resume'"]:
                    self.assertNotIn(forbidden,raw)
        before=admission.payload(observed)
        self.assertIn("'nativeExecEntries':58",before);self.assertNotIn('all52',before)
        self.assertIn(admission.PUBLICATION_PATH,before)
        rows=acceptance.rows_payload(observed,'0'*64)
        self.assertIn("before=json.loads(br)['database']['rows']",rows)
        self.assertIn('all24SameCapturedImage',rows)
        self.assertIn('startsStopsSqlReadsWrites',rows)
        self.assertNotIn('subprocess.run',rows)
        seal=acceptance.seal_payload(observed,'0'*64)
        self.assertIn(admission.PUBLICATION_PATH,seal)
        self.assertIn("before=project(before,json.loads(publication_raw))",seal)
        self.assertIn('!=58',seal)
        self.assertNotIn("sum(k.endswith('.exec')for k in value['native'])!=52",seal)
        for name in ['pg4584_current_admission_image.py','pg4586_current_independent_acceptance.py','pg4584_current_acceptance_test.py']:
            self.assertEqual(0,checkPath('tools/quality/'+name))
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in {'kill','unlink'}for n in ast.walk(ast.parse(admission.payload(observed)))))


if __name__=='__main__':unittest.main()
