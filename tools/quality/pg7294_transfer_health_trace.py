"""Current42 from169 cases, all61 source/53 physical trace, old byte witnesses remain historical."""
import pg7160_filesystem_health_trace as trace

if __name__=='__main__':
    trace.OUT=trace.host.BASE/'PG7294-transfer-health-trace-v1'
    trace.SOURCE='74371ae0b185cee42e9b6930d68e34522640c2d6'
    trace.SOURCE_COUNT=61;trace.PREVIOUS_COUNT=59;trace.CURRENT_TESTS=169;trace.CURRENT_SUITES=23
    trace.CURRENT_EXECUTABLE=42;trace.ADDED_PHYSICAL=53;trace.REPORTS=(1620,1621)
    trace.NEW_SPEC=1619;trace.NEW_TEST_IDS='TRANSFERCONN001..008';trace.NEW_SS='341,351'
    trace.ALLOWED_NEW_NAMES={'TransferHealthMonitor.java','TransferHealthMonitorTest.java'}
    trace.EDITED_EXISTING=set();trace.EXTRA_SPECS={};trace.EXTRA_TEST_IDS={}
    trace.PINS['physical']=('PG7292-transfer-health-six-post-v1/manifest.json','47ce5233888b5518fd0dc683dfbf29b8429a75adbc3439c4825d581ad12202ce')
    trace.PINS['currentBatch']=('PG7288-transfer-health-post-v1/manifest.json','afac4559457cc1b93b359da1193d34d08558a868cf0513f5b2d9045a9d64da70')
    trace.PINS['previousTrace']=('PG7280-transfer-metric-trace-v2/manifest.json','1975ccbc56108eff443fc9e3e067ae4440843e55e57edf4ad342c7a6d22fcdd3')
    trace.main()
