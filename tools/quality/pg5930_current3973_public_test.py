import hashlib
import unittest
import pg5930_current3973_public as t


class OriginalCurrentProjectionTest(unittest.TestCase):
    def test_payload_and_terminal_identity_mapping_do_not_execute_tests(self):
        raw = t.payload({})
        self.assertIn('PG5926', raw); self.assertNotIn('PG5886', raw); self.assertNotIn('Popen', raw)
        cases = [dict(klass='fixture', **{'class': 'fixture'}, caseNameSha256=hashlib.sha256(('term'+str(i)).encode()).hexdigest(), testId='actual'+str(i), xmlSha256='a'*64, result='PASS_ORIGINAL_XML') for i in range(1, 7)]
        design = [dict(klass='fixture', **{'class': 'fixture'}, method='term'+str(i), designTestId='PT-JMS-TERM'+str(i).zfill(3)) for i in range(1, 7)]
        self.assertEqual(6, len(t.terminal_trace(cases, design)))
        for bad in (cases[:-1], cases+[cases[0]], [dict(r, result='UNKNOWN') for r in cases]):
            with self.assertRaises(ValueError):
                t.terminal_trace(bad, design)


if __name__ == '__main__':
    unittest.main()
