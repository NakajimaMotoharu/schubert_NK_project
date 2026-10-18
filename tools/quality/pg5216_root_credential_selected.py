"""Eleven Root approval/credential scopes, existing25 independent tests,776/92 expected."""
import pg5208_maintenance_run_selected as previous

selected=previous.selected
PREFIX=previous.PREFIX
OUTERS={'RootReleaseApprovalReader','RootServiceCredentialSource','RootBatchCredentialReader'}
DEBUG={'RootReleaseApprovalReader$Operation','RootReleaseApprovalReader$Gate','RootReleaseApprovalReader$Io',
       'RootReleaseApprovalReader$NativeIo','RootBatchCredentialReader$Io','RootBatchCredentialReader$NativeIo',
       'RootServiceCredentialSource$Work','RootServiceCredentialSource$1'}
CREDENTIALS={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch' for name in OUTERS}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**CREDENTIALS}


def main():
    configure()
    return selected.main(stem_override='pg5216-root-credential',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=previous.previous.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
