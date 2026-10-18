"""Eighteen durable run scopes with existing63 tests, current-source751/89 expected."""
import pg5200_morning_owner_selected as previous

selected=previous.selected
PREFIX='batch:dev/codex/schubert/nk/batch/file/'
OUTERS={'MaintenanceRunFiles','MaintenanceRunFiles$Session'}
DEBUG={f'MaintenanceRunFiles${name}' for name in (
    'Digests','Operation','Work','Decoder','Io','StartupOriginal','Mutation','Inventory','CapturedFile','Graph','NioIo')}
RUNS={f'dev.codex.schubert.nk.batch.{folder}.{name}Test':'batch' for folder,name in (
    ('file','MaintenanceRunFiles'),('file','MaintenanceRecords'),('file','MaintenanceRetirementRecords'),
    ('repository','RunReferenceRepository'))}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RUNS}


def main():
    configure()
    return selected.main(stem_override='pg5208-maintenance-run',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=previous.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
