"""Same physical Main as PG5364, plus independently specified positive authentication progress."""
import pg5356_ffm_outputs_selected as previous

selected=previous.selected
aliases=previous.aliases
repetitions=previous.repetitions
PREFIX=previous.PREFIX
FILES=previous.FILES
OUTERS=previous.OUTERS
DEBUG=previous.DEBUG
configure=previous.configure
extra_suites=previous.extra_suites


if __name__=='__main__':
    configure()
    raise SystemExit(selected.main(stem_override='pg5372-ffm-progress',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions()))
