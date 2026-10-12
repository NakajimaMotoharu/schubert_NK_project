"""Published exact key-order invariant; no event/value/duplicate normalization."""
import json
import unittest
from pg1765_warning_terminal_capture_v2 import projection_source,payload


class Projection(unittest.TestCase):
    def test_equivalence_and_every_non_equivalent_observation(self):
        env={'json':json};exec(projection_source(),env);project=env['project']
        first=b'{"__CURSOR":"a","_PID":"1","UNIT":"morning"}\n'
        second=b'{"UNIT":"morning","_PID":"1","__CURSOR":"a"}\n'
        self.assertEqual(project(first),project(second))
        self.assertNotEqual(project(first),project(second.replace(b'"1"',b'"2"')))
        for bad in [b'{"__CURSOR":"a","_PID":"1","_PID":"2"}\n',first+first,b'{"__CURSOR":"a","_PID":1}\n',b'{"__CURSOR":"","_PID":"1"}\n']:
            with self.assertRaises(ValueError):project(bad)
        a=first+b'{"__CURSOR":"b","_PID":"1"}\n'
        b=b'{"__CURSOR":"b","_PID":"1"}\n'+first
        self.assertNotEqual(project(a),project(b))

    def test_actual_payload_keeps_both_raw_and_no_completion_claim(self):
        raw=payload();self.assertIn('project(again)==project(journal)',raw)
        self.assertIn('pid1-first.private.jsonl',raw);self.assertIn('pid1-second.private.jsonl',raw)
        self.assertIn("'wholeAccepted':False",raw)


if __name__=='__main__':unittest.main()
