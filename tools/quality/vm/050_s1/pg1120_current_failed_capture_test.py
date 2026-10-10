"""Independent failed-cohort delta oracle and immutable read-only capture structure."""
import ast
import copy
import unittest
from pg1120_current_failed_capture import PAYLOAD


class FailedCaptureTest(unittest.TestCase):
    def namespace(self):
        tree=ast.parse(PAYLOAD)
        names={'require','row_oracle'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
        self.assertEqual(len(nodes),2)
        env={'RUN':'343a5a1b-d064-47d5-88c2-31c36d7ba7a4'}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<literal row oracle>','exec'),env)
        return env

    def fixture(self):
        old=[{'id':i}for i in range(594)]
        before={'schubert.batch_runs':old,'schubert.answers':[{'literal':'unchanged'}]}
        steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_INBOX_OUTBOX','CLEAN_LOG',
               'CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_TRANSFER',
               'CLEAN_BATCH_RUN','CLEAN_EXPIRY']
        delta=[dict(step=x,run_id='343a5a1b-d064-47d5-88c2-31c36d7ba7a4',
                    business_date='2026-10-10',status='SKIPPED',error_code='ALREADY_SUCCESSFUL',
                    error_summary='step already successful for business date',
                    target_count=0,success_count=0,failure_count=0,byte_count=0,
                    started_at='2026-10-10T12:41:00+00:00',ended_at='2026-10-10T12:41:01+00:00')
               for x in steps]
        return before,{'schubert.batch_runs':copy.deepcopy(old)+delta,
                       'schubert.answers':[{'literal':'unchanged'}]}

    def test_literal_594_plus_10_and_other_table(self):
        env=self.namespace();before,actual=self.fixture();env['baseline']={'rows':before}
        env['row_oracle'](actual)
        self.assertEqual(len(actual['schubert.batch_runs']),604)
        self.assertEqual(before,self.fixture()[0])

    def test_null_missing_foreign_nonzero_or_changed_existing(self):
        env=self.namespace();before,actual=self.fixture();env['baseline']={'rows':before}
        cases=[None,{},dict(actual,extra=[])]
        value=copy.deepcopy(actual);value['schubert.answers']=[]
        cases.append(value)
        for key,bad in [('run_id','old'),('business_date','2026-10-11'),
                        ('status','SUCCESS'),('error_code',None),('target_count',1),
                        ('success_count',1),('failure_count',1),('byte_count',1),
                        ('started_at',None),('ended_at',None),('step','UNKNOWN')]:
            value=copy.deepcopy(actual);value['schubert.batch_runs'][-1][key]=bad;cases.append(value)
        value=copy.deepcopy(actual);value['schubert.batch_runs'].pop(0);cases.append(value)
        value=copy.deepcopy(actual);value['schubert.batch_runs'].append(None);cases.append(value)
        for value in cases:
            with self.assertRaises(ValueError):env['row_oracle'](value)

    def test_actual_generation_source_metadata_and_no_mutations(self):
        text=PAYLOAD;ast.parse(text)
        for required in ['21f20c0cdbe34ce99431a55b10f92285','36458395316',
                         '7dab3e61504949608fabaaac52e024b0','0f751fba26c94b22ac693a839fced07d',
                         'd5b00104280028d9ea81b44c1d1c805f3c2861ed',
                         "UNITS=set(units);FIELDS=set(",
                         "'metadata':a,'sha256':",
                         'require(value==capture())','manager.UnrefUnit(u)']:
            self.assertTrue(required in text)
        self.assertFalse('systemctl start' in text or 'systemctl stop' in text)
        self.assertTrue("'startsStopsConfigDbWrites0':True" in text)
        self.assertTrue("row_oracle(rs)" in text and "original_oracle(durable[kind])" in text)


if __name__=='__main__':unittest.main()
