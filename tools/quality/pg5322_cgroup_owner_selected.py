"""Primitive six-FD FIFO owner, eight new independent cases and existing ten termination cases."""
import pg5314_readiness_stream_selected as previous

selected=previous.selected
aliases=previous.aliases
PREFIX=previous.PREFIX
FILES={'FixedUnitCgroupNamespace'}
OUTERS=FILES|{'FixedUnitCgroupNamespace$Owner'}
DEBUG={'FixedUnitCgroupNamespace$Context','FixedUnitCgroupNamespace$Io',
       'FixedUnitCgroupNamespace$Identity','FixedUnitCgroupNamespace$Snapshot'}
RELATED={f'dev.codex.schubert.nk.batch.platform.{name}Test':'batch' for name in
    ('CgroupPrimitiveOwner','MaintenanceUnitTermination')}
repetitions=previous.repetitions


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5322-cgroup-owner',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions())


if __name__=='__main__':raise SystemExit(main())
