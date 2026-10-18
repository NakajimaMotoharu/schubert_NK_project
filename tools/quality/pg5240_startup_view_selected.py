"""Primitive admission ViewOwner: existing9 plus new8 independent cases; current829/98 expected."""
import pg5232_caddy_child_selected as previous

selected=previous.selected
PREFIX='batch:dev/codex/schubert/nk/batch/file/'
OUTERS={'StartupAdmissionFile','StartupAdmissionFile$ViewOwner'}
DEBUG={'StartupAdmissionFile$'+n for n in ('Io','Admission','AdmittedOperation','ViewOperation','Identity','Snapshot','NioIo')}
VIEW={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch'
      for name in ('StartupAdmissionFile','StartupAdmissionViewOwner')}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**VIEW}


def main():
    configure()
    return selected.main(stem_override='pg5240-startup-view-owner',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=previous.previous.aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
