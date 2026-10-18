"""Three readiness streams plus six independent nullable-response cases; exact repeated10 retained."""
import pg5304_permit_intent_selected as previous

selected=previous.selected
aliases=previous.aliases
PREFIX='batch:dev/codex/schubert/nk/batch/platform/'
FILES={'MorningCaddyReadiness','MorningServiceReadiness'}
OUTERS={'MorningCaddyReadiness','MorningCaddyReadiness$NativeIo','MorningServiceReadiness$NativeIo'}
DEBUG={'MorningCaddyReadiness$Guard','MorningCaddyReadiness$Io','MorningServiceReadiness',
       'MorningServiceReadiness$1','MorningServiceReadiness$Guard','MorningServiceReadiness$Io','MorningServiceReadiness$Response'}
RELATED={f'dev.codex.schubert.nk.batch.platform.{name}Test':'batch' for name in
    ('MorningCaddyReadiness','MorningServiceReadiness','MorningServiceReadinessNative')}
repetitions=previous.repetitions


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5314-readiness-stream',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions())


if __name__=='__main__':raise SystemExit(main())
