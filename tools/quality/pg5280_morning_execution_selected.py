"""Seventeen Morning Directory owners; nested Completion is a semantic target, not debug."""
import pg5272_cleanup_factory_selected as previous

selected=previous.selected
aliases=previous.aliases
PREFIX=previous.PREFIX
FILES={'MorningStartupRoots','MorningControlScope','MorningCurrentInvalidation','MorningExpiryExecution',
       'MorningCleanupExecution','MorningBrokerExecution'}
OUTERS=FILES|{'MorningBrokerExecution$Completion'}
DEBUG={'MorningBrokerExecution$ExpectedCurrent','MorningBrokerExecution$Observations','MorningCleanupExecution$Completion',
       'MorningControlScope$1','MorningControlScope$2','MorningControlScope$3','MorningControlScope$4','MorningControlScope$5',
       'MorningControlScope$AfterPublication','MorningControlScope$EpochInvalidation','MorningControlScope$Exclusive',
       'MorningControlScope$Gate','MorningControlScope$IntentClear','MorningControlScope$Invalidation',
       'MorningControlScope$Original','MorningControlScope$OwnedEpochWork','MorningControlScope$OwnedOriginal',
       'MorningControlScope$StartupExclusive','MorningControlScope$StopPass','MorningControlScope$Terminals',
       'MorningControlScope$VerifiedEpochWork','MorningCurrentInvalidation$1','MorningCurrentInvalidation$Gate',
       'MorningCurrentInvalidation$Store','MorningStartupRoots$Entry','MorningStartupRoots$Gate',
       'MorningStartupRoots$Observation','MorningStartupRoots$Profile','MorningStartupRoots$Profiles'}
RELATED={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch' for name in
    ('MorningBackupStage','MorningCleanupCompletion','MorningCompletedMain','MorningCompletionEvidence',
     'MorningControlScope','MorningCurrentInvalidation','MorningPrestartEvidence','MorningResumeAdmission',
     'MorningStartupRoots','StartupPermitFiles')}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5280-morning-execution',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
