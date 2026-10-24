"""New cross-role SS schema6/1, source4950 unchanged; no build/baseline/role28 replay."""
import scoped_prometheus_host as run

SOURCE = '4950b3daf1632ed9f57c3ca42276532b24204745'
COMPILE = run.host.W / 'pg8504-web-batch-jvm-six-compile-v1'
COMPILE_SHA = '3e19a0703f8b845bdf71d7e7d78fdb73733528103acad510a69ba65b4652cf8e'
COUNTS = {'MetricCatalogRoleJoinTest': 6}

if __name__ == '__main__':
    run.require(run.host.sha(run.host.ROOT / 'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md') == '9da7c4e4f24740e031f37f984ec562d56e14ff098b1433af3ec55fe15bd195e6', 'frozen independent approved SS351 source')
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8516-metric-role-join-host-v1'
    run.OUT = run.host.BASE / 'PG8516-metric-role-join-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/MetricCatalogRoleJoinJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/MetricCatalogRoleJoinTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8516-METRIC-ROLE-JOIN'
    run.FIXTURES = {}
    run.main()

