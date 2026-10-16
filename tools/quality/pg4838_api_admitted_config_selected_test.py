import ast
import unittest
import pg4838_api_admitted_config_selected as role


class ActualBoundaries(unittest.TestCase):
    def test_real_selection_and_missing_coverage_fail_closed(self):
        raw=role.source();tree=ast.parse(raw)
        self.assertIn('-DfailIfNoTests=false',raw)
        self.assertIn('every selected suite requires explicit nonempty methods',raw)
        self.assertIn('target coverage absent; not executed or failed, never accepted',raw)
        self.assertIn('selected identity inventory differs',raw)
        self.assertIn("'actualMavenExit': code",raw)
        guards=[n for n in ast.walk(tree)if isinstance(n,ast.If)and isinstance(n.test,ast.Call)and isinstance(n.test.func,ast.Attribute)and n.test.func.attr=='exists']
        self.assertEqual(2,len(guards))
        target=next(n for n in guards if '/schubert-nk-api' in ast.unparse(n.test)or 'src/schubert-nk-api' in ast.unparse(n.test))
        self.assertIn('ET.parse',ast.unparse(target))
        self.assertIn('reasons.append',ast.unparse(target.orelse[0]))
        self.assertIn("code == 0 and (not reasons)",raw)


if __name__=='__main__':unittest.main()
