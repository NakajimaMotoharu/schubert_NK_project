import unittest
import pg5168_release_selected as role


class ReleaseScope(unittest.TestCase):
    def test_changed_and_debug_boundaries_are_exact_and_full_bootstrap_stays_selected(self):
        role.configure()
        self.assertEqual(role.selected.EXTRA_CHANGED,{
            'bootstrap:dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class',
            'bootstrap:dev/codex/schubert/nk/bootstrap/ReleasePayloadVerification.class',
            'bootstrap:dev/codex/schubert/nk/bootstrap/StartupReleaseManifest.class'})
        self.assertEqual(role.selected.EXTRA_DEBUG,{
            'bootstrap:dev/codex/schubert/nk/bootstrap/StartupReleaseManifest$ManifestValue.class',
            'bootstrap:dev/codex/schubert/nk/bootstrap/StartupReleaseManifest$Snapshot.class',
            'bootstrap:dev/codex/schubert/nk/bootstrap/StartupReleaseManifest$NioIo.class'})
        self.assertEqual(len(role.bootstrap.bootstrap_suites()),42)


if __name__=='__main__':unittest.main()
