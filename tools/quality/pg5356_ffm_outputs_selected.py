"""Preowned FFM output buffers and primitive call/release states, same source only."""
import pg5348_manager_session_selected as previous

selected=previous.selected
aliases=previous.aliases
repetitions=previous.repetitions
PREFIX=previous.PREFIX
FILES={'LinuxSystemdSession'}
OUTERS={'LinuxSystemdSession','LinuxSystemdSession$Factory'}
DEBUG={'LinuxSystemdSession$Calls','LinuxSystemdSession$Native','LinuxSystemdSession$Octets'}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return previous.extra_suites()


if __name__=='__main__':
    configure()
    raise SystemExit(selected.main(stem_override='pg5356-ffm-outputs',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions()))
