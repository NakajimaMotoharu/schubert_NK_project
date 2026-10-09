"""Literal current source/history plus dependency-free injected oracle and one-shot."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import textwrap
import unittest
import pg721_backup_preserve as a
import pg722_fresh_contract as p
import pg722_fresh_parent as b
import pg723_observer as c


class ContractTest(unittest.TestCase):
    def test_retention_current_oldest_and_each_rejection(self):
        # Existing independent literal fixture reused, not production-generated expected.
        raw = b.R.joinpath('pg690691_contract_test.py').read_text()
        tree = ast.parse(raw)
        method = next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)
                      and n.name=='test_seven_literal_pairs_oldest_one_and_five_protected')
        body = textwrap.dedent(ast.get_source_segment(raw,method))
        old = "'20261006-172236-49437eda-1681-43a9-883a-424eb55a6166',"
        self.assertEqual(1,body.count(old)); body=body.replace(old,'')
        oldlast = "'20261009-063333-601297d0-a8ba-47da-852b-0ffeae409965']"
        self.assertEqual(1,body.count(oldlast))
        body=body.replace(oldlast,"'20261009-063333-601297d0-a8ba-47da-852b-0ffeae409965','20261009-094310-8633b77f-77dc-4a78-88b4-41165f159b43']")
        env={'p':p,'Path':Path,'tempfile':tempfile,'hashlib':hashlib,'json':json,'copy':copy}
        exec(compile(body,'<literal seven current retention fixture>','exec'),env)
        env[method.name](self)

    def test_current_invalid_and_all_foreign_fields(self):
        raw = b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\nepoch_id=aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee\nrun_id=8633b77f-77dc-4a78-88b4-41165f159b43\ncutoff_utc=2026-10-09T00:43:10.150245Z\nactivation_id=c6815985-26c5-4f5f-aed0-abc81fa8f71e\npermit_sha256=-\n'
        self.assertTrue(p.invalid_epoch(raw))
        for bad in (None,'text',b'',raw[:-1],raw+b'extra=x\n',raw.replace(b'INVALID',b'ISSUED'),raw.replace(b'4ccc',b'1ccc'),raw.replace(b'8633b77f',b'9633b77f'),raw.replace(b'150245',b'150246'),raw.replace(b'permit_sha256=-',b'permit_sha256='+b'1'*64)):
            self.assertFalse(p.invalid_epoch(bad))

    def test_history524_today42_and_each_column_rejected(self):
        steps = ['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
        rows = [{'business_date':'2026-10-08','run_id':'older','status':'SUCCESS','step':'BACKUP_DB','attempt':1} for _ in range(482)]
        for run, backup_attempt, cleanup_attempt in (
            ('3a53b979-fa01-47dd-92a6-7b26affcfb5c',1,1),
            ('e49243d5-de84-4714-8612-6912ddc17e9e',3,2),
            ('601297d0-a8ba-47da-852b-0ffeae409965',4,3),
            ('8633b77f-77dc-4a78-88b4-41165f159b43',5,4)):
            if backup_attempt==3:
                for s in steps[:2]:
                    rows.append({'business_date':'2026-10-09','run_id':run,'status':'SUCCESS','step':s,'attempt':2})
            for s in steps:
                status = 'SUCCESS' if backup_attempt==1 or (backup_attempt!=3 and s in steps[:2]) else 'SKIPPED'
                rows.append({'business_date':'2026-10-09','run_id':run,'status':status,'step':s,'attempt':backup_attempt if s in steps[:2] else cleanup_attempt})
        self.assertEqual(524,len(rows)); self.assertTrue(p.prior_history(rows,'2026-10-09'))
        for bad in (None,[],rows[:-1],rows+[rows[-1]],rows[:-1]+[None]):
            self.assertFalse(p.prior_history(bad,'2026-10-09'))
        self.assertFalse(p.prior_history(rows,'2026-10-10'))
        for i in range(482,524):
            for key, value in (('run_id','foreign'),('status','FAILED'),('step','UNKNOWN'),('attempt',99),('business_date','2026-10-08')):
                bad = copy.deepcopy(rows); bad[i][key]=value
                self.assertFalse(p.prior_history(bad,'2026-10-09'))
                del bad[i][key]; self.assertFalse(p.prior_history(bad,'2026-10-09'))

    def test_newslots_source_signature_and_injected_graph(self):
        archive, parent, observer, watch = a.source(), b.source(), c.source(), c.watch()
        for raw in (archive,parent,observer,watch):
            ast.parse(raw)
        for text in ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','pg721-prior-seven-backups','pg717-completed-activate-v1','3849806f2d462004c9135ed29b914388bf17d903219a2dc65a73bf23764eed7a'):
            self.assertIn(text,archive)
        for text in ("'priorBatchRows':524","'priorTodayRuns':42",'pg723-observer-v1.started','pg722_fresh_contract.py','PG715',"'originalBudgetSeconds':1800","interval '2 minutes'",'74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'):
            self.assertIn(text,parent)
        start = "['systemctl','start','--no-block','schubert-nk-morning-controller.service']"
        self.assertEqual(1,parent.count(start)); self.assertLess(parent.index("persist('external-start-guard.private.json'"),parent.index(start))
        self.assertIn("sys.argv[3]=='PG715'",watch)
        self.assertIn('sameRootOrdinary',watch); self.assertIn('authenticate_ready',watch)
        raw = b.R.joinpath('pg722_fresh_contract.py').read_text()
        self.assertFalse(any(isinstance(n,ast.ImportFrom) for n in ast.parse(raw).body))
        namespace = {'__name__':'independent_guard_fixture'}
        exec(compile(raw,'<no local module dependencies>','exec'),namespace)
        self.assertTrue(callable(namespace['prior_history']))
        self.assertTrue(callable(namespace['skipped_cleanup_oracle']))
        for old in ('pg690','pg691','pg689','PG682'):
            self.assertNotIn(old,archive+parent+observer+watch)


if __name__ == '__main__':
    unittest.main()
