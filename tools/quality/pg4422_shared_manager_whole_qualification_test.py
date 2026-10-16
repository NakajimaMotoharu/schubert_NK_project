"""Independent tool-only XML rejection vectors and exact relocation/case contracts."""
import ast
import hashlib
import inspect
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as E
import pg4422_shared_manager_whole_qualification as subject


def classifier():
    tree = ast.parse(inspect.getsource(subject.qualify))
    nodes = [n for n in tree.body[0].body if isinstance(n, ast.FunctionDef) and n.name in {'sha', 'need', 'identities'}]
    if {n.name for n in nodes} != {'sha', 'need', 'identities'}: raise ValueError('exact standalone classifier boundary')
    ns = {'hashlib': hashlib, 'E': E, 'start': 0}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), '<actual XML tool classifier>', 'exec'), ns)
    return ns['identities']


class WholeQualification(unittest.TestCase):
    def test_genuine_single_xml_identity_and_fresh_hash_are_required(self):
        text = '<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase classname="literal.Class" name="literalMethod"/></testsuite>'
        with tempfile.TemporaryDirectory(prefix='pg4422-xml-') as folder:
            path = Path(folder) / 'TEST-literal.xml'; path.write_text(text)
            hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}
            self.assertEqual(({('literal.Class', 'literalMethod')}, 1), classifier()(Path(folder), hashes, True))
            with self.assertRaises(ValueError): classifier()(Path(folder), {path.name: '0' * 64}, True)

    def test_failure_skipped_flaky_duplicates_and_missing_identity_never_become_success(self):
        prefix = '<testsuite tests="1" failures="0" errors="0" skipped="0">'
        good = '<testcase classname="literal.Class" name="literalMethod"/>'
        tails = ['failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError']
        vectors = [prefix + '<testcase classname="literal.Class" name="literalMethod"><' + n + '/></testcase></testsuite>' for n in tails]
        vectors += [prefix.replace('failures="0"', 'failures="1"') + good + '</testsuite>',
                    prefix.replace('tests="1"', 'tests="2"') + good + '</testsuite>',
                    prefix.replace('tests="1"', 'tests="2"') + good + good + '</testsuite>',
                    prefix + '<testcase name="literalMethod"/></testsuite>']
        with tempfile.TemporaryDirectory(prefix='pg4422-negative-') as folder:
            path = Path(folder) / 'TEST-literal.xml'
            for text in vectors:
                with self.subTest(text=text):
                    path.write_text(text); hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}
                    with self.assertRaises(ValueError): classifier()(Path(folder), hashes, True)

    def test_only_two_exact_test_class_aliases_and_four_real_new_methods(self):
        self.assertEqual({
            'dev.codex.schubert.nk.batch.platform.LinuxSystemdQueryTest': 'dev.codex.schubert.nk.bootstrap.SystemManagerObservationTest',
            'dev.codex.schubert.nk.batch.platform.LinuxSystemdSessionTest': 'dev.codex.schubert.nk.bootstrap.LinuxSystemdSessionTest'}, subject.ALIASES)
        self.assertEqual(4, len(set(subject.NEW_CASES)))
        root = subject.ROOT
        for name, method in subject.NEW_CASES:
            path = root / ('src/schubert-nk-bootstrap/src/test/java/' + name.replace('.', '/') + '.java')
            self.assertIn('void ' + method + '(', path.read_text())
        raw = inspect.getsource(subject.qualify)
        for guard in ['len(oldcases) == 3717', 'len(cases) == 3721', 'len(physical) == 1644',
                      "'ADDED_FIXED_ENUM'", "'candidateNativePending': True", "'global100': False"]:
            self.assertIn(guard, raw)


if __name__ == '__main__':
    unittest.main()
