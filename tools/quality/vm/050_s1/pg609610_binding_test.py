"""Frozen new-cohort tools; literal PID1 vector and finite deadline, no VM action."""
import ast
import copy
import datetime
from pathlib import Path
import unittest
from pg609_parent_receipt import completed
R=Path(__file__).resolve().parent
class Test(unittest.TestCase):
    def test_done_binding(self):
        expected=(R/'pg578_capture_done.py').read_text()
        for a,b in [["969d8ded10c0bf5841d9e3a5c531e922caf4a24a","23b14a44b10504172e030bbd6625926bf049fb5c"],["a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b","a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f"],["b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e","3a53b979-fa01-47dd-92a6-7b26affcfb5c"],["557ae9688c03162fe1962cd81d93eb9e4a70eb9acca998a02040afb96f0ec505","f6b3a93a9ad83396098fea7bbabef6fb03ca47b5e9a0e4e4bac0902f7b5ad8be"],["267003d6e12845dd8690cd9bd5afcad0","5a1acaa0c35e484c979401e3b6dfb36a"],["57679957905","86264628081"],["76444","87863"],["909808","1207482"],["0.1.0-PG548","0.1.0-PG600"],["pg573-fresh-parent-v2","pg605-fresh-parent-v2"],["pg574-observer-v1","pg606-observer-v1"],["pg575-chr-a01-native-v1","pg607-chr-a01-native-v1"],["pg576-client-v1","pg608-client-v1"],["pg578-completed-readonly-v1","pg609-completed-readonly-v1"],["PG578-completed-readonly-v1","PG609-completed-readonly-v1"]]:expected=expected.replace(a,b)
        expected=expected.replace("pg556_parent_receipt.py","pg609_parent_receipt.py")
        actual=(R/'pg609_capture_done.py').read_text()
        self.assertEqual(actual,expected)
        tree=ast.parse(actual)
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        ast.parse(payload)
        self.assertIn("'MainPID']=='1207482'",payload)
        self.assertIn("'operationAuthority':False",payload)
    def test_preui_binding(self):
        expected=(R/'pg555_capture_preui.py').read_text()
        for a,b in [["pg553-newrun-preflight-v2","pg605-fresh-parent-v2"],["b9a70c2635febf3893b17369af3ddfdf721f040b3d6782423790ee63353bac87","f6b3a93a9ad83396098fea7bbabef6fb03ca47b5e9a0e4e4bac0902f7b5ad8be"],["969d8ded10c0bf5841d9e3a5c531e922caf4a24a","23b14a44b10504172e030bbd6625926bf049fb5c"],["pg555-preui-v1","pg610-preui-v1"],["581443","1207482"],["075ad6644b284056a6cccf7af252519b","5a1acaa0c35e484c979401e3b6dfb36a"],["59402","87863"],["deadline=time.monotonic()+1200","deadline=86264628081/1e6+1800"],["sealed['bounds']","old['bounds']"],["sealed['inboxExpectedDeleted']","sealed['expected']['inbox_scan_candidates']"],["PG555_PREUI","PG610_PREUI"]]:expected=expected.replace(a,b)
        actual=(R/'pg610_capture_preui.py').read_text()
        self.assertEqual(actual,expected);ast.parse(actual)
        self.assertIn('deadline=86264628081/1e6+1800',actual)
        self.assertIn("pg555_cleanup_postcondition.py",actual)
        self.assertIn("sealed['expected']['inbox_scan_candidates']",actual)
    def test_literal_genuine_pid1_and_original(self):
        # Independent timestamp calculation from an explicit UTC literal, not Production.
        stamp=int(datetime.datetime.fromisoformat('2026-10-08T15:33:46.368375+00:00').timestamp()*1000000)
        base={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd',
              'UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'5a1acaa0c35e484c979401e3b6dfb36a',
              '__MONOTONIC_TIMESTAMP':'86324628081','__REALTIME_TIMESTAMP':str(stamp)}
        rows=[dict(base,__CURSOR='literal1',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='87863',JOB_TYPE='start',JOB_RESULT='done'),
              dict(base,__CURSOR='literal2',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        done=b'NKDONE1\n3a53b979-fa01-47dd-92a6-7b26affcfb5c\n2026-10-08T15:32:46.368375Z\n970bbce1-6bba-4db0-ace1-680ee7dfde92\n2026-10-08T15:33:45.368375Z\n0\n'
        self.assertEqual(completed(rows,done)['elapsedSeconds'],60)
        for k in rows[0]:
            if k=='__CURSOR':continue
            for bad in (None,'foreign'):
                changed=copy.deepcopy(rows);changed[0][k]=bad
                with self.assertRaises(ValueError):completed(changed,done)
        changed=copy.deepcopy(rows);changed[0]['__CURSOR']='foreign'
        self.assertEqual(completed(changed,done)['elapsedSeconds'],60)
        for bad in (None,'','literal2'):
            changed=copy.deepcopy(rows);changed[0]['__CURSOR']=bad
            with self.assertRaises(ValueError):completed(changed,done)
        changed=copy.deepcopy(rows);del changed[0]['__CURSOR']
        with self.assertRaises(ValueError):completed(changed,done)
        for bad in (None,[],rows[:1],rows+rows):
            with self.assertRaises(ValueError):completed(bad,done)
        for bad in (None,b'',done.replace(b'\n0\n',b'\n143\n'),done.replace(b'3a53b979',b'b62b6984')):
            with self.assertRaises(ValueError):completed(rows,bad)
if __name__=='__main__':unittest.main()
