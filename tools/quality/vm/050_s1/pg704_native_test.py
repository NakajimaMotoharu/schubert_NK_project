"""BOOT704001 independent role/invocation/time/type session vectors and join pins."""
import ast
import hashlib
import unittest
from pg704_native import source

env = {'__file__': __file__}; exec(compile(source(), '<inert current native>', 'exec'), env)


class Test(unittest.TestCase):
    def test_session_vectors(self):
        valid = env['session_valid']; bounds = {'lowerMs': 1000, 'upperMs': 2000}
        value = {'sessions': 1, 'sessionIdSha256': hashlib.sha256(b'BOOTSTRAP-d420de6553ef48038a40332c37a8b12e-ordinary').hexdigest(), 'startMs': 1000, 'dumpMs': 2000}
        self.assertTrue(valid(value, bounds))
        for key, bad in ({'sessions': True, 'sessionIdSha256': hashlib.sha256(b'API-d420de6553ef48038a40332c37a8b12e-ordinary').hexdigest(), 'startMs': 999, 'dumpMs': 2001}).items():
            self.assertFalse(valid({**value, key: bad}, bounds))
        for key in value:
            bad = dict(value); del bad[key]; self.assertFalse(valid(bad, bounds))
        for bad in (None, {**value, 'dumpMs': 999}): self.assertFalse(valid(bad, bounds))

    def test_only_current_source_and_genuine_post(self):
        raw = source(); ast.parse(raw)
        for literal in ('pg703-bootstrap-final-v4', 'pg680-owner-six-host-v1', 'pg698-current-eight-native-v1',
                        'streams.append(stream);assert len(streams)==9', 'classByteMismatch',
                        "'qualifiedSingleSessions':9", "'otherSourceStreamsImported':False"):
            self.assertIn(literal, raw)
        for old in ('pg658', 'pg644', 'pg657', 'pg630', '36fe7a0b', '65bfe1da', 'second', '==514'):
            self.assertNotIn(old, raw)
        self.assertEqual(env['SOURCE'], '9bd50536f692610036a0ed8b83e0a8b35fe2a66f')


if __name__ == '__main__': unittest.main()
