"""Literal stage profile/archive boundary; no native operation."""
import ast
import unittest
import pg686_stage_candidate as p


class BindingTest(unittest.TestCase):
    def test_exact_old_new_stage_and_no_startup(self):
        raw = p.source(); compile(raw, '<new candidate stage>', 'exec')
        env = {}
        for n in ast.parse(raw).body:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('SOURCE','DIGEST','PAYLOAD') for t in n.targets):
                exec(compile(ast.Module(body=[n], type_ignores=[]), '<literal constants>', 'exec'), env)
        self.assertEqual('9bd50536f692610036a0ed8b83e0a8b35fe2a66f', env['SOURCE'])
        self.assertEqual('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480', env['DIGEST'])
        payload = env['PAYLOAD']; compile(payload, '<unused candidate payload>', 'exec')
        for text in ('/releases/0.1.0-PG631', '/releases/0.1.0-PG682',
                     '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe',
                     'group==986', 'signatureVerified=true', 'assert protected()==before',
                     'before=protected();assert before==protected()', 'len(rows)==24', "==514"):
            self.assertIn(text, payload)
        self.assertIn('pg682-release-v1', raw); self.assertIn('pg682-manifest-v1.sig', raw)
        for forbidden in ('systemctl start', 'systemctl stop', 'daemon-reload', 'os.replace(', 'DELETE FROM', 'INSERT INTO'):
            self.assertNotIn(forbidden, payload)


if __name__ == '__main__':
    unittest.main()
