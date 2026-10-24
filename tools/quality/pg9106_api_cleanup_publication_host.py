"""New14/necessary20 current cache PT34 only; repository/pool/RO-attempt fixture outers compile-only."""
import re
import scoped_prometheus_host as run
SOURCE='fa29009e4fdc97effb40e441110102caf46f3926'
COMPILE=run.host.W/'pg9104-api-cleanup-publication-six-compile-v1'
COMPILE_SHA='89b73f7be9b10823da271f53d31e3816b1d74cad616bf2ae07a9b1afe3652da6'
COUNTS={'ApiOutboxCleanupPublicationTest':14,'ApiOutboxObservationSourceTest':20}

if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=COMPILE
    run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg9106-api-cleanup-publication-host-v1'
    run.OUT=run.host.BASE/'PG9106-api-cleanup-publication-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiCleanupPublicationJunitLauncher.java'
    paths={name:run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in COUNTS}
    run.NEW_TEST=paths['ApiOutboxCleanupPublicationTest']
    run.TEST_SOURCE_OVERRIDES={'ApiOutboxObservationSourceTest':paths['ApiOutboxObservationSourceTest']}
    run.EXTRA_TEST_SOURCES=tuple(run.host.ROOT/f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{name}.java' for name in ('DbPoolMetricObservationTest','OutboxObservationRepositoryTest','ApiReadOnlyObservationAttemptTest'))
    run.COUNTS=COUNTS
    run.SESSION_ID='PG9106-API-CLEANUP-PUBLICATION'
    run.FIXTURES={}
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',run.HELPER.read_text(),re.S)
    assert len(selected)==1 and set(re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0]))=={'dev.codex.schubert.nk.api.monitoring.'+name for name in COUNTS}
    for name,path in paths.items():
        prefix='outboxPublish' if name=='ApiOutboxCleanupPublicationTest' else 'outboxSource'
        cases=re.findall(r'void\s+('+prefix+r'\d{3})',path.read_text())
        assert len(cases)==COUNTS[name] and set(cases)=={prefix+str(i).zfill(3) for i in range(1,COUNTS[name]+1)} and path.read_text().count('@Test')==COUNTS[name]
    assert sum(COUNTS.values())==34 and run.SLOT.name.upper()==run.OUT.name.upper()
    run.main()
