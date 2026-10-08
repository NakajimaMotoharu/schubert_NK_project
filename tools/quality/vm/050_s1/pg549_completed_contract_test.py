"""Independent literal transition/whole preservation mutation tests, management only."""
import copy
import hashlib
import unittest
from pathlib import Path
from pg549_completed_contract import OLD,NEXT,STARTUP,EPOCH,NEW_APPROVAL,epoch_transition,changed_only,phase_action

OLD_EPOCH=b'NKEPOCH1\nstate=ISSUED\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=91a748b4-1abe-484c-9682-44f46429b324\ncutoff_utc=2026-10-06T12:06:14.564793Z\nactivation_id=179758d2-5b77-443a-a743-bf0065e732ea\npermit_sha256='+b'1'*64+b'\n'
NEW_EPOCH=OLD_EPOCH.replace(b'state=ISSUED',b'state=INVALID').replace(b'11111111-2222-4333-8444-555555555555',b'22222222-2222-4333-8444-555555555555').replace(b'permit_sha256='+b'1'*64,b'permit_sha256=-')


def file(raw,inode,mode):return {'metadata':[1,inode,0,0,0o100000|mode,1,len(raw),0,0],'sha256':hashlib.sha256(raw).hexdigest()}


class ContractTest(unittest.TestCase):
    def test_phase_normal_and_forbidden(self):
        state='READY'
        for action in('before','before','after','release'):state=phase_action(state,action)
        self.assertEqual(state,'CLOSED')
        for state,action in [('READY','release'),('CHECKED','before'),('CHECKED','after'),('CLOSED','release'),('CLOSED','before'),('FOREIGN','after'),(None,'before'),('READY',None),('READY','foreign')]:
            with self.subTest(state=state,action=action),self.assertRaises(ValueError):phase_action(state,action)

    def test_readonly_precedes_typed_bom_in_owned_scope(self):
        source=Path(__file__).with_name('Pg549CompletedDeployment.java').read_text()
        body=source[source.index('public static void main'):]
        self.assertLess(body.index('var refs=new References'),body.index('immutableCandidate();'))
        self.assertLess(body.index('immutableCandidate();'),body.index('phase="CANDIDATE_TYPED_BOM"'))
        self.assertLess(body.index('phase="CANDIDATE_TYPED_BOM"'),body.index('publish(next)'))
        self.assertIn('if(result==0)require',source)
        self.assertIn('else Pg387TrustedDeployment.freezeCandidate();',source)

    def test_epoch_normal_and_negative(self):
        epoch_transition(OLD_EPOCH,NEW_EPOCH)
        for value in (None,b'',NEW_EPOCH+b'foreign=x\n',NEW_EPOCH.replace(b'state=INVALID',b'state=ISSUED'),NEW_EPOCH.replace(b'22222222-2222-4333-8444-555555555555',b'11111111-2222-4333-8444-555555555555'),NEW_EPOCH.replace(b'2026-10-06T12:06:14.564793Z',b'2026-10-07T12:06:14.564793Z'),NEW_EPOCH.replace(b'activation_id=179758d2',b'activation_id=279758d2'),NEW_EPOCH.replace(b'permit_sha256=-',b'permit_sha256='+b'1'*64)):
            with self.subTest(valueType=type(value).__name__),self.assertRaises((ValueError,UnicodeError)):epoch_transition(OLD_EPOCH,value)

    def test_all_preservation_and_delta(self):
        before={'current':OLD,'startup':{EPOCH:file(OLD_EPOCH,2,0o600),STARTUP:{'metadata':[1,3,0,0,0o40700,2,4096,0,0],'sha256':None},STARTUP+'/old.permit':file(b'fixed old permit',4,0o600)},'approval':file(b'old approval',5,0o400)}
        for key in ('rows','backup','originals','native','units','configuration','credentials','dependencies','oldProofs','parentPid1','pid1Stop','unitFiles','bootstrapOldProofs','bootstrapTools','caddyPre'):before[key]={'preserved':key}
        before['runtime']=None
        after=copy.deepcopy(before);after['current']=NEXT;after['startup'][EPOCH]=file(NEW_EPOCH,6,0o600);after['approval']=file(NEW_APPROVAL,7,0o400)
        after['startup'][STARTUP]['metadata'][7:]=[10,10]
        self.assertTrue(changed_only(before,after,OLD_EPOCH,NEW_EPOCH))
        for key in before.keys()-{'current','startup','approval'}:
            bad=copy.deepcopy(after)
            if key=='runtime':bad[key]={'foreign':'runtime'}
            else:bad[key]['preserved']='mutated'
            with self.subTest(key=key),self.assertRaises(ValueError):changed_only(before,bad,OLD_EPOCH,NEW_EPOCH)
        for change in ('extra','permit','inode','mode','hash','dir','current','schema'):
            bad=copy.deepcopy(after)
            if change=='extra':bad['startup']['extra']=file(b'x',8,0o600)
            if change=='permit':bad['startup'][STARTUP+'/old.permit']['sha256']='0'*64
            if change=='inode':bad['startup'][EPOCH]['metadata'][1]=2
            if change=='mode':bad['approval']['metadata'][4]=0o100600
            if change=='hash':bad['approval']['sha256']='0'*64
            if change=='dir':bad['startup'][STARTUP]['metadata'][1]=9
            if change=='current':bad['current']=OLD
            if change=='schema':del bad['rows']
            with self.subTest(change=change),self.assertRaises(ValueError):changed_only(before,bad,OLD_EPOCH,NEW_EPOCH)
        for raw in (OLD_EPOCH.replace(b'11111111-2222-4333-8444-555555555555',b'33333333-2222-4333-8444-555555555555'),OLD_EPOCH.replace(b'permit_sha256='+b'1'*64,b'permit_sha256='+b'2'*64)):
            with self.assertRaises(ValueError):changed_only(before,after,raw,NEW_EPOCH)
        for key in before:
            bad=copy.deepcopy(before);del bad[key]
            with self.subTest(missing=key),self.assertRaises(ValueError):changed_only(bad,after,OLD_EPOCH,NEW_EPOCH)


if __name__=='__main__':unittest.main()
