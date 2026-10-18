"""Four original permit scopes, three internal handoffs and two extra intent factories."""
import pg5296_handoff_selected as previous

selected=previous.selected
aliases=previous.aliases
PREFIX='batch:dev/codex/schubert/nk/batch/file/'
FILES={'MorningPermitPublication'}
EXTRA_FACTORY_FILES={'BackupStartIntentFiles'}
OUTERS=FILES|EXTRA_FACTORY_FILES
DEBUG={'MorningPermitPublication$Retain','MorningPermitPublication$OpenIntent','MorningPermitPublication$Store',
       'MorningPermitPublication$Gate','MorningPermitPublication$Intents','MorningPermitPublication$1',
       'MorningPermitPublication$2','MorningPermitPublication$OpenStore','BackupStartIntentFiles$Intent','BackupStartIntentFiles$Gate'}
RELATED={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch' for name in
    ('BackupStartIntentFiles','RootFailedStartPairRecovery','StartupPermitFiles','MorningCompletedMain')}


def repetitions():
    return {'dev.codex.schubert.nk.batch.file.BackupStartIntentFilesTest':
        {'concurrentDistinctOwnersCannotPublishTwoIntents':10}}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5304-permit-intent',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions())


if __name__=='__main__':raise SystemExit(main())
