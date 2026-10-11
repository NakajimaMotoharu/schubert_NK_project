"""Actual generated current baseline boundary, pure host test."""
import unittest
import pg1344_bootstrap_before as p

class Test(unittest.TestCase):
    def test_complete_sent_payload(self):
        seals = dict.fromkeys(p.previous.previous.transport.previous.SEALS, 'b' * 64)
        raw = p.payload(seals)
        compile(raw, '<independent current baseline fixture>', 'exec')
        for required in ("'parentPid1':receipt_rows", "'oldProofs':tree(root)",
                         "result['batchRows']", 'dependency_graph(raw_dependencies,UNITS)',
                         'pg1344-current-bootstrap-before-v1', '769ddb15cd735c25fef581b5f9850ef9d0053c0f'):
            self.assertIn(required, raw)
        for old in ('PG1340-published-terminal-post-v4', 'pg1340-published-terminal-post-v4'):
            self.assertNotIn(old, raw)
        self.assertIn("pg1336-stop-v1.exit", p.source())
        self.assertIn("pg1335-frozen-v1.safe.json", p.source())

if __name__ == '__main__':
    unittest.main()
