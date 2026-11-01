"""Pure metadata qualification of scoped own-loopback declarations and unchanged runner gates."""
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_owned_mvc_loopback_host_v1 as helper
OUT=data.BASE/'PG17782-owned-mvc-loopback-runner-metadata-v1'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD='d1be3797900c6cceab2d4362bd9d1cec17d7ee1496d5c40859af0eaf62b8616f'
NEW='18a7ac7b682c388d72c7d3542c563c80b1c131accf41f5eeec7dce2d508e1f5f'
TRANSFORMS=[["{'WebManagementServerTest':10,'WebManagementDeadlineTest':3}","{'WebHttpServerTest':12,'WebHttpAdmissionTest':3}"],["only whole original reviewed thirteen; held child tests not authorized","only whole original reviewed fifteen; held child tests not authorized"],["/bootstrap/WebManagementServerTest.java","/bootstrap/WebHttpServerTest.java"],["EPHEMERAL_OR_PRIOR_SELF_OWNED_REBIND_OR_EXCLUSIVE_8081","EPHEMERAL_OR_PRIOR_SELF_OWNED_REBIND"],["SELF_OWNED_UNIT_TEST_HTTP_FIXTURE_NOT_API_BUSINESS_START_OR_OS_ADMISSION","SELF_OWNED_UNIT_TEST_HTTP_FIXTURE_NOT_PRODUCTION_BUSINESS_START_OR_OS_ADMISSION"]]
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only metadata, no Product calls')
    old=data.ROOT/'tools/quality/scoped_prometheus_owned_web_loopback_host_v1.py';new=data.ROOT/'tools/quality/scoped_prometheus_owned_mvc_loopback_host_v1.py'
    require(data.sha(old.read_bytes())==OLD and data.sha(new.read_bytes())==NEW,'immutable old/new bytes')
    expected=old.read_text()
    for a,b in TRANSFORMS:
        require(expected.count(a)==1,'one closed delta anchor');expected=expected.replace(a,b)
    def algorithm(candidate):require(candidate==expected,'all old algorithm/closed selection/source/session/terminal gates preserved')
    algorithm(new.read_text());algorithm_labels=[]
    for a,b in [('append=false','append=true'),('-proc:none','-proc:full'),('timeout=180','timeout=None'),('close_fds=True','close_fds=False'),('len(cases)==sum(COUNTS.values())','len(cases)>=0'),("c['result']=='PASS'","True"),("host.sha(SDK_FILE)==SDK_SHA","True")]:
        require(a in expected,'actual guard anchor');bad=expected.replace(a,b)
        require(bad!=expected,'nondegenerate algorithm vector')
        try:algorithm(bad)
        except ValueError:algorithm_labels.append(a)
        else:raise ValueError('altered runner guard accepted')
    base=dict(OWNED_LOOPBACK_AUTHORITY=True,SOURCE=SOURCE,COUNTS={'WebHttpServerTest':12,'WebHttpAdmissionTest':3},NEW_TEST=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServerTest.java',TEST_ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap',TEST_SOURCE_OVERRIDES={},FIXTURES={})
    saved={k:getattr(helper,k) for k in base};scope_labels=[]
    def configure(values):
        for k,v in values.items():setattr(helper,k,v)
    try:
        configure(base);effects=helper.loopback_effects()
        for k,v in [('OWNED_LOOPBACK_AUTHORITY',False),('SOURCE','0'*40),('COUNTS',{'WebHttpServerTest':12}),('COUNTS',{'WebHttpServerTest':12,'WebHttpAdmissionTest':3,'WebUnstartedManagementTest':1}),('NEW_TEST',Path('/not-selected')),('TEST_ROOT',Path('/not-selected')),('TEST_SOURCE_OVERRIDES',{'ApiManagementStopTest':Path('/not-selected')}),('FIXTURES',{'unknown':'0'*64})]:
            bad=copy.deepcopy(base);bad[k]=v;configure(bad)
            try:helper.loopback_effects()
            except ValueError:scope_labels.append(k)
            else:raise ValueError('unreviewed loopback scope accepted')
        configure(base);require(helper.loopback_effects()==effects,'no state leakage from negative scopes')
    finally:configure(saved)
    expected_effects=dict(actualNetworkActions=None,networkOperationCountStatus='NOT_MEASURED_NOT_ZERO',declaredOwnedLoopbackFixtureNetwork=True,declaredLoopbackAddresses=['127.0.0.1'],declaredLoopbackPorts='EPHEMERAL_OR_PRIOR_SELF_OWNED_REBIND',actualExternalNetworkActions=0,actualProductionServiceActions=0,effectAuthority='SELF_OWNED_UNIT_TEST_HTTP_FIXTURE_NOT_PRODUCTION_BUSINESS_START_OR_OS_ADMISSION')
    def effect_contract(v):require(v==expected_effects,'accurate bounded fixture effects, counts unknown not zero')
    effect_contract(effects);effect_labels=[]
    for k,v in [('actualNetworkActions',0),('networkOperationCountStatus','ZERO'),('declaredOwnedLoopbackFixtureNetwork',False),('declaredLoopbackAddresses',['0.0.0.0']),('declaredLoopbackPorts','ANY'),('actualExternalNetworkActions',1),('actualProductionServiceActions',1),('effectAuthority','PRODUCTION_READY')]:
        bad=copy.deepcopy(effects);bad[k]=v
        try:effect_contract(bad)
        except ValueError:effect_labels.append(k)
        else:raise ValueError('false fixture disclosure accepted')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,oldRunnerSha256=OLD,newRunnerSha256=NEW,exactAlgorithmOnlyDisclosureDelta=True,algorithmNegativeVectors=len(algorithm_labels),algorithmNegativeLabels=algorithm_labels,scopeNegativeVectors=len(scope_labels),scopeNegativeLabels=scope_labels,effectNegativeVectors=len(effect_labels),effectNegativeLabels=effect_labels,acceptedFixtureEffects=effects,productClassesLoaded=False,productTestsExecuted=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,rootMainInvoked=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
