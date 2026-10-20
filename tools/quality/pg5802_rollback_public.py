"""Independent finite54 XML/static/class reader; no PT, provider or external runtime action."""
import datetime
import hashlib
import json
import os
import xml.etree.ElementTree as ET
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5800_rollback_green import CASES,COUNTS,TARGETS,source_test_names
from pg5804_rollback_static import class_contract

SOURCE='9b80cc9540ff9b23ce45ee0c6893141db407be18'
W=ROOT.parent/'pgpt-runs/PG379';BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
DESIGN={
 'ConsumerRollbackUnconfirmedContractTest':dict(zip((
  'syncRollbackUnconfirmedStopsAllFourContexts','questionRollbackUnconfirmedStopsFurtherWork','webLogRollbackUnconfirmedStopsFurtherLogs','syncConfirmedRollbackKeepsAllFourContextsRetryReady','questionConfirmedRollbackKeepsRetryReady','webLogConfirmedRollbackKeepsRetryReady'),('001','002','003','009','010','011'))),
 'UnconfirmedJmsRollbackExceptionTest':dict(zip((
  'primaryAndRollbackMustBothBePresent','sameNodeIsRetainedOnceWithoutSelfSuppression','distinctEqualValuedNodesAreBothRetained','disabledPrimarySuppressionDoesNotHideRollbackFailure'),('005','006','007','008'))),
 'ReplyRollbackUnconfirmedContractTest':{'rollbackUnconfirmedMakesReplyOwnerUnreadyAndStopsFurtherDecode':'004'},
 'ReplyRollbackSignalContractTest':dict(zip((
  'unconfirmedRollbackSignalsInfrastructureOnceAndNeverCommittedFatal','confirmedRollbackRemainsRetryReadyWithoutFatalSignal','errorIdentitySurvivesConfirmedOrUnconfirmedRollbackAndOwnerStaysHalted','priorProtocolTerminalIsNeverRenotifiedOrReclassifiedAsUnconfirmedCommit','nullFatalSignalIsRejectedBeforeAcquisitionOrListenerStart'),('012','013','014','015','016')))}


def case_name(value):
    if not value or not value.split('(',1)[0].isidentifier():raise ValueError('ordinary method identity only')
    return value.split('(',1)[0]


