"""Literal current epoch/history/retention and single-start observer bindings."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import pg690_fresh_contract as p
from pg690_fresh_parent import source
from pg691_observer import source as observer, watch


class ContractTest(unittest.TestCase):
    def test_current_invalid_not_old_resume(self):
        raw=b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee\nrun_id=601297d0-a8ba-47da-852b-0ffeae409965\ncutoff_utc=2026-10-08T21:33:23.332578Z\nactivation_id=ad15ac4a-8d8e-4970-bcb3-2e000050ce77\npermit_sha256=-\n'
        self.assertTrue(p.invalid_epoch(raw))
        for bad in (None,'text',b'',raw[:-1],raw+b'extra=x\n',raw.replace(b'INVALID',b'ISSUED'),raw.replace(b'4ccc',b'1ccc'),raw.replace(b'601297d0',b'701297d0'),raw.replace(b'332578',b'332579'),raw.replace(b'permit_sha256=-',b'permit_sha256='+b'1'*64)):
            self.assertFalse(p.invalid_epoch(bad))

    def test_exact_prior_32_and_every_current_row_mutation(self):
        steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
        rows=[{'business_date':'2026-10-08','run_id':'old','status':'SUCCESS','step':'BACKUP_DB','attempt':1}for _ in range(482)]
        for run,status,attempt,items in (
            ('3a53b979-fa01-47dd-92a6-7b26affcfb5c','SUCCESS',1,steps),
            ('e49243d5-de84-4714-8612-6912ddc17e9e','SUCCESS',2,steps[:2]),
            ('e49243d5-de84-4714-8612-6912ddc17e9e','SKIPPED',None,steps),
            ('601297d0-a8ba-47da-852b-0ffeae409965',None,None,steps)):
            for s in items:
                a=attempt if attempt is not None else((3 if s in steps[:2]else 2)if run.startswith('e492')else(4 if s in steps[:2]else 3))
                st=status if status is not None else('SUCCESS'if s in steps[:2]else'SKIPPED')
                rows.append({'business_date':'2026-10-09','run_id':run,'status':st,'step':s,'attempt':a})
        self.assertEqual(514,len(rows));self.assertTrue(p.prior_history(rows,'2026-10-09'))
        for bad in (None,[],rows[:-1],rows+[rows[-1]],rows[:-1]+[None]):self.assertFalse(p.prior_history(bad,'2026-10-09'))
        self.assertFalse(p.prior_history(rows,'2026-10-10'))
        for i in range(482,514):
            for key,value in (('run_id','foreign'),('status','FAILED'),('attempt',99),('step','unknown'),('business_date','2026-10-08')):
                bad=copy.deepcopy(rows);bad[i][key]=value
                with self.subTest(i=i,key=key):self.assertFalse(p.prior_history(bad,'2026-10-09'))
                del bad[i][key];self.assertFalse(p.prior_history(bad,'2026-10-09'))

    def test_seven_literal_pairs_oldest_one_and_five_protected(self):
        names=['20261006-172236-49437eda-1681-43a9-883a-424eb55a6166','20261006-210623-91a748b4-1abe-484c-9682-44f46429b324','20261008-130310-b7e73994-b951-4696-bdd1-cfbc8a10e734','20261008-163630-b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e','20261009-003255-3a53b979-fa01-47dd-92a6-7b26affcfb5c','20261009-033251-e49243d5-de84-4714-8612-6912ddc17e9e','20261009-063333-601297d0-a8ba-47da-852b-0ffeae409965']
        with tempfile.TemporaryDirectory(prefix='pg690-literal-backup-')as directory:
            root=Path(directory);rows=[]
            for i,name in enumerate(names):
                d=root/name;d.mkdir();run=name[16:];claims=[]
                for j,step in enumerate(('BACKUP_DB','BACKUP_CONFIG')):
                    row={'id':i*2+j+1,'run_id':run,'status':'SUCCESS','step':step,'attempt':1,'started_at':'2026-10-06T08:22:36Z'};rows.append(row);claims.append({'id':row['id'],'attempt':1,'startedAt':row['started_at']})
                files={}
                for n in ('schubert_nk.dump','config.tar','credentials.tar.age'):
                    b=b'fixed-independent-fixture';(d/n).write_bytes(b);files[n]={'size':len(b),'sha256':hashlib.sha256(b).hexdigest()}
                (d/'MANIFEST.json').write_text(json.dumps({'databaseStep':claims[0],'configurationStep':claims[1],'runId':run,'files':files}))
            for n in ('one.part','two.part','three.part','pgpt-db-305','pgpt-db-308'):(root/n).mkdir()
            actual=p.retention_upper(root,{'schubert.batch_runs':rows})
            self.assertEqual([names[0]],actual['expectedDeleted']);self.assertEqual(1,actual['expectedRetentionDeletes'])
            self.assertEqual(8,actual['maximumEligibleAfterNew']);self.assertEqual(5,actual['protectedLowerBound'])
            for key,value in (('status','FAILED'),('attempt',2),('step','CLEAN_LOG'),('run_id','foreign')):
                bad=copy.deepcopy(rows);bad[0][key]=value
                with self.subTest(key=key),self.assertRaises(AssertionError):p.retention_upper(root,{'schubert.batch_runs':bad})
            manifest=root/names[0]/'MANIFEST.json';m=json.loads(manifest.read_text());m['files']={};manifest.write_text(json.dumps(m))
            with self.assertRaises(AssertionError):p.retention_upper(root,{'schubert.batch_runs':rows})

    def test_fixed_single_start_and_observer_first_current_source(self):
        raw=source();o=observer();w=watch()
        for value in (raw,o,w):compile(value,'<fixed new source campaign>','exec')
        for text in ('pg690-fresh-parent-v1','pg691-observer-v1.started',"'priorBatchRows':514","'priorTodayRuns':32",'pg689-prior-seven-backups',"guard['invalid_epoch']","'originalBudgetSeconds':1800","interval '2 minutes'",'076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'):
            self.assertIn(text,raw)
        action="['systemctl','start','--no-block','schubert-nk-morning-controller.service']"
        self.assertEqual(1,raw.count(action));self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index(action))
        self.assertIn('watch().encode()',o);self.assertIn("sys.argv[3]=='PG682'",w)
        self.assertIn('sameRootOrdinary',w);self.assertIn('authenticate_ready',w)
        for text in ('PG621','PG631','pg626','pg637','--resume 601'):
            self.assertNotIn(text,raw+o+w)


if __name__=='__main__':unittest.main()
