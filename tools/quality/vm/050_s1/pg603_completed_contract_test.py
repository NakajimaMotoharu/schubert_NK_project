"""Independent literal transition/whole preservation mutation tests, management only."""
import copy
import hashlib
import unittest
from pg603_completed_contract import epoch_transition,changed_only,phase_action,same_value

OLD='/opt/schubert-nk/releases/0.1.0-PG548'
NEXT='/opt/schubert-nk/releases/0.1.0-PG600'
STARTUP='/run/schubert-nk/startup'
EPOCH=STARTUP+'/epoch.current'
NEW_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG600\nmanifest_sha256=a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f\n'
OLD_EPOCH=b'NKEPOCH1\nstate=ISSUED\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e\ncutoff_utc=2026-10-08T07:36:21.802335Z\nactivation_id=57f0e73d-d334-4882-9284-04246011da54\npermit_sha256='+b'1'*64+b'\n'
NEW_EPOCH=b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=22222222-2222-4333-8444-555555555555\nrun_id=b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e\ncutoff_utc=2026-10-08T07:36:21.802335Z\nactivation_id=57f0e73d-d334-4882-9284-04246011da54\npermit_sha256=-\n'


def file(raw,inode,mode):return {'metadata':[1,inode,0,0,0o100000|mode,1,len(raw),0,0],'sha256':hashlib.sha256(raw).hexdigest()}


class ContractTest(unittest.TestCase):
    def test_phase_normal_and_forbidden(self):
        state='READY'
        for action in('before','before','after','release'):state=phase_action(state,action)
        self.assertEqual(state,'CLOSED')
        for state,action in [('READY','release'),('CHECKED','before'),('CHECKED','after'),('CLOSED','release'),('CLOSED','before'),('FOREIGN','after'),(None,'before'),('READY',None),('READY','foreign')]:
            with self.subTest(state=state,action=action),self.assertRaises(ValueError):phase_action(state,action)

    def test_epoch_normal_and_negative(self):
        epoch_transition(OLD_EPOCH,NEW_EPOCH)
        for value in (None,b'',NEW_EPOCH+b'foreign=x\n',NEW_EPOCH.replace(b'state=INVALID',b'state=ISSUED'),NEW_EPOCH.replace(b'22222222-2222-4333-8444-555555555555',b'11111111-2222-4333-8444-555555555555'),NEW_EPOCH.replace(b'2026-10-08T07:36:21.802335Z',b'2026-10-09T07:36:21.802335Z'),NEW_EPOCH.replace(b'activation_id=57f0e73d',b'activation_id=67f0e73d'),NEW_EPOCH.replace(b'permit_sha256=-',b'permit_sha256='+b'1'*64)):
            with self.subTest(valueType=type(value).__name__),self.assertRaises((ValueError,UnicodeError)):epoch_transition(OLD_EPOCH,value)

    def test_all_preservation_and_delta(self):
        before={'current':OLD,'startup':{EPOCH:file(OLD_EPOCH,2,0o600),STARTUP:{'metadata':[1,3,0,0,0o40700,2,4096,0,0],'sha256':None},STARTUP+'/old.permit':file(b'fixed old permit',4,0o600)},'approval':file(b'old approval',5,0o400)}
        for key in ('rows','backup','originals','native','units','configuration','credentials','dependencies','oldProofs','parentPid1','pid1Stop','unitFiles','bootstrapOldProofs','bootstrapTools','caddyPre'):before[key]={'preserved':key}
        before['rows']['literalBoolean']=True
        before['runtime']=None
        after=copy.deepcopy(before);after['current']=NEXT;after['startup'][EPOCH]=file(NEW_EPOCH,6,0o600);after['approval']=file(NEW_APPROVAL,7,0o400)
        after['startup'][STARTUP]['metadata'][7:]=[10,10]
        self.assertTrue(changed_only(before,after,OLD_EPOCH,NEW_EPOCH))
        bad=copy.deepcopy(after);bad['rows']['literalBoolean']=1
        with self.assertRaises(ValueError):changed_only(before,bad,OLD_EPOCH,NEW_EPOCH)
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

    def test_types_nonfinite_and_nested_changes_are_not_equal(self):
        self.assertTrue(same_value({'literal':[True,1,1.5,None]}, {'literal':[True,1,1.5,None]}))
        for left,right in [(True,1),(1,True),(1,1.0),([True],[1]),({'k':True},{'k':1}),
                           (float('nan'),float('nan')),(float('inf'),float('inf')),
                           ({1:'x'},{1:'x'}),((),())]:
            with self.subTest(leftType=type(left).__name__):
                self.assertFalse(same_value(left,right))
        self.assertFalse(same_value({'k':[1]}, {'k':[2]}))
        self.assertFalse(same_value({'k':None}, {'other':None}))
        self.assertFalse(same_value([], [None]))


if __name__=='__main__':unittest.main()
