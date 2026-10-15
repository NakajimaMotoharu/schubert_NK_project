"""Independent member-map mismatch oracle and no-guest admission checks."""
import ast
import unittest
from pg3032_same_a9_two_activation_join import payload


class Join(unittest.TestCase):
    def test_complete_payload_and_all_members(self):
        raw = payload()
        ast.parse(raw)
        for required in ['PG2934-native-v1', 'PG3030-native-v1', 'PG3026-six-v1', 'main_count==1643 and resource_count==79', 'full[\'tests\']==3685', 'len(streams)==18', "len({s['sessionIdSha256']for s in sessions})==18", "if not n.endswith('/')", 'NativePointDominance', 'NativeSessions571']:
            self.assertIn(required, raw)
        for forbidden in ['PG2284', 'PG2384', 'PG2300', '04207efc', '0fd734', 'systemctl', 'daemon-reload']:
            self.assertNotIn(forbidden, raw)
        tree = ast.parse(raw)
        expr = next(n.args[0] for n in ast.walk(tree) if isinstance(n, ast.Call) and ast.get_source_segment(raw, n) == 'require(images[0]==images[1])')
        code = compile(ast.Expression(expr), '<independent member equality>', 'eval')
        base = {'A.class': 'class', 'META-INF/MANIFEST.MF': 'resource'}
        for candidate, expected in [(base, True), ({'A.class': 'foreign', 'META-INF/MANIFEST.MF': 'resource'}, False), ({'A.class': 'class'}, False), ({**base, 'extra': 'foreign'}, False), ({**base, 'META-INF/MANIFEST.MF': 'foreign'}, False)]:
            self.assertEqual(expected, eval(code, {'images': [base, candidate]}))


if __name__ == '__main__':
    unittest.main()
