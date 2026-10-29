"""Twenty-two private monitor contexts; retain all raw findings and dynamic/pinning risks."""
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE=cfg.SOURCE
OUT=data.BASE/'PG14052-sampling-budget-admission-monitor-contexts-v1'
MEASURED=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
RULE='AvoidSynchronizedStatement'
TARGETS=json.loads("{\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java\":[\"6ae561e25cfcdcce0b6b61641b3b2afd7867cf0eaa646059c8b3606dd915e28b\",null,[\"PMD-00097\",\"PMD-00098\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricCollector.java\":[\"e1acec700e97398c11aa2a690a87b84f0a4df5d00b01a12ad9da2660d257e138\",\"WBS-P018-09\",[\"PMD-00351\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricCollector.java\":[\"e62f5a2eda99539f59e540ca4d54e9d70d99d7c4c25b0d30e75a98801a295515\",\"WBS-P018-09\",[\"PMD-00354\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/DbQueryDurationMetricCollector.java\":[\"ec89dd7ee618ea44a50067d99d0b26c9b1ee8ad247f3ec44adf4edc81927a4bb\",\"WBS-P018-09\",[\"PMD-00357\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/MqPressureMetricCollector.java\":[\"51493fa1068d31c0652e30f4b899b82103eb74f7471ba14c97c2e2c391e064ae\",\"WBS-P018-09\",[\"PMD-00360\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OutboxMetricCollector.java\":[\"db5801d5f2627d4dbbda16cdec6d75165e01a789101d77e732a6c7e3d35434ea\",\"WBS-P018-09\",[\"PMD-00363\"]],\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/TimedDbPoolMonitor.java\":[\"bf02bb6b387398ce3a0f5f1229b1df747284eef521946984a7d37d834a4ac649\",\"WBS-P018-09\",[\"PMD-02974\",\"PMD-02975\"]],\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/TimedJvmHeapMonitor.java\":[\"e17c6174e193584fcc681d26706390d165c7a29b7ea1c77a13ac3a7eb54566e4\",\"WBS-P018-09\",[\"PMD-02978\",\"PMD-02979\"]],\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/TimedSyncLatencyMonitor.java\":[\"fb6e3e4efc7d43f537bbe830537bfccd133f759640943be3f0204e83a92dd7a9\",\"WBS-P018-09\",[\"PMD-02980\",\"PMD-02981\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpAdmission.java\":[\"dd0cda3ed6582fed7cd1d05ce1505d8b4bbfa77eb2984cd275b7c585e57ee130\",\"WBS-P018-06\",[\"PMD-07202\",\"PMD-07203\",\"PMD-07204\",\"PMD-07205\",\"PMD-07206\",\"PMD-07207\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/MediaStreamsMetricCollector.java\":[\"8361006db20fb7346ad0faa6adc3521dd8877ccd9866c3684f57109f0a60d4f6\",\"WBS-P018-09\",[\"PMD-07376\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricCollector.java\":[\"dc1b278e0d111128b2679b7943ae1cabe56ea55eb7cbdc0104503e2b99a46210\",\"WBS-P018-09\",[\"PMD-07379\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebOutboxMetricCollector.java\":[\"110e730c16f77a5b87a6a2a31a49e4e82feb45da3eb6393c8336d7c0004b322a\",\"WBS-P018-09\",[\"PMD-07382\"]]}")
IDS={v for _,_,ids in TARGETS.values() for v in ids}
DESIGN={
 'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md':'9da7c4e4f24740e031f37f984ec562d56e14ff098b1433af3ec55fe15bd195e6',
 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md':'3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82',
}
RULE_JAR=Path('/home/mini/codex/project1/work/toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar')
RULE_JAR_SHA='068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
RULE_RESOURCE_SHA='a584188485d8da3ca58abf4d80cfd443775a2f9fecdc97ebd6aa4dec33049da3'
def reason(path,method):
    name=path.rpartition('/')[2]
    if name=='ApiStopBudget.java':
        return 'SS342/351: one private final monitor atomically claims the first stop clock and preserves irreversible expiry across begin/remaining. Failed clock cannot refresh budget. It is no resource or native TERM timing proof, and supplier blocking/pinning/time bounds remain unmeasured.'
    if name=='WebHttpAdmission.java':
        return 'SS342/352: same private monitor protects admission/stopping/request lease count; completion notifies drain, wait releases the same monitor and checks original deadline/interrupt after wakeup. Actual Tomcat terminal lease pairing, callback bounds, drain/owner termination and native pinning remain unqualified; no generic replacement of wait/notify semantics.'
    if name.startswith('Timed'):
        return 'SS351: same private final monitor serializes monotonic elapsed, continuity windows and lifecycle updates with snapshot. Missing values do not become measured zero, and supplied report evaluation is not actual OOM/process/DB/endpoint sampling. This source reference does not prove concurrent schedules or performance/native safety.'
    if name=='DbQueryDurationMetricCollector.java':
        return 'SS332/351: private owner serializes supplied duration acquisition and event publication. Missing/failed acquisition creates no event, not a fabricated zero or success. Supplier may block/throw; no query execution, outer deadline, native pinning or real service proof is obtained here.'
    return 'SS351/411 section9: private final owner monitor serializes sample acquisition through recorder publication; absent/failing observation clears only the relevant family/dimension and propagates failure. Borrowed connection/provider/source is not closed by the collector. Source callbacks and underlying recorder semantics/real IO/native pinning/whole concurrent outcomes remain separately unqualified; no blanket Java25 rule exemption.'
