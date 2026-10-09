"""Fixed latest-only recipe, actualpair oracle required, no terminal fallback/union."""
import ast
import unittest
from pg768_sources_test import fixture
from pg769_binding_test import meta
from pg770_closing_native import source


class Test(unittest.TestCase):
    def test_latest_pair_binds_current_and_separate_private_terminal(self):
        raw=source(*fixture(),meta(),'5'*64);tree=ast.parse(raw)
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets));ast.parse(payload)
        for v in ('pg768-bootstrap-existing-v1','pg769-bootstrap-final-v1','pg766-current-eight-native-v1','pg748-closing-six-host-v1',
            'pg770-current-nine-native-v1','NativeClosing746',"'.closing.exec'","'.terminal.exec'",'BOOTSTRAP','terminalIncludedInCounter',"'closingOnlyIncludedInCounter':True",'26cb3b18f8542af5819f1f3a28496a2e3351bed6048fb9ae0fe66ecefa14530c'):self.assertIn(v,raw)
        self.assertIn('streams.append(stream);assert len(streams)==9',raw)
        self.assertNotIn('streams.append(terminal)',raw)
        self.assertLess(raw.index("'NativeClosing746'"),raw.index("'NativeSessions571'"))
        for old in ('pg737','pg738','pg739','pg730','pg713','1ec19782','0d42d02d','2f575a4'):self.assertNotIn(old,raw)

    def test_unknown_eight_manifest_rejected(self):
        for bad in (None,'',True,'F'*64,'a'*63):
            with self.assertRaises(AssertionError):source(*fixture(),meta(),bad)


if __name__=='__main__':unittest.main()
