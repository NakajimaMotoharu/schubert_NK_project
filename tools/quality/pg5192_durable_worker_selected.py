"""Eight durable/worker ownership scopes, related684 actual cases, no VM action."""
import pg5184_environment_selected as previous

selected=previous.selected
PREFIX=previous.PREFIX
OUTERS={'DurableRecordFiles','BackupWorkerRequestFiles','CleanupWorkerRequestFiles','MorningBackupRequestPublication'}
DEBUG={'MorningBackupRequestPublication$1','MorningBackupRequestPublication$Owner',
       'MorningBackupRequestPublication$Open','MorningBackupRequestPublication$Gate'}
WORKERS={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch' for name in OUTERS}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+name+'.class' for name in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+name+'.class' for name in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**WORKERS}


def main():
    configure()
    return selected.main(stem_override='pg5192-durable-worker-scopes',version_override='v1',
                         extra_suites=extra_suites())


if __name__=='__main__':raise SystemExit(main())
