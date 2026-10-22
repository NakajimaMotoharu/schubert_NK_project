"""Qualify original normal observation PT only; no global coverage splice or runtime operation."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from pg5940_private_lock_compile import ROOT,W,BASE,sha
import pg6844_observation_boundaries_selected as selected
from pg6818_current_counter_delta import explicit_four100

QSHA='28748350e9f1d67cfb0e1addb43b073b398eee3f105d7948e1bf70c3e6dbd458'
FULL=BASE/'PG6828-current4203-cases/qualification.json'
FULLSHA='87d3de1b887514b10838d3cef748e9421f17574c87ae89a37f5b616a8e1f4dc0'
ACCEPTOR='batch:dev/codex/schubert/nk/batch/mq/ArtemisAcceptorReadinessClient.class'
PGCLASS='dev/codex/schubert/nk/batch/file/MorningGateEvidence'
PGDESC='(Ldev/codex/schubert/nk/batch/file/StartupPermitRecords$Epoch;Ljava/lang/String;Ljava/lang/String;Ldev/codex/schubert/nk/batch/repository/MorningDatabaseSession$DatabaseObservation;)[B'


def postgres_method(tree):
    methods=[m for c in tree.findall('package/class')if c.get('name')==PGCLASS for m in c.findall('method')if m.get('name')=='postgres'and m.get('desc')==PGDESC]
    if len(methods)!=1:raise ValueError('one exact original postgres member and descriptor')
    counters={c.get('type'):{k:int(c.get(k))for k in('covered','missed')}for c in methods[0].findall('counter')}
    if not all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in('LINE','METHOD','BRANCH')):
        raise ValueError('method actual positive counters/zero miss, never synthetic CLASS')
    return counters


def main():
    qp=BASE/'PG6846-observation-boundaries-original-v1/manifest.json'
    rp=W/'pg6846-observation-boundaries-original-v1';pp=rp/'manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA or sha(FULL)!=FULLSHA:raise ValueError('freeze genuine selected and prior full first')
    q,p,old=[json.loads(x.read_bytes())for x in(qp,pp,FULL)]
    if not(q['actualExit']==0 and q['source']==p['source']and(q['tests'],q['suites'],q['physicalMain'])==(23,11,1669)
      and q['privateManifestSha256']==sha(pp)and q['originalSixSpotBugs']==q['checkstyleFindings']==0
      and q['pmdRawFindings']==1405 and q['changedPhysical']==[]and p['allSourceHashes']==old['allSourceHashes']
      and p['allPhysicalMainSha256']==old['allPhysicalMainSha256']):raise ValueError('all851/1669 exact prior Main, original selected23 only')
    selected.guard(q['source'])
    if subprocess.check_output(['git','diff',q['source'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('current Main/Test/gates remain original')
    if {x.relative_to(ROOT).as_posix():sha(x)for x in ROOT.glob('src/*/src/main/java/**/*.java')}!=p['allSourceHashes']:raise ValueError('all actual current851 Main unchanged')
    run=W/selected.SLOT
    original=json.loads((run/'manifest.safe.json').read_bytes());xml=run/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml'
    if sha(xml)!=original['coverage']['batch']['sha256']or q['originalManifestSha256']!=sha(run/'manifest.safe.json'):raise ValueError('actual original coverage XML/terminal')
    target=p['allActualCounters'][ACCEPTOR]
    if not explicit_four100(target):raise ValueError('acceptor actual four counters, no exclusions or absent fill')
    method=postgres_method(ET.parse(xml).getroot());cases_path=rp/'cases.safe.json'
    if sha(cases_path)!=q['casesSha256']:raise ValueError('original selected case map')
    cases=json.loads(cases_path.read_bytes());rows=[]
    mapping={
      'dev.codex.schubert.nk.batch.mq.AcceptorObjectBoundaryTest':{
        'opsMqObj001RejectsEachNonObjectExtraPropsBeforeStartedRead':'PT-OPS-MQ-OBJ001',
        'opsMqObj002RejectsEachNonObjectParamsBeforeStartedRead':'PT-OPS-MQ-OBJ002'},
      'dev.codex.schubert.nk.batch.file.PostgresObservationRowsTest':{
        'pgRows001MaximumFullGoldenAndOversizeOrSameBomRankGapRejected':'PT-OPS-PG-ROWS-001'}}
    for cls,methods in mapping.items():
        path=ROOT/'src/schubert-nk-batch/src/test/java'/(cls.replace('.','/')+'.java')
        for name,tid in methods.items():
            matches=[c for c in cases if c['className']==cls and c['method']==name and c['source']==q['source']and c['result']=='PASS_ORIGINAL_XML']
            if len(matches)!=1:raise ValueError('one original case per independent TestID')
            rows.append(dict(testId=tid,sourcePath=path.relative_to(ROOT).as_posix(),sourceSha256=sha(path),method=name,originalCase=matches[0]))
    if len(cases)!=23:raise ValueError('whole selected case identities, not new vector count')
    value=dict(actualExit=0,source=q['source'],selectedQualificationSha256=sha(qp),originalTerminalSha256=sha(run/'manifest.safe.json'),
      originalCoverageXmlSha256=sha(xml),priorFullQualificationSha256=FULLSHA,priorFullSource=old['productionSource'],
      all851MainByteExact=True,all1669PhysicalMainByteExact=True,mainChanges=0,oldTestChanges=0,
      selectedTests=23,selectedSuites=11,newJUnitMethods=3,independentTestIdTrace=rows,
      acceptorCounters=target,postgresMethodCounters=method,postgresClassCounters=p['allActualCounters']['batch:'+PGCLASS+'.class'],
      postgresClassFullyCovered=explicit_four100(p['allActualCounters']['batch:'+PGCLASS+'.class']),
      newSourceGlobalCounters=None,oldFullImportedIntoNewGlobal=False,currentWholePending=True,
      testsExecutedByReader=0,additionalBuildsIssued=0,vmActions=0,realBusinessOperations=0,
      nativeQualified=False,formalAccepted=False,ptAlternativeCompleted=0,acceptedLeafDelta=0,effortPercent=None,
      scope='Normal selected data validation; actual retention/Root/cohort/native remain held. Prior full is Main identity proof only, not new-source global coverage.',
      toolSha256=sha(Path(__file__)))
    out=BASE/'PG6848-observation-boundary-qualification-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),newJUnitMethods=3,acceptorFour100=True,postgresMethod100=True,postgresClass100=value['postgresClassFullyCovered'])))


if __name__=='__main__':main()
