"""Immutable API15/18 same-value bounds plan; no PG mutation/PT/runtime invocation."""
import hashlib
import json
import os
import re
from collections import defaultdict
from pg5964_api_sql_constants_plan import declared_source,formatted
from pg5940_private_lock_compile import ROOT,BASE,W,sha
from pg5994_web24_public import SOURCE
from static_disposition_overlay import load

RULES={
 'QuestionWorkerService':[('if (delivery.deliveryCount() < 4)','if (delivery.deliveryCount() < TERMINAL_DELIVERY_COUNT)','int TERMINAL_DELIVERY_COUNT','4')],
 'ScenarioDetailDelivery':[('if (snapshot.records().size() <= 200)','if (snapshot.records().size() <= MAXIMUM_INLINE_RECORDS)','int MAXIMUM_INLINE_RECORDS','200')],
 'ApiManagementServer':[('if (json.length() > 1)','if (json.length() > JSON_OPENING_DELIMITER_LENGTH)','int JSON_OPENING_DELIMITER_LENGTH','1'),
                        ('if ("/actuator/info".equals(path))','if (INFORMATION_PATH.equals(path))','String INFORMATION_PATH','"/actuator/info"'),
                        ('if ("/actuator/prometheus".equals(path))','if (METRICS_PATH.equals(path))','String METRICS_PATH','"/actuator/prometheus"')],
 'FingerprintKeyRing':[('if (key.length < 32)','if (key.length < MINIMUM_FINGERPRINT_KEY_BYTES)','int MINIMUM_FINGERPRINT_KEY_BYTES','32')],
 'RequestLogDetails':[('if (text.getBytes(StandardCharsets.UTF_8).length > 1024)','if (text.getBytes(StandardCharsets.UTF_8).length > MAXIMUM_REQUEST_DETAILS_UTF8_BYTES)','int MAXIMUM_REQUEST_DETAILS_UTF8_BYTES','1024')],
 'QuestionMutationInboxInspector':[('if (wire.length != 320)','if (wire.length != EXPECTED_QUESTION_WORK_BYTES)','int EXPECTED_QUESTION_WORK_BYTES','320')],
 'ArtemisConnectionFactoryProvider':[('if (port > 65_535)','if (port > MAXIMUM_TCP_PORT)','int MAXIMUM_TCP_PORT','65_535')],
 'JmsMessageGuard':[('if (count < 1)','if (count < MINIMUM_DELIVERY_COUNT)','int MINIMUM_DELIVERY_COUNT','1')],
 'OutboxDlqMetadata':[('if (deliveryCount < 1)','if (deliveryCount < MINIMUM_DELIVERY_COUNT)','int MINIMUM_DELIVERY_COUNT','1')],
 'LogQueryRepository':[('if (total > 99999900)','if (total > MAXIMUM_PAGED_TOTAL_RECORDS)','int MAXIMUM_PAGED_TOTAL_RECORDS','99_999_900')],
 'QuestionQueryRepository':[('if (total > 49_999_950)','if (total > MAXIMUM_PAGED_TOTAL_RECORDS)','int MAXIMUM_PAGED_TOTAL_RECORDS','49_999_950')],
 'ScenarioRepository':[('if (total > 99_999_900)','if (total > MAXIMUM_PAGED_TOTAL_RECORDS)','int MAXIMUM_PAGED_TOTAL_RECORDS','99_999_900'),
                       ('if (records.size() == 10000)','if (records.size() == MAXIMUM_DETAIL_RECORDS)','int MAXIMUM_DETAIL_RECORDS','10_000')],
 'UserQueryRepository':[('if (total > 49_999_950)','if (total > MAXIMUM_PAGED_TOTAL_RECORDS)','int MAXIMUM_PAGED_TOTAL_RECORDS','49_999_950')],
 'AuthContextCodec':[('if (key.length != 32)','if (key.length != AUTH_CONTEXT_KEY_BYTES)','int AUTH_CONTEXT_KEY_BYTES','32')],
 'ScenarioFileWriter':[('if (attempt >= 3)','if (attempt >= MAXIMUM_COLLISION_RETRY_INDEX)','int MAXIMUM_COLLISION_RETRY_INDEX','3')]}


