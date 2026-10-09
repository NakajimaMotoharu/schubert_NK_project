"""Literal exact748 provenance and whitelist boundary, no publication/VM authority."""
import ast
import unittest
from pg763_public_full import source


class Test(unittest.TestCase):
    def test_exact_source_receipt_and_spec(self):
        raw=source();ast.parse(raw)
        for value in ('pg748-closing-six-host-v1','PG748-full-public-v1','(3513, 519, 1616)',
            'd4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e',
            '588_PG746_748_closing資格・全6回帰仕様.md'):self.assertIn(value,raw)
        for old in ('pg713','PG713','3502','5f6a570'):self.assertNotIn(old,raw)

    def test_literal_public_keys_no_private_native(self):
        raw=source();tree=ast.parse(raw)
        keys=next(ast.literal_eval(n.value)for n in ast.walk(tree)if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name)and t.id=='keys'for t in n.targets))
        self.assertEqual(('actualExit','run','candidateSource','collectorOperator','installedVmSource','candidateNotDeployed',
            'sourceQualification','tests','suites','mainClasses','allMainBytesEqualSelectedCandidate','FESFlakyNotRunIndicators','staticModules','staticIssues'),keys)
        for bad in ('sessionId','cookie','password','rows','backup','native'):
            self.assertNotIn(bad,keys)


if __name__=='__main__':unittest.main()
