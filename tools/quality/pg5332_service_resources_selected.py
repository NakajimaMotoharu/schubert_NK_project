"""Service resource ports before acquisition, retaining UNKNOWN and source password erasure."""
import pg5322_cgroup_owner_selected as previous
import pg5156_native_coverage_selected as bootstrap

selected=previous.selected
aliases=previous.aliases
repetitions=previous.repetitions
PREFIX='bootstrap:dev/codex/schubert/nk/api/file/'
FILES={'ServiceProcessResources'}
OUTERS=FILES
DEBUG=set()
RELATED={'dev.codex.schubert.nk.api.file.ServiceOwnedReleaseTest':'bootstrap'}


def configure():
    previous.configure()
    bootstrap.EXTRA_BOOTSTRAP_SUITES=set(RELATED)
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5332-service-resources',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions())


if __name__=='__main__':raise SystemExit(main())
