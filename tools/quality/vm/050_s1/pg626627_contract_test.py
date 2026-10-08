"""Same-day fresh source independent history/epoch/retention literals; no VM actions."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from pg626_fresh_parent_contract import prior_history,invalid_epoch,skipped_cleanup_oracle,retention_upper

R=Path(__file__).resolve().parent


class ContractTest(unittest.TestCase):
    def test_current_completed_history_only_and_foreign_duplicates(self):
        steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
        prior=[{'business_date':'2026-10-08','run_id':'old','status':'SUCCESS','step':'BACKUP_DB'}for _ in range(482)]
        today=[{'business_date':'2026-10-09','run_id':'3a53b979-fa01-47dd-92a6-7b26affcfb5c','status':'SUCCESS','step':s}for s in steps]
        rows=prior+today;self.assertTrue(prior_history(rows,'2026-10-09'))
        for bad in (None,[],rows[:-1],rows+[today[0]],rows[:-1]+[today[0]],rows[:-1]+[None]):self.assertFalse(prior_history(bad,'2026-10-09'))
        for key,value in [('run_id','foreign'),('status','SKIPPED'),('status','FAILED'),('business_date','2026-10-08'),('step','foreign')]:
            bad=copy.deepcopy(rows);bad[-1][key]=value;self.assertFalse(prior_history(bad,'2026-10-09'))
        for day in (None,False,'2026-10-08','2026-10-10'):self.assertFalse(prior_history(rows,day))

    def test_old_epoch_invalid_only_and_current_fixture_preserved(self):
        raw=b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee\nrun_id=3a53b979-fa01-47dd-92a6-7b26affcfb5c\ncutoff_utc=2026-10-08T15:32:46.368375Z\nactivation_id=970bbce1-6bba-4db0-ace1-680ee7dfde92\npermit_sha256=-\n'
        self.assertTrue(invalid_epoch(raw))
        for bad in (None,'text',b'',raw[:-1],raw+b'foreign=x\n',raw.replace(b'INVALID',b'ISSUED'),raw.replace(b'4ccc',b'1ccc'),raw.replace(b'3a53b979',b'4a53b979'),raw.replace(b'970bbce1',b'870bbce1'),raw.replace(b'368375',b'368376'),raw.replace(b'permit_sha256=-',b'permit_sha256='+b'1'*64)):
            self.assertFalse(invalid_epoch(bad))

    def test_same_admission_oracle_does_not_fake_fresh_cleanup(self):
        keys=['notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references','inbox_scan_candidates']
        good={k:[]for k in keys};good['web_http_sessions']=['expired-but-skipped'];self.assertTrue(skipped_cleanup_oracle(good,copy.deepcopy(good)))
        for bad in (None,{},[],{**good,'foreign':[]},{**good,'questions':[None]},{**good,'questions':'x'},{**good,'web_http_sessions':[]}):
            self.assertFalse(skipped_cleanup_oracle(good,bad))

    def test_literal_retention_one_oldest_and_all_five_protected(self):
        with tempfile.TemporaryDirectory(prefix='pg626-independent-')as directory:
            root=Path(directory);rows=[]
            names=['20260930-120030-31100027-2222-4333-8444-555555555555']+[f'20261008-1{i}0030-31100027-2222-4333-8444-555555555555'for i in range(6)]
            for i,name in enumerate(names):
                p=root/name;p.mkdir();claims=[]
                for j,step in enumerate(['BACKUP_DB','BACKUP_CONFIG']):
                    row={'id':i*2+j+1,'run_id':'31100027-2222-4333-8444-555555555555','status':'SUCCESS','step':step,'attempt':1,'started_at':'2026-09-30T03:00:30Z'};rows.append(row);claims.append({'id':row['id'],'attempt':1,'startedAt':'2026-09-30T03:00:30Z'})
                files={}
                for name2 in ['schubert_nk.dump','config.tar','credentials.tar.age']:
                    value=b'independent literal fixture';(p/name2).write_bytes(value);files[name2]={'size':len(value),'sha256':hashlib.sha256(value).hexdigest()}
                (p/'MANIFEST.json').write_text(json.dumps({'databaseStep':claims[0],'configurationStep':claims[1],'runId':'31100027-2222-4333-8444-555555555555','files':files}))
            for name in ['one.part','two.part','three.part','pgpt-db-305','pgpt-db-308']:(root/name).mkdir()
            result=retention_upper(root,{'schubert.batch_runs':rows})
            self.assertEqual(result['expectedDeleted'],['20260930-120030-31100027-2222-4333-8444-555555555555'])
            self.assertEqual(result['expectedRetentionDeletes'],1);self.assertEqual(result['protectedLowerBound'],5)
            rows[0]['status']='FAILED'
            with self.assertRaises(AssertionError):retention_upper(root,{'schubert.batch_runs':rows})

    def test_exact_source_paths_prior_completed_and_one_shot_guard(self):
        parent=(R/'pg626_fresh_parent.py').read_text();tree=ast.parse(parent)
        values={t.id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)for t in n.targets if isinstance(t,ast.Name)and t.id in ('SOURCE','DIGEST','PAYLOAD')}
        self.assertEqual(values['SOURCE'],'72fb7440697ee1048a5c0145055dc1cc3c577914');self.assertEqual(values['DIGEST'],'4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e')
        payload=values['PAYLOAD'];ast.parse(payload)
        action="['systemctl','start','--no-block','schubert-nk-morning-controller.service']"
        self.assertEqual(payload.count(action),1);self.assertLess(payload.index("persist('external-start-guard.private.json'"),payload.index(action))
        for value in ['pg624-completed-activate-v1/after.private.json','11675ec02384a125f762014ebb1da251a2ab07c466aa8465bcd0f05ee284ce91',"'originalBudgetSeconds':1800","'priorBatchRows':492","'--resume'not in execstart","now()+interval '2 minutes'","'nonBackupExpectedSkipped':8"]:self.assertIn(value,payload)
        self.assertIn('pg627-observer-v1.started',parent)
        for filename in ['pg626_fresh_parent.py','pg627_observer.py','pg627_watch_parent.py']:
            source=(R/filename).read_text();ast.parse(source)
            for old in ['pg605','pg606','PG600','23b14a44','a6342b8a']:self.assertNotIn(old,source)


if __name__=='__main__':unittest.main()
