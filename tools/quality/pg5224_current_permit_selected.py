"""Eight current permit/OS admission scopes, existing33 tests; current809/95 expected."""
import pg5216_root_credential_selected as previous
import pg5200_morning_owner_selected as aliases

selected=previous.selected
PREFIX='batch:dev/codex/schubert/nk/batch/'
OUTERS={'file/RootCurrentPermitPreflight','file/StartupPermitFiles','platform/RootReleaseAdmission'}
DEBUG={'file/RootCurrentPermitPreflight$Observed',
       *{'file/StartupPermitFiles$'+n for n in ('Io','Parts','IssueProof','Revoked','NioIo')},
       *{'platform/RootReleaseAdmission$'+n for n in ('Loader','Platform','OsIo','DatabaseInspection','EffectiveConfigurations','NativeOsIo')}}
PERMIT={f'dev.codex.schubert.nk.batch.{folder}.{name}Test':'batch' for folder,name in (
    ('file','RootCurrentPermitPreflight'),('file','StartupPermitFiles'),('platform','RootReleaseAdmission'))}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**PERMIT}


def main():
    configure()
    return selected.main(stem_override='pg5224-current-permit',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
