"""One manager session scope; preserve pending UNKNOWN and post-release closed observation."""
import pg5332_service_resources_selected as previous

selected=previous.selected
aliases=previous.aliases
repetitions=previous.repetitions
PREFIX='bootstrap:dev/codex/schubert/nk/bootstrap/'
FILES={'SystemManagerObservation'}
OUTERS=FILES
DEBUG={'SystemManagerObservation$Budget','SystemManagerObservation$Factory','SystemManagerObservation$Owner',
       'SystemManagerObservation$Property','SystemManagerObservation$Service','SystemManagerObservation$Session'}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return previous.extra_suites()


if __name__=='__main__':
    configure()
    raise SystemExit(selected.main(stem_override='pg5348-manager-session',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions()))
