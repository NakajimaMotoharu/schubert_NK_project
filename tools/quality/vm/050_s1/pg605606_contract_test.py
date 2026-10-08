"""Independent literals for the new day/source fixture. No VM operations."""
import ast
from pathlib import Path
import unittest
from pg605_fresh_parent_contract import prior_history, empty_oracle, invalid_epoch

R=Path(__file__).resolve().parent


class Test(unittest.TestCase):
    def test_day9_prior482_not_old_today10(self):
        rows=[{'business_date':'2026-10-08','run_id':'prior','status':'SUCCESS'} for _ in range(482)]
        self.assertTrue(prior_history(rows,'2026-10-09'))
        for bad in (None,[],rows[:-1],[*rows,None],[*rows[:-1],{}],
                    [*rows[:-1],{**rows[-1],'business_date':'2026-10-09'}]):
            self.assertFalse(prior_history(bad,'2026-10-09'))
        for day in (None,False,'2026-10-08','2026-10-10'):
            self.assertFalse(prior_history(rows,day))

    def test_literal229_only_stable_admission_bounds(self):
        good={k:[] for k in ('notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions',
            'schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','batch_runs',
            'schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references','inbox_scan_candidates')}
        good['web_http_sessions']=[str(i) for i in range(229)]
        self.assertTrue(empty_oracle(good,dict(good)))
        for bad in (None,{},[],{**good,'foreign':[]},{**good,'questions':['unexpected']},
                    {**good,'web_http_sessions':None},{**good,'web_http_sessions':[None]*229},
                    {**good,'web_http_sessions':['same']*229},
                    {**good,'web_http_sessions':good['web_http_sessions'][:-1]},
                    {**good,'web_http_sessions':good['web_http_sessions']+['230']}):
            self.assertFalse(empty_oracle(good,bad)); self.assertFalse(empty_oracle(bad,bad))

    def test_invalid_epoch_is_not_old_permit(self):
        good=(b'NKEPOCH1\nstate=INVALID\nboot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441\n'
              b'epoch_id=aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee\n'
              b'run_id=b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e\ncutoff_utc=2026-10-08T07:36:21.802335Z\n'
              b'activation_id=57f0e73d-d334-4882-9284-04246011da54\npermit_sha256=-\n')
        self.assertTrue(invalid_epoch(good))
        for bad in (None,'text',b'',good[:-1],good+b'unknown=x\n',good.replace(b'INVALID',b'ISSUED'),
                    good.replace(b'permit_sha256=-',b'permit_sha256='+b'1'*64),
                    good.replace(b'4ccc',b'1ccc'),good.replace(b'2026-10-08T07:36',b'2026-10-09T07:36'),
                    good.replace(b'cc9ed874',b'00000000'),good.replace(b'NKEPOCH1',b'\xff')):
            self.assertFalse(invalid_epoch(bad))

    def test_fixed_source_new_only_one_start_and_readonly_observer(self):
        parent=(R/'pg605_fresh_parent.py').read_text()
        parsed=ast.parse(parent)
        values={t.id:ast.literal_eval(n.value) for n in parsed.body if isinstance(n,ast.Assign)
                for t in n.targets if isinstance(t,ast.Name) and t.id in ('SOURCE','DIGEST','PAYLOAD')}
        self.assertEqual(values['SOURCE'],'23b14a44b10504172e030bbd6625926bf049fb5c')
        self.assertEqual(values['DIGEST'],'a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f')
        payload=values['PAYLOAD']; ast.parse(payload)
        start="['systemctl','start','--no-block','schubert-nk-morning-controller.service']"
        self.assertEqual(payload.count(start),1)
        self.assertLess(payload.index("persist('external-start-guard.private.json'"),payload.index(start))
        self.assertIn("'originalBudgetSeconds':1800",payload)
        self.assertIn("now()+interval '2 minutes'",payload)
        self.assertIn("datetime.datetime.fromisoformat(before['bounds']['upper'])",payload)
        self.assertIn('pg605-fresh-parent-v2',payload)
        self.assertIn("'--resume'not in execstart",payload)
        self.assertIn("'priorBatchRows':482",payload)
        self.assertIn('pg604-completed-activate-v1/after.private.json',payload)
        self.assertIn('8d0c96f44c0fadbaac91bcc7f67463ca8f28d26ecfc8dec8eee7a7fa99153ee8',payload)
        self.assertIn('pg606-observer-v1.started',parent)
        watch=(R/'pg606_watch_parent.py').read_text()
        self.assertEqual(watch,(R/'pg554_watch_parent.py').read_text().replace('PG548','PG600'))
        ast.parse(watch)
        observer=(R/'pg606_observer.py').read_text(); ast.parse(observer)
        self.assertIn('/pg606_watch_parent.py ',observer); self.assertIn(' PG600',observer)
        self.assertNotIn('PG548',parent+observer+watch)
        self.assertNotIn('systemctl stop',watch)


if __name__=='__main__': unittest.main()
