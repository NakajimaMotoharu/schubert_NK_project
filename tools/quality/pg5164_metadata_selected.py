"""New readonly metadata branch plus its actual related tests; no confirmation replay of536."""
import pg5148_native_fd_selected as selected

EXTRA={'dev.codex.schubert.nk.bootstrap.NativeCoverageExportTest':'bootstrap'}


def main():
    selected.EXTRA_CHANGED={'bootstrap:dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'}
    return selected.main(stem_override='pg5164-readonly-agent',version_override='v1',extra_suites=EXTRA)


if __name__=='__main__':raise SystemExit(main())
