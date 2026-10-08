"""New same-day normal admission, independent null/history/epoch negatives."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from pg650_fresh_contract import completed_epoch,prior_history,retention_upper
from pg650_fresh_parent import source,guest_contract
from pg651_observer import source as observer


class Contract(unittest.TestCase):
    def test_retention_independent_eight_valid_pairs_two_oldest(self):
        with tempfile.TemporaryDirectory(prefix='pg650-retention-')as directory:
            root=Path(directory);rows=[]
            names=['20260930-120030-31100027-2222-4333-8444-555555555555']+[f'20261008-1{i}0030-31100027-2222-4333-8444-555555555555'for i in range(7)]
            for i,name in enumerate(names):
                p=root/name;p.mkdir();claims=[]
                for j,step in enumerate(('BACKUP_DB','BACKUP_CONFIG')):
                    row={'id':i*2+j+1,'run_id':'31100027-2222-4333-8444-555555555555','status':'SUCCESS','step':step,'attempt':1,'started_at':'2026-09-30T03:00:30Z'};rows.append(row);claims.append({'id':row['id'],'attempt':1,'startedAt':row['started_at']})
                files={}
                for name2 in ('schubert_nk.dump','config.tar','credentials.tar.age'):
                    value=b'literal-independent';(p/name2).write_bytes(value);files[name2]={'size':len(value),'sha256':hashlib.sha256(value).hexdigest()}
                (p/'MANIFEST.json').write_text(json.dumps({'databaseStep':claims[0],'configurationStep':claims[1],'runId':row['run_id'],'files':files}))
            for name in ('one.part','two.part','three.part','pgpt-db-305','pgpt-db-308'):(root/name).mkdir()
            got=retention_upper(root,{'schubert.batch_runs':rows})
            self.assertEqual(got['expectedDeleted'],names[:2]);self.assertEqual(got['expectedRetentionDeletes'],2)
            self.assertEqual(got['maximumEligibleAfterNew'],9);self.assertEqual(got['protectedLowerBound'],5)
            rows[0]['status']='FAILED'
            with self.assertRaises(AssertionError):retention_upper(root,{'schubert.batch_runs':rows})

    def test_completed_issued_epoch_not_operator_invalidation(self):
        raw=b'NKEPOCH1\nstate=ISSUED\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee\nrun_id=e49243d5-de84-4714-8612-6912ddc17e9e\ncutoff_utc=2026-10-08T18:32:42.140966Z\nactivation_id=7d381b67-b37b-48c6-99ac-e04a336f887d\npermit_sha256='+b'1'*64+b'\n'
        self.assertTrue(completed_epoch(raw))
        for bad in (None,'text',b'',raw[:-1],raw+b'extra=x\n',raw.replace(b'ISSUED',b'INVALID'),raw.replace(b'4ccc',b'1ccc'),raw.replace(b'e49243d5',b'a49243d5'),raw.replace(b'140966',b'140967'),raw.replace(b'permit_sha256='+b'1'*64,b'permit_sha256=-')):
            self.assertFalse(completed_epoch(bad))

    def test_twenty_two_today_original_and_skip_history_preserved(self):
        steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
        old=[{'business_date':'2026-10-08','run_id':'old','status':'SUCCESS','step':'BACKUP_DB','attempt':1}for _ in range(482)]
        today=[{'business_date':'2026-10-09','run_id':'3a53b979-fa01-47dd-92a6-7b26affcfb5c','status':'SUCCESS','step':s,'attempt':1}for s in steps]
        today +=[{'business_date':'2026-10-09','run_id':'e49243d5-de84-4714-8612-6912ddc17e9e','status':'SUCCESS','step':s,'attempt':2}for s in steps[:2]]
        today +=[{'business_date':'2026-10-09','run_id':'e49243d5-de84-4714-8612-6912ddc17e9e','status':'SKIPPED','step':s,'attempt':3}for s in steps]
        rows=old+today;self.assertTrue(prior_history(rows,'2026-10-09'))
        for bad in (None,[],rows[:-1],rows+[today[0]],rows[:-1]+[None]):self.assertFalse(prior_history(bad,'2026-10-09'))
        for index in (482,492,494):
            for key,value in (('step','foreign'),('status','FAILED'),('run_id','foreign'),('business_date','2026-10-08')):
                bad=copy.deepcopy(rows);bad[index][key]=value
                with self.subTest(index=index,key=key):self.assertFalse(prior_history(bad,'2026-10-09'))
        bad=copy.deepcopy(rows);bad[-1]['attempt']=2;self.assertFalse(prior_history(bad,'2026-10-09'))

    def test_finite_current_transport_before_single_start(self):
        v=source();g=guest_contract();o=observer()
        for x in (v,g,o):compile(x,'<new campaign>','exec')
        for x in ('pg650-fresh-parent-v1','pg651-observer-v1.started',"'priorBatchRows':504","'priorTodayRuns':22",'pg649-prior-eight-backups',"guard['completed_epoch']","'originalBudgetSeconds':1800","interval '2 minutes'"):
            self.assertIn(x,v)
        action="['systemctl','start','--no-block','schubert-nk-morning-controller.service']"
        self.assertEqual(v.count(action),1);self.assertLess(v.index("persist('external-start-guard.private.json'"),v.index(action))
        self.assertIn("'expectedRetentionDeletes':2",g);self.assertIn("'maximumEligibleAfterNew':9",g)
        self.assertIn('pg638_watch_parent.py',o);self.assertIn('pg650-fresh-parent-v1',o)
        for x in ('PG621','pg626-prepare-v2','invalid_epoch','11675ec0'):
            self.assertNotIn(x,v)


if __name__=='__main__':unittest.main()
