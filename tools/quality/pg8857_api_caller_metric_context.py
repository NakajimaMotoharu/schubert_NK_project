"""Existing six exact collector rationales + current60 XML/source join, no legacy PT/exec transfer."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg8856_api_caller_metric_host as selected
from host_tool_invocation import capture,verify

host=selected.run.host
OUT=host.BASE/'PG8857-api-caller-metric-context-v1'
RAW=host.W/'pg8856-api-caller-metric-host-v1/manifest.safe.json'
RAW_SHA=host.sha(RAW)
LEGACY={
 'api':('PG7372-api-pool-observation-review-v1/manifest.json','cf76bd87cc5a35c58b4b005de3a0206ee9f1d9130a9eee1f6d084f507e202178','staticDispositions','DbPoolMetricCollector'),
}
RULES='tools/quality/static/pmd.xml'

def qualify_rows(raw,normal,legacy):
    assert raw['actualExit']==0 and raw['begin']['source']==normal['source']==selected.SOURCE
    assert normal['actualExit']==normal['terminal']['actualExit']==0 and normal['testsExecuted']==0
    expected={'dev.codex.schubert.nk.api.monitoring.'+name:number for name,number in selected.COUNTS.items()}
    assert set(raw['suites'])==set(expected)
    assert all(row==dict(tests=expected[name],failures=0,errors=0,skipped=0) for name,row in raw['suites'].items())
    rows=[];pins={}
    for role,(relative,digest,key,name) in LEGACY.items():
        proof=legacy[role]
        assert proof['actualExit']==0
        if role=='api': assert proof['currentApiUnclassified']==proof['currentApiApplicableViolations']==0
        else: assert proof['unclassified']==proof['actualViolationsOutstanding']==0
        path=f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{name}.java'
        old_source=subprocess.check_output(['git','show',proof['source']+':'+path],cwd=host.ROOT)
        old_rules=subprocess.check_output(['git','show',proof['source']+':'+RULES],cwd=host.ROOT)
        assert old_source==(host.ROOT/path).read_bytes()
        assert old_rules==(host.ROOT/RULES).read_bytes()
        assert hashlib.sha256(old_source).hexdigest()==normal['begin']['inputHashes'][path]==raw['begin']['sourceHashes'][path]
        chosen=[copy.deepcopy(row) for row in proof[key] if row['sourcePath']==path]
        assert len(chosen)==3
        expected_keys={('AvoidSynchronizedStatement','27','5'),('AvoidCatchingGenericException','34','16'),('AvoidCatchingGenericException','34','35')}
        assert {(row['raw']['rule'],row['raw']['beginline'],row['raw']['begincolumn']) for row in chosen}==expected_keys
        for row in chosen:
            assert row['sourceSha256']==host.sha(host.ROOT/path) and row['sourceOrRulesChanged'] is False and row['suppressionAdded'] is False
            assert row['classification']=='CONTEXT_NOT_APPLICABLE' and len(row['reason'])>80
            assert row['raw']['package']==f'dev.codex.schubert.nk.{role}.monitoring' and row['raw']['class']==name and row['raw']['method']=='collect'
        compact=''.join(old_source.decode().split())
        assert 'privatefinalObjectlock=newObject();' in compact and 'synchronized(lock){' in compact
        assert 'catch(RuntimeException|ErrorunavailableObservation){metrics.missing();throwunavailableObservation;}' in compact
        rows.extend(chosen)
        pins[role]=dict(path=relative,sha256=digest,source=proof['source'],semantics='HISTORICAL_SOURCE_FIXED_RATIONALE_ONLY_NOT_CURRENT_PT_OR_COVERAGE',currentTestClass=f'dev.codex.schubert.nk.{role}.monitoring.{role.title()}DbPoolMetricBindingTest',currentCases=[f'{role}poolb005EveryRuntimeGetterFailureClearsPreservesIdentityAndDoesNotRetry',f'{role}poolb006DirectGetterErrorRemainsFatalAndMissing',f'{role}poolb010OneRetainedCollectorSerializesBothOwnedRefreshes'])
    assert len(rows)==3
    return rows,pins

def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists() and host.sha(RAW)==RAW_SHA
    assert host.sha(selected.COMPILE/'manifest.safe.json')==selected.COMPILE_SHA
    raw=json.loads(RAW.read_text());normal=json.loads((selected.COMPILE/'manifest.safe.json').read_text())
    legacy={}
    for role,(path,digest,_,_) in LEGACY.items():
        assert host.sha(host.BASE/path)==digest
        legacy[role]=json.loads((host.BASE/path).read_text())
    rows,pins=qualify_rows(raw,normal,legacy)
    current_cases={}
    for role,pin in pins.items():
        file=selected.run.host.W/'pg8856-api-caller-metric-host-v1/xml'/('TEST-'+pin['currentTestClass']+'.xml')
        assert host.sha(file)==raw['xmlHashes'][file.name]
        xml=ET.parse(file).getroot()
        cases={row.attrib['name']:row for row in xml.findall('testcase')}
        assert len(cases)==15
        assert all(name in cases and not list(cases[name]) for name in pin['currentCases'])
        current_cases[role]=dict(xmlSha256=host.sha(file),cases=pin['currentCases'],source=selected.SOURCE,result='ACTUAL_NEW_CASES_F0_E0_S0_NOT_LEGACY_TRANSFER')
    assert all(host.sha(host.ROOT/path)==digest for path,digest in raw['begin']['sourceHashes'].items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=selected.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,normalManifestSha256=selected.COMPILE_SHA,currentHostManifestSha256=RAW_SHA,legacyRationalePins=pins,currentSemanticCases=current_cases,staticDispositions=rows,rawWarningsExpectedRetained=3,pmdRulesSha256=host.sha(host.ROOT/RULES),unclassified=0,actualViolationsOutstanding=0,reviewScope='EXACT_UNCHANGED_COLLECTOR_SOURCE_AND_RULE_ROWS_WITH_CURRENT_SELECTED_XML',currentSixMainStaticRunPending=True,currentCoverageQualificationPending=True,productPtExecutedByThisTool=0,coverageUnion=False,suppressionsAdded=False,formalUpdated=False,newAccepted=0,managerDynamicPt='UNRUN_HOLD',actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,exactRationaleRows=3,oldProductPtReplayed=0,currentSource=selected.SOURCE,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
