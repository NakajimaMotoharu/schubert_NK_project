import ast
import copy
import hashlib
import unittest
from pyflakes.api import check,checkPath
import pg4900_current_admission_image as admission
import pg4902_current_genuine_terminal as terminal
import pg4904_current_same_day_rows as rows
import pg4906_current_whole_seal as seal


class Acceptance(unittest.TestCase):
    def test_actual_generation_full11_source_before72_never_old_credit(self):
        observed=admission.live();raw=admission.payload(observed)
        self.assertEqual(0,check(raw,'<actual immutable full11 admission>'))
        for text in (admission.SOURCE,admission.BOM,admission.ONCE,admission.PUBLICATION,admission.PUBLICATION_PATH,"'nativeExecEntries':72",'!=72',observed['run'],observed['activation']):self.assertIn(text,raw)
        self.assertNotIn(admission.previous.SOURCE,raw);self.assertNotIn(admission.previous.ONCE,raw)
        self.assertNotIn('systemctl',raw);self.assertNotIn('os.system',raw)

    def test_lossless_projection_null_foreign_schema_and_nonquiescent_rejected(self):
        units={str(i):{'MainPID':'0','ControlPID':'0','Job':''}for i in range(10)}
        value={'backup':{'literal-backup':['independent']},'configuration':{n:{}for n in units},'extraDurable':{'credentials':{'literal-key-path':['metadata-only']},'oldProofs':{'literal-proof-path':['metadata-only']}},'originals':{'literal-original':['independent']},'pid1':{},'rows':{str(i):[]for i in range(24)},'runtime':{},'startup':{},'unitFilesActual':{'literal-unit':['independent']},'units':units,'native':{str(i)+'.exec':{}for i in range(72)}}
        publication={'unitFilesActual':copy.deepcopy(value['unitFilesActual'])};before=copy.deepcopy(value)
        projected=admission.project(value,publication)
        self.assertEqual({'originals':value['originals'],'backup':value['backup'],**value['extraDurable']},projected['durable']);self.assertEqual(before,value)
        self.assertEqual(value['native'],projected['native'])
        for change in (lambda v:v.pop('rows'),lambda v:v.update(database={}),lambda v:v.update(rows=None),lambda v:v['native'].pop('0.exec'),lambda v:v['units']['0'].update(MainPID='2'),lambda v:v.update(extraDurable={})):
            bad=copy.deepcopy(value);change(bad)
            with self.assertRaises(ValueError):admission.project(bad,publication)
        with self.assertRaises(ValueError):admission.project(None,publication)
        with self.assertRaises(ValueError):admission.project(value,{'unitFilesActual':{}})

    def test_terminal_binds_actual_generation_independent_pid1_and_original_budget(self):
        raw=terminal.payload(admission.live());self.assertEqual(0,check(raw,'<genuine current terminal>'))
        observed=admission.live()
        for text in (admission.SOURCE,admission.BOM,terminal.TERM,observed['invocation'],observed['run'],"'_PID=1'",'1800','genuineRootDone'):self.assertIn(text,raw)
        self.assertNotIn('pg4734-parent-watch-v1',raw);self.assertNotIn('pg4754-new-current-genuine-terminal-v1',raw)

    def test_raw_all24_durable_before_parse_and_current_cutoff(self):
        raw=rows.payload(admission.live(),'a'*64)
        self.assertEqual(0,check(raw,'<pure all24 emission, not actual observation>'))
        self.assertLess(raw.index("preserve('sql-stdout.private.jsonl'"),raw.index('for line in r.stdout.splitlines():'))
        self.assertLess(raw.index("preserve('after.private.json'"),raw.index('result=qualify(before,now,'))
        self.assertIn("before=json.loads(br)['rows']",raw);self.assertNotIn("json.loads(br)['database']",raw)
        self.assertIn('NKQRY1',raw);self.assertIn(admission.SOURCE,raw)

    def test_whole_guard_independent_oracle_actual_full11_and72(self):
        raw=seal.payload(admission.live(),'a'*64)
        self.assertEqual(0,check(raw,'<pure whole emission, not actual seal>'))
        constants={t.id:ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name) and t.id in {'ORACLE','GUARD'}}
        self.assertEqual({'ORACLE','GUARD'},set(constants));self.assertIn('NKQRY1',constants['ORACLE'])
        self.assertIn("require({'CLEAN_SESSION','CLEAN_LOG','CLEAN_NOTIFICATION'}<=skips)",constants['ORACLE'])
        self.assertIn('all72 old native',raw);self.assertNotIn(admission.previous.SOURCE,raw)
        self.assertIn('genuineRootDone',constants['GUARD']);self.assertIn('1800',constants['GUARD'])
        self.assertIn(seal.SLOT,raw);self.assertNotIn('pg4760-new-current-whole-seal-v1',raw)
        for text in ('pg4576-current-fresh-noargs-once-v1','pg4578-current-live-binding','pg4552-failed-current-publication-post-v1','f14b97d22963b2ad3eeea7dbcb5087fcb6885047d965256ffca444fbf1f306b5'):
            self.assertNotIn(text,raw)
        self.assertIn(admission.ONCE+'/before.private.json',raw)
        self.assertIn(admission.PUBLICATION_PATH,raw);self.assertIn(admission.PUBLICATION,raw)
        self.assertNotIn('0.1.0-PG4432',raw);self.assertNotIn('pg4432-manifest.sig',raw)
        self.assertNotIn('0.1.0-PG4702',raw);self.assertNotIn('pg4702-manifest.sig',raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG4860',raw);self.assertIn('pg4860-manifest.sig',raw)
        for path in (admission.__file__,terminal.__file__,rows.__file__,seal.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_prior_successful_admission_and_terminal_emissions_remain_byte_identical(self):
        for slot,raw in ((admission.SLOT,admission.payload(admission.live())),(terminal.TERM,terminal.payload(admission.live()))):
            actual=(admission.W/slot/'payload.private.py').read_bytes()
            self.assertEqual(actual,raw.encode());self.assertEqual(hashlib.sha256(actual).hexdigest(),hashlib.sha256(raw.encode()).hexdigest())


if __name__=='__main__':unittest.main()
