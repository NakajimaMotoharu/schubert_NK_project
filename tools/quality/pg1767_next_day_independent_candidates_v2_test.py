"""Test emitted full dependencies, not only host imported definitions."""
import ast
import unittest
from pg1767_next_day_independent_candidates_v2 import payload


class Emitted(unittest.TestCase):
    def test_actual_generated_full_definition_namespace(self):
        raw=payload();tree=ast.parse(raw)
        nodes=[]
        for n in tree.body:
            if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CUT'for t in n.targets):break
            nodes.append(n)
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual emitted definitions>','exec'),env)
        self.assertEqual('UTC',str(env['instant']('2026-10-12T18:20:32Z').tzinfo))
        rows={n:[]for n in ['schubert.notifications','schubert.questions','schubert.auth_sessions','schubert.login_ip_attempts','schubert_web_session.web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','schubert.app_logs','schubert.batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','schubert_web_session.web_receipt_references','schubert.request_inbox']}
        self.assertTrue(all(v==[]for v in env['candidates'](rows,'2026-10-12T18:20:32Z').values()))
        self.assertEqual([],env['classify_inbox'](rows,[])['protected'])


if __name__=='__main__':unittest.main()
