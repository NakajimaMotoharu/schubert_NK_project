"""Independent exact expected marker versus both actual emitted producer/consumer."""
import ast
import re
import unittest
from pg1872_warning_ro_marker_sources import sources


class Marker(unittest.TestCase):
    def test_real_python_print_and_java_ascii_consumer_match_independent_bytes(self):
        s=sources('b'*64,'c'*64);py=s['pg1872_input_preflight.py'];java=s['Pg1872CandidateRo.java']
        expected=b'PG1872_INPUT_CLOSURE_READY\n'
        calls=[n for n in ast.walk(ast.parse(py))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='print']
        self.assertEqual(1,len(calls));self.assertEqual(expected,(ast.literal_eval(calls[0].args[0])+'\n').encode('ascii'))
        match=re.findall(r'"(PG[0-9]+_INPUT_CLOSURE_READY\\n)"\.getBytes\(StandardCharsets.US_ASCII\)',java)
        self.assertEqual(1,len(match));self.assertEqual(expected,match[0].replace('\\n','\n').encode('ascii'))
        self.assertNotIn('PG1681_INPUT_CLOSURE_READY',py)
        self.assertIn('pg1874-warning-candidate-host-ro-v1',java)
        self.assertIn('4148e3e8-f107-431a-ab27-d6e6d1f1772e',java)


if __name__=='__main__':unittest.main()