GUARDS={
 'ApiStopBudget.java':['if (begun) return;','begun = true;','began = time();','if (expired) return 0;','if (!returned) expired = true;'],
 'WebHttpAdmission.java':['active++;','active--;','lock.notifyAll();','while (active != 0)','lock.wait(left / 1_000_000, (int) (left % 1_000_000));','Thread.currentThread().interrupt();'],
 'TimedDbPoolMonitor.java':['elapsed.compareTo(lastElapsed.orElseThrow()) < 0','lastElapsed = Optional.of(elapsed);','if (!consecutive || percent.isEmpty()) lifecycle.interruptContinuity(elapsed);','return lifecycle.snapshot();'],
 'TimedJvmHeapMonitor.java':['elapsed.compareTo(lastElapsed.orElseThrow()) < 0','lastElapsed = Optional.of(elapsed);','if (!consecutive || percent.isEmpty()) lifecycle.interruptContinuity(elapsed);','return lifecycle.snapshot();'],
 'TimedSyncLatencyMonitor.java':['elapsed.compareTo(lastElapsed.orElseThrow()) < 0','lastElapsed = Optional.of(elapsed);','if (!consecutive || seconds.isEmpty()) lifecycle.interruptContinuity(elapsed);','return lifecycle.snapshot();'],
}
def source_guards(path,text):
    assert 'private final Object lock = new Object();' in text and 'synchronized (lock)' in text
    assert 'synchronized (this)' not in text and '.class)' not in text
    for phrase in GUARDS.get(path.rpartition('/')[2],['detailedMetricsRequested()', 'return Optional']):assert phrase in text
def related_imports(path,text,hashes):
    result={}
    for imported in re.findall(r'^import (?:static )?(dev\.codex\.schubert\.nk\.[A-Za-z0-9_.]+);$',text,re.M):
        parts=imported.split('.');found=None
        while len(parts)>=6:
            suffix='/src/main/java/'+'/'.join(parts)+'.java'
            candidates=[p for p in hashes if p.endswith(suffix)]
            if candidates:
                assert len(candidates)==1;found=candidates[0];break
            parts.pop()
        assert found is not None
        result[imported]=dict(path=found,sha256=hashes[found],qualification='RELATED_SOURCE_HASH_ONLY_NOT_WHOLE_REVIEW_OR_EXECUTION')
    return result
def rule_evidence(measured):
    assert data.sha(RULE_JAR.read_bytes())==RULE_JAR_SHA
    with zipfile.ZipFile(RULE_JAR) as z:raw=z.read('category/java/multithreading.xml')
    assert data.sha(raw)==RULE_RESOURCE_SHA
    rule,=[v for v in ET.fromstring(raw) if v.tag.rpartition('}')[2]=='rule' and v.get('name')==RULE]
    values=[v.text.strip() for v in rule.iter() if v.tag.rpartition('}')[2]=='value' and v.text and 'SynchronizedStatement' in v.text]
    assert values==['//SynchronizedStatement']
    command=measured['stages']['pmd']['command'];assert command[command.index('--use-version')+1]=='java-25' and measured['stages']['pmd']['actualExit']==4
    return dict(jarSha256=RULE_JAR_SHA,resourceSha256=RULE_RESOURCE_SHA,xpath=values[0],analysisLanguage='java-25',originalPmdExit=4,version='7.28.0',allJava25MonitorsExempt=False,newStaticRunExecuted=False)
def rows():
    normal,_=cfg.normal();hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    for p,pin in DESIGN.items():assert data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT))==data.sha((data.ROOT/p).read_bytes())==pin
    measured=data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);rule=rule_evidence(measured)
    facts=data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    old=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result=[];imports={}
    for path,(pin,owner,identities) in TARGETS.items():
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==hashes[path]==pin;source_guards(path,text)
        imports[path]=related_imports(path,text,hashes)
        ownership=canonical(path,logical);assert ownership['canonicalOwner']==ownership['canonicalCostOwner']==owner
        selected=[r for r in facts if r['path']==path and r['rule']==RULE];prior=[r for r in old if r['id'] in identities]
        assert len(selected)==len(prior)==len(identities)
        for row in prior:
            matches=[v for v in selected if v['attributes']==row['attributes']];assert len(matches)==1 and row['inputSha256']==matches[0]['sourceSha256']==pin
            start,end,value=span(text,row['attributes']);assert value=='synchronized'
            assert text[end:].startswith(' (lock)')
            result.append(dict(id=row['id'],path=path,source=SOURCE,sourceSha256=pin,rule=RULE,attributes=row['attributes'],originalRowSha256=row['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),typeToken=value,monitor='lock',monitorDeclaration='private final Object lock = new Object();',rawDiagnosticMultiplicity=1,occurrenceOrdinal=0,reason=reason(path,row['attributes']['method']),disposition='PRIVATE_OWNER_MONITOR_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,allJava25MonitorsExempt=False,**ownership))
    assert len(result)==22 and {r['id'] for r in result}==IDS
    return sorted(result,key=lambda r:r['id']),rule,imports
if __name__=='__main__':
    invocation=capture(__file__);assert not OUT.exists();result,rule,imports=rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,approvedDesignHashes=DESIGN,staticRuleEvidence=rule,directNkRelatedSourceScope=imports,importScopeIsNotRuntimeAllowlist=True))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=22,sourceFiles=13,rawRetained=22,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False,allJava25MonitorsExempt=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
