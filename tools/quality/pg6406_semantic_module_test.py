import copy
import hashlib
import json
import subprocess
import unittest
from pyflakes.api import checkPath
import pg6282_current4040_static_join as helper
import pg6406_current4052_static_join as subject


class OriginalModule(unittest.TestCase):
    def test_actual_four_bootstrap_module_api_package_classes(self):
        qp, _ = subject.read_qualified(); cases = json.loads(qp.with_name('cases.json').read_bytes())
        for name in ('ServiceProcessResourcesTest', 'ServiceOwnedReleaseTest', 'ServiceNativeReleaseTest', 'ServiceResourceRetentionTest'):
            cls = 'dev.codex.schubert.nk.api.file.'+name
            actual = [r for r in cases if r['class'] == cls]
            self.assertTrue(actual); self.assertEqual({'bootstrap'}, {r['module'] for r in actual})
            path = 'src/schubert-nk-bootstrap/src/test/java/'+cls.replace('.', '/')+'.java'
            text = subprocess.check_output(['git', 'show', subject.SOURCE+':'+path], cwd=helper.ROOT)
            declarations = [dict(className=cls, sourceSha256=hashlib.sha256(text).hexdigest())]
            seen = []
            def read(request):
                self.assertEqual(path, request); seen.append(request); return text
            refs = helper.declared_class_references(declarations, cases, subject.SOURCE, read)
            self.assertEqual(len(actual), len(refs)); self.assertEqual([path], seen)
            self.assertTrue(all(r['source'] == subject.SOURCE for r in refs))
        for path in (helper.__file__, subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_unknown_ambiguous_module_fails_before_source_read(self):
        text = b'fixed Test source'; cls = 'dev.codex.schubert.nk.api.file.ExampleTest'
        declaration = dict(className=cls, sourceSha256=hashlib.sha256(text).hexdigest())
        case = dict(module='bootstrap', **{'class': cls}, source='a'*40, result='PASS_ORIGINAL_XML',
                    caseNameSha256='b'*64, testId='PT-FIXTURE-001', xmlSha256='c'*64)
        bad = [dict(case, module=None), dict(case, module='other'), dict(case, module='../api')]
        absent = copy.deepcopy(case); del absent['module']; bad.append(absent)
        for row in bad:
            with self.subTest(module=row.get('module')), self.assertRaisesRegex(ValueError, 'original XML module'):
                helper.declared_class_references([declaration], [row], 'a'*40,
                    lambda path: self.fail('invalid module cannot read source'))
        with self.assertRaisesRegex(ValueError, 'original XML module'):
            helper.declared_class_references([declaration], [case, dict(case, module='api', caseNameSha256='d'*64)], 'a'*40,
                lambda path: self.fail('ambiguous module cannot read source'))


if __name__ == '__main__':
    unittest.main()
