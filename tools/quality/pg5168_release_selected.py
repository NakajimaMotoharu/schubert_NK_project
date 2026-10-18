"""Sixteen immutable-release scopes, all42 bootstrap suites including new metadata case."""
import pg5156_native_coverage_selected as bootstrap

selected=bootstrap.selected
PREFIX='bootstrap:dev/codex/schubert/nk/bootstrap/'
OUTERS={'NativeCoveragePrivateFile','ReleasePayloadVerification','StartupReleaseManifest'}
DEBUG={'StartupReleaseManifest$ManifestValue','StartupReleaseManifest$Snapshot','StartupReleaseManifest$NioIo'}


def configure():
    selected.EXTRA_CHANGED={PREFIX+name+'.class' for name in OUTERS}
    selected.EXTRA_DEBUG={PREFIX+name+'.class' for name in DEBUG}


def main():
    configure()
    return selected.main(stem_override='pg5168-release-scopes',version_override='v1',
                         extra_suites=bootstrap.bootstrap_suites())


if __name__=='__main__':raise SystemExit(main())
