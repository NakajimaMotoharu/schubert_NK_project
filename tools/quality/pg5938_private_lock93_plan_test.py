import unittest
from unittest.mock import patch
from types import SimpleNamespace
import pg5938_private_lock93_plan as t


class DeclaredPrivateLockTransformTest(unittest.TestCase):
    def test_formatter_stdin_argv_and_nonzero_are_explicit(self):
        with patch.object(t.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='formatted')) as run:
            self.assertEqual('formatted', t.formatted('input'))
            self.assertEqual(['--skip-reflowing-long-strings', '-'], run.call_args.args[0][-2:])
            self.assertEqual('input', run.call_args.kwargs['input'])
            self.assertTrue(run.call_args.kwargs['text'])
        with patch.object(t.subprocess, 'run', return_value=SimpleNamespace(returncode=2)):
            with self.assertRaises(ValueError):
                t.formatted('input')

    def fixture(self, extra=''):
        text = ('final class Fixture {\n'+extra+'  private final Object lock = new Object();\n'
                '  int value(boolean fail) {\n    synchronized (lock) {\n'
                '      if (fail) throw new IllegalStateException("literal");\n      return 7;\n    }\n  }\n}\n')
        utf = lambda pos: len(text[:pos].encode('utf-16-le'))//2
        a = text.index('Object lock'); b = text.index('Object();'); s = text.index('synchronized'); body = text.index('{', s); end = text.index('}', body)+1; expr = text.index('lock)', s)
        field = dict(owner='Fixture', name='lock', eligible=True, serializableOwner=False, superclass='java.lang.Object', otherReads=0,
                     typeStart=utf(a), typeEnd=utf(a+6), initStart=utf(b), initEnd=utf(b+6))
        block = dict(fieldOwner='Fixture', name='lock', parentKind='BLOCK', start=utf(s), end=utf(end), bodyStart=utf(body), bodyEnd=utf(end), expressionStart=utf(expr), expressionEnd=utf(expr+4))
        return text, field, block

    def test_exact_body_unknown_return_and_utf16_input_remain_unchanged(self):
        for extra in ('', '  // 😀 independent offset fixture\n'):
            text, field, block = self.fixture(extra)
            result = t.transform(text, [field], [block])
            self.assertIn('private final '+t.FQ+' lock = new '+t.FQ+'();', result)
            self.assertIn('lock.lock();\n    try {\n      if (fail) throw new IllegalStateException("literal");\n      return 7;\n    } finally {\n      lock.unlock();\n    }', result)
            self.assertEqual(1, result.count('lock.lock();')); self.assertEqual(1, result.count('lock.unlock();'))
            self.assertNotIn('synchronized', result)

    def test_unsafe_parent_serialization_alias_or_header_never_transforms(self):
        text, field, block = self.fixture()
        for bad in (dict(field, serializableOwner=True), dict(field, otherReads=1), dict(field, superclass='UnknownParent')):
            with self.assertRaises(ValueError):
                t.transform(text, [bad], [block])
        with self.assertRaises(ValueError):
            t.transform(text, [field], [dict(block, parentKind='IF')])
        with self.assertRaises(ValueError):
            t.transform(text.replace('synchronized', 'otherkeyword'), [field], [block])


if __name__ == '__main__':
    unittest.main()