def main():
    p=W/'pg5800-rollback-selected54-v4/manifest.safe.json';v=json.loads(p.read_bytes());snapshot=p.parent/'source';begin=json.loads(p.with_name('begin.safe.json').read_bytes())
    if not(v['source']==SOURCE and v['actualExit']==0 and v['phaseExits']==[0,0]and v['selectedQualified']and v['exactInventory']and v['sourceFixed']and not v['failedOrSkipped']and(v['tests'],v['suites'])==(54,15)):raise ValueError('actual current finite54 genuine terminal0 first')
    if begin['source']!=SOURCE or sha(p.parent/'source.tar')!=begin['archiveSha256']or v['archiveSha256']!=begin['archiveSha256']:raise ValueError('original fixed source/archive binding')
    if begin['commands'][0][-1]!='spotless:check'or not begin['commands'][1][-1].endswith(':check'):raise ValueError('format precedes tests and existing static check')
    sp=W/'pg5804-rollback-static-v1/manifest.safe.json';s=json.loads(sp.read_bytes());pub=BASE/'PG5804-rollback-static-v1/manifest.json'
    if sha(sp)!=json.loads(pub.read_bytes())['privateManifestSha256']or s['actualExit']!=0 or s['source']!=SOURCE or s['inputSourceFiles']!=850 or s['physicalMain']!=1665:raise ValueError('current independent850/1665 source static proof')
    prior=BASE/'PG5780-current3939-cases/qualification.json'
    if sha(prior)!='1a5a5db819bde6bf01c85b4bb43017b8aae15bd59407b66adfbc4f5a0ca23c45':raise ValueError('previous3939 physical reference, never test import')
    class_contract(json.loads(prior.read_bytes())['allPhysicalMainSha256'],v['allPhysicalMainSha256'])
    if v['allPhysicalMainSha256']!=s['auxClassHashes']or {q.relative_to(snapshot).as_posix():sha(q)for q in snapshot.glob('src/*/src/main/java/**/*.java')}!=s['allSourceHashes']:raise ValueError('same actual Main byte and source throughout independent checks')
    expected={};rows=[];actual={};static={};coverage={};counters={};start=datetime.datetime.fromisoformat(v['startedUTC']).timestamp();end=datetime.datetime.fromisoformat(v['completedUTC']).timestamp()
    for module,classes in CASES.items():
        for cls in classes:
            name='dev.codex.schubert.nk.'+cls;path=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java');names=source_test_names(path)
            if len(names)!=COUNTS[cls.rsplit('.',1)[1]]:raise ValueError('one explicit Test per source method')
            expected[name]=names
        target=snapshot/('src/schubert-nk-'+module+'/target');spot=target/'spotbugsXml.xml';static[module]=len(ET.parse(spot).getroot().findall('BugInstance'))
        for xml in sorted((target/'surefire-reports').glob('TEST-*.xml')):
            tree=ET.parse(xml).getroot();cls=tree.get('name')
            if cls in actual or cls not in expected or not start-2<=xml.stat().st_mtime<=end+2:raise ValueError('one fresh original XML per exact expected class')
            actual[cls]=set();xp=sha(xml)
            if xp!=v['xmlHashes'][cls]['sha256']:raise ValueError('actual original XML hashes fixed')
            for ordinal,case in enumerate(tree.findall('testcase'),1):
                name=case_name(case.get('name'))
                if name in actual[cls]or case.get('classname')!=cls or any(e.tag in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for e in case.iter()):raise ValueError('no failure skip rerun or normalized alias')
                actual[cls].add(name);design=DESIGN.get(cls.rsplit('.',1)[1],{}).get(name)
                rows.append({'testId':'PG5800-'+hashlib.sha256((cls+'#'+case.get('name')).encode()).hexdigest(),'class':cls,'method':name,'caseNameSha256':hashlib.sha256(case.get('name').encode()).hexdigest(),'ordinalInXml':ordinal,'xmlSha256':xp,'designTestId':'PT-JMS-UNC'+design if design else None,'result':'PASS_ORIGINAL_XML'})
        report=target/'site/jacoco/jacoco.xml';coverage[module]=sha(report)
        if coverage[module]!=v['coverage'][module]['sha256']:raise ValueError('actual current coverage XML')
        for name in TARGETS.get(module,[]):
            matches=[c for c in ET.parse(report).getroot().findall('package/class')if c.get('name')=='dev/codex/schubert/nk/'+name]
            if len(matches)!=1:raise ValueError('one actual target class')
            c={n.get('type'):{'covered':int(n.get('covered')),'missed':int(n.get('missed'))}for n in matches[0].findall('counter')};c={k:c.get(k,{'covered':0,'missed':0})for k in('LINE','METHOD','CLASS','BRANCH')};counters[module+':'+name]=c
    if actual!=expected or len(rows)!=54 or len(actual)!=15 or len({r['testId']for r in rows})!=54 or set(static)!=set(CASES)or any(static.values())or counters!=v['targetCounters']:raise ValueError('all and only finite54/15/six static0/actual counters')
    designs=[r['designTestId']for r in rows if r['designTestId']]
    if len(designs)!=16 or set(designs)!={'PT-JMS-UNC'+str(i).zfill(3)for i in range(1,17)}:raise ValueError('all16 independent design contracts uniquely traced')
    value={k:v[k]for k in('source','startedUTC','completedUTC','phaseExits','archiveSha256','tests','suites','staticIssues','targetCounters','targetFour100','fullRegressionPending','fullCoverageClaimed','formalAccepted','ptAlternativeCompleted','vmActions')};value.update(actualExit=0,independentXmlReadExit=0,physicalMain=1665,inputSourceFiles=850,selectedPrivateManifestSha256=sha(p),staticPrivateManifestSha256=sha(sp),staticPublicManifestSha256=sha(pub),allOriginalXmlSha256={k:r['sha256']for k,r in v['xmlHashes'].items()},coverageXmlSha256=coverage,caseTrace=rows,acceptedLeafDelta=0,effortPercent=None,newSourceNativeQualified=False)
    os.umask(0o077);out=BASE/'PG5802-rollback54-v1';out.mkdir();manifest=out/'manifest.json'
    with manifest.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'tests':54,'suites':15,'newDesignTestIds':16,'targetFour100':v['targetFour100'],'manifestSha256':sha(manifest),'formalAccepted':False}))


if __name__=='__main__':main()
