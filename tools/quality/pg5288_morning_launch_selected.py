"""Seven Directory owners; two DB anonymous classes semantic, outer classes method-equivalence only."""
import pg5280_morning_execution_selected as previous

selected=previous.selected
aliases=previous.aliases
PREFIX=previous.PREFIX
FILES={'MorningNewRunAdmission','MorningResumeAdmission','MorningStartupLaunchOwner','MorningProcessMain'}
OUTERS={'MorningNewRunAdmission$1','MorningResumeAdmission$1','MorningStartupLaunchOwner','MorningProcessMain'}
DEBUG={'MorningNewRunAdmission','MorningNewRunAdmission$2','MorningNewRunAdmission$2$1','MorningNewRunAdmission$3',
       'MorningNewRunAdmission$Continuation','MorningNewRunAdmission$Database','MorningNewRunAdmission$DatabaseWork',
       'MorningNewRunAdmission$FileWork','MorningNewRunAdmission$Files','MorningNewRunAdmission$Gate',
       'MorningNewRunAdmission$OriginalFiles','MorningNewRunAdmission$OriginalProof','MorningNewRunAdmission$Originals',
       'MorningNewRunAdmission$OwnedContinuation','MorningNewRunAdmission$VerifiedContinuation','MorningProcessMain$1',
       'MorningProcessMain$Admission','MorningProcessMain$Archive','MorningProcessMain$CompletedAdmission',
       'MorningProcessMain$ResumeAdmission','MorningProcessMain$VerifiedArchive','MorningResumeAdmission',
       'MorningResumeAdmission$2','MorningResumeAdmission$2$1','MorningResumeAdmission$Database',
       'MorningResumeAdmission$DatabaseWork','MorningResumeAdmission$FileWork','MorningResumeAdmission$Files',
       'MorningResumeAdmission$Gate','MorningResumeAdmission$Originals','MorningStartupLaunchOwner$ApiRetained',
       'MorningStartupLaunchOwner$Completion','MorningStartupLaunchOwner$CompletionPhase','MorningStartupLaunchOwner$CompletionProgress',
       'MorningStartupLaunchOwner$CompletionRetirement','MorningStartupLaunchOwner$Launch','MorningStartupLaunchOwner$Started',
       'MorningStartupLaunchOwner$Stop'}
RELATED={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch' for name in
    ('MorningNewRunAdmission','MorningResumeAdmission','MorningStartupLaunchOwner','MorningStartupLaunchOwnerAdmission','MorningProcessMain')}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5288-morning-launch',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