def private_source(before,changes,constants):
    record=re.search(r'^public record ([A-Za-z_$][\w$]*)\([^{}]*\) \{',before,re.MULTILINE)
    enum=re.search(r'^public enum (ArtemisConnectionFactoryProvider) \{\s+INSTANCE;',before,re.MULTILINE)
    special=record or enum
    if special is None:return declared_source(before,changes,constants)
    original=special.group();placeholder='public final class '+special.group(1)+' {'
    if before.count(original)!=1 or placeholder in before:raise ValueError('one exact record/enum header; preserve components/enum constant ordering')
    return declared_source(before.replace(original,placeholder,1),changes,constants).replace(placeholder,original,1)


def main():
    bp=BASE/'PG6002-direct-jdbc-finally63-v1/manifest.json';bsha='ad81ef51ee6c97ec86f72266a3e8bfd8183cb4789b91cd00949395ba8fbfd181';rows=load(bp,bsha,SOURCE);groups=defaultdict(list)
    for r in rows:
        if r['status']=='NOT_REVIEWED_CURRENT_SOURCE' and r['rule']=='AvoidLiteralsInIfCondition' and r['sourcePath'].startswith('src/schubert-nk-api/') and r['sourcePath'].rsplit('/',1)[1][:-5] in RULES:
            groups[r['sourcePath']].append(r)
    if len(groups)!=15 or sum(map(len,groups.values()))!=18:raise ValueError('all15 eligible API sources/18 current raw warnings, native main one not omitted as accepted')
    baseline=W/'pg5966-api-sql-selected1021-v1/manifest.safe.json';old=json.loads(baseline.read_bytes())
    if sha(baseline)!='2890bb1385a43d81d38f7799e9e2f0677ee448019a3570e6a8fbf60d7fe41941' or old['actualExit']!=0:raise ValueError('actual selected API source qualification retained;not current-source success')
    current=json.loads((W/'pg5992-web-contract-static-v1/manifest.safe.json').read_bytes());plans=[]
    for path,diagnostics in sorted(groups.items()):
        before=(ROOT/path).read_text();changes=[];constants=set();simple=path.rsplit('/',1)[1][:-5]
        for a,b,declaration,value in RULES[simple]:
            count=before.count(a)
            if count<1:raise ValueError('one exact declared current condition: '+simple+' '+a)
            changes.append((a,b,count));constants.add('private static final '+declaration+' = '+value+';')
        key='api:'+path.split('/src/main/java/')[1][:-5]+'.class'
        if sum(c[2]for c in changes)!=len(diagnostics) or any(r['sourceSha256']!=sha(ROOT/path)for r in diagnostics) or old['allPhysicalMainSha256'][key]!=current['auxClassHashes'][key]:raise ValueError('one actual current warning per exact token;unchanged baseline owner byte')
        counters=old['coverage']['api']['classes'][key.split(':',1)[1][:-6]]
        if not all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ('LINE','METHOD','CLASS','BRANCH')):raise ValueError('explicit original baseline four counters100, never new source pass')
        after=formatted(private_source(before,changes,sorted(constants)))
        plans.append(dict(path=path,beforeSha256=sha(ROOT/path),predictedAfterSha256=hashlib.sha256(after.encode()).hexdigest(),changes=changes,constants=sorted(constants),findingIds=[r['findingId']for r in diagnostics],baselineCounters=counters,productionApplied=False))
    cp=BASE/'PG5970-api-sql1021-v1/cases.json'
    if sha(cp)!='0b6c700f292df4241824399724aa4179ac04329228e5edd58a2712234c1efc79':raise ValueError('immutable independent semantic Test identities only')
    cases=[r for r in json.loads(cp.read_bytes())if r['module']=='api']
    if len(cases)!=1010 or len({r['class']for r in cases})!=169:raise ValueError('all API1010/169 unchanged Test semantics')
    out=BASE/'PG6004-api-bounds18-plan-v1';os.umask(0o077);out.mkdir();value=dict(actualExit=0,source=SOURCE,sourcePlans=plans,selectedSourceFiles=15,selectedDiagnosticConditions=18,baseManifestPath=bp.relative_to(ROOT).as_posix(),baseManifestSha256=bsha,
         plannedApiCaseReferences=[{k:r[k]for k in ('class','caseNameSha256')}for r in cases],plannedApiCases=1010,plannedApiSuites=169,additionalGuardCases=11,sourceCodeApplied=False,testsExecuted=0,oldBaselineNotNewPt=True,ptAlternativeCompleted=0,formalAccepted=False,F03Accepted=False,vmActions=0)
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,sourceFiles=15,conditions=18,manifestSha256=sha(out/'manifest.json'),productionApplied=False)))


if __name__=='__main__':main()
