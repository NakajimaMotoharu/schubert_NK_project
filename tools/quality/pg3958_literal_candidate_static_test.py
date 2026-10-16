"""Pinned analyzer source/closure and no premature receipt or legacy candidate gate."""
import inspect
import unittest
from pyflakes.api import check
import pg3958_literal_candidate_static as static


class LiteralAnalyzers(unittest.TestCase):
    def test_complete_source_and_no_intermediate_manifest(self):
        source = 'INPUT={}\n' + inspect.getsource(static.require) + '\n' + static.pmd_source() + '\n' + inspect.getsource(static.server) + '\nserver(INPUT)\n'
        self.assertEqual(0, check(source, '<actual all849 fixed candidate static namespace>'))
        compile(source, '<actual all849 fixed static>', 'exec')
        self.assertNotIn("(out/'manifest.safe.json').write_text", static.pmd_source())
        self.assertIn('return value', static.pmd_source())
        for flag in ['recordOverlaySha256', 'auxJarSha256', 'pinnedToolSha256', 'ruleSha256']:
            self.assertIn(flag, static.pmd_source())

    def test_exact_allowed_delta_zero_checkstyle_and_unapplied_identity(self):
        source = inspect.getsource(static.server)
        for expected in ["{'AvoidDuplicateLiterals': -187}", "== 1653", "'proposedConstants'] == proof['requestedFindings'] == 187", "checked.returncode == 0 and not findings", 'candidateGitSource=None', 'mainApplied=False', 'F03Accepted=False']:
            self.assertIn(expected, source)


if __name__ == '__main__':
    unittest.main()
