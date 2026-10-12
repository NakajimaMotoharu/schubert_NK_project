"""Independent count/XML mismatch and actual projection expressions: BUG1140/YKT908."""
import ast
import contextlib
import io
import json
import unittest
import pg1625_unsupported_ports_selected as p3
import pg1626_unsupported_ports_selected as p6
from pg1627_selected_contract_qualification import qualified_tests


class SelectedCountTest(unittest.TestCase):
    def test_actual_projection_uses_qualified_three_or_six(self):
        for module,n in [(p3,3),(p6,6)]:
            statement=next(v for v in ast.parse(module.SERVER).body if isinstance(v,ast.Expr) and isinstance(v.value,ast.Call) and isinstance(v.value.func,ast.Name) and v.value.func.id=='print')
            out=io.StringIO()
            with contextlib.redirect_stdout(out):
                exec(compile(ast.Module(body=[statement],type_ignores=[]),'<actual count projection>','exec'),{'json':json,'result':{'tests':n},'coverage':{},'out':__import__('pathlib').Path('/unused'),'sha':lambda _: 'a'*64})
            value=json.loads(out.getvalue());self.assertEqual(n,value['tests']);self.assertEqual(0,value['actualExit'])

    def test_exact_literal_xml_rejects_every_failed_or_mismatched_claim(self):
        expected={'example.Class:a','example.Class:b','example.Class:c'}
        xml=b'<testsuite tests="3" failures="0" errors="0" skipped="0"><testcase classname="example.Class" name="a"/><testcase classname="example.Class" name="b"/><testcase classname="example.Class" name="c"/></testsuite>'
        m={'tests':3,**{k:0 for k in ['actualExit','failures','errors','skipped','aborted','notRun','javacWarnings','classByteMismatch']}}
        self.assertEqual(3,qualified_tests(m,xml,expected))
        for manifest,oracle in [(None,expected),(m,None),(m,list(expected)),({**m,'actualExit':False},expected)]:
            with self.assertRaises(ValueError):qualified_tests(manifest,xml,oracle)
        for k in m:
            wrong=dict(m);wrong[k]=6 if k=='tests' else 1
            with self.assertRaises(ValueError):qualified_tests(wrong,xml,expected)
        for bad in [xml.replace(b'tests="3"',b'tests="6"'),xml.replace(b'name="b"',b'name="a"'),xml.replace(b'name="b"',b'name="unknown"'),xml.replace(b'name="b"/>',b'name="b"><failure/></testcase>'),xml.replace(b'skipped="0"',b'skipped="1"')]:
            with self.assertRaises(ValueError):qualified_tests(m,bad,expected)


if __name__=='__main__':unittest.main()
