import unittest
from pg573_fresh_parent_contract import prior_history, empty_oracle


class Test(unittest.TestCase):
    def test_prior_today_exact_new_run_only(self):
        rows = [{'business_date':'2026-10-07','run_id':'old','status':'SUCCESS'} for _ in range(462)] + [{'business_date':'2026-10-08','run_id':'b7e73994-b951-4696-bdd1-cfbc8a10e734','status':'SUCCESS'} for _ in range(10)]
        self.assertTrue(prior_history(rows, '2026-10-08'))
        for key, bad in [('run_id','foreign'),('status','RUNNING'),('business_date','2026-10-07')]:
            changed = [*rows[:-1], {**rows[-1],key:bad}]
            self.assertFalse(prior_history(changed,'2026-10-08'))
        for bad in (None,[],rows[:-1],[*rows,None]): self.assertFalse(prior_history(bad,'2026-10-08'))
        self.assertFalse(prior_history(rows,None))
        changed=[*rows[:-1],dict(rows[-1])];del changed[-1]['status']
        self.assertFalse(prior_history(changed,'2026-10-08'))

    def test_no_new_cleanup_targets_or_boundary_change(self):
        good={k:[] for k in ('notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references','inbox_scan_candidates')}
        good['web_http_sessions']=[str(n)for n in range(115)]
        self.assertTrue(empty_oracle(good,dict(good)))
        for bad in (None,{},[],{**good,'foreign':[]},{**good,'questions':['unexpected']}):
            self.assertFalse(empty_oracle(good,bad));self.assertFalse(empty_oracle(bad,bad))
        for values in (None,good['web_http_sessions'][:-1],[*good['web_http_sessions'],'116'],['same']*115,[None]*115):
            bad={**good,'web_http_sessions':values};self.assertFalse(empty_oracle(bad,bad))
        self.assertFalse(empty_oracle(None,None))


if __name__ == '__main__': unittest.main()
