"""Thirteen bounded applicability checks; no test, analyzer, VM or runtime operation."""
import copy
import hashlib
import json
import os
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT,TC,sha
from pg5734_enum48_static import renamed_source
from pg5758_static_rebind import SOURCE,coordinate

BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
W=ROOT.parent/'pgpt-runs/PG379'
OUT=BASE/'PG5760-changed-context-v1'
ROOT_PATH='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/RootStartupContext.java'
WEB_PATH='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java'
UNCHANGED_OUTERS={
 'BackupUnitStartClient.java':{'DoNotUseThreads':5},
 'InspectorUnitSnapshot.java':{'UseConcurrentHashMap':1},
 'SystemManagerObservation.java':{'DoNotUseThreads':4,'NullAssignment':1}}


def exact_scope(before,after,mode):
    if mode=='NATIVE_IO':
        marker='  static final class NativeIo implements Io {'
        if before.count(marker)!=1 or after.count(marker)!=1:raise ValueError('one exact NativeIo declaration')
        left,right=before.index(marker),after.index(marker)
        if before[left:]!=after[right:]:raise ValueError('actual complete NativeIo source tail changed')
        return after[:right].count('\n')-before[:left].count('\n')
    if renamed_source(mode,before)!=after:raise ValueError('only bounded declared private enum edits permitted')
    return 0


def opcode(text):
    text=re.sub(r'#\d+[ \t]+(?=//)','<cp> ',text)
    return re.sub(r'#\d+','<cp>',text)


def main():
    sp=BASE/'PG5758-current-dispositions-v1/manifest.json'
    if sha(sp)!='4ce7da2d11ac41fc2e087dc4f0887b89ef139cf7b813f5c815a89ca9012ee55b':raise ValueError('exact prior conservative rebind')
    rows=json.loads(sp.with_name('findings.json').read_bytes())
    oldp=BASE/'PG5690-current-identity-review-v1/manifest.json'
    if sha(oldp)!='7d318fea2b0cdddaf7af4de85aaf6453356689ab0b06d42e9d7dcaa24ee4c53e':raise ValueError('original individual dispositions')
    old=json.loads(oldp.read_bytes());whole=json.loads((BASE/'PG5588-current3905-cases/qualification.json').read_bytes())
    cp=W/'pg5750-exception-static-v1/manifest.safe.json';proof=json.loads(cp.read_bytes())
    if proof['source']!=SOURCE or proof['actualExit']!=0:raise ValueError('current all-source and all-byte proof')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('current source immutability')
    if subprocess.check_output(['git','diff',old['source'],SOURCE,'--','pom.xml',':(glob)src/*/pom.xml','src/deployment','program/characterization'],cwd=ROOT):raise ValueError('own JVM/dependency contracts must remain unchanged')
    jar=TC/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar';rules={}
    with zipfile.ZipFile(jar)as z:
        for entry in('category/java/multithreading.xml','category/java/errorprone.xml'):
            raw=z.read(entry)
            for rule in ET.fromstring(raw).findall('{*}rule'):
                if rule.get('name')in('DoNotUseThreads','UseConcurrentHashMap','UseProperClassLoader'):
                    rules[rule.get('name')]={'entry':entry,'entrySha256':hashlib.sha256(raw).hexdigest(),'message':rule.get('message'),'definitionSha256':hashlib.sha256(ET.tostring(rule)).hexdigest()}
    if set(rules)!={'DoNotUseThreads','UseConcurrentHashMap','UseProperClassLoader'}or'J2EE'not in rules['DoNotUseThreads']['message']or'J2EE'not in rules['UseProperClassLoader']['message']or'concurrent access'not in rules['UseConcurrentHashMap']['message']:raise ValueError('installed actual context-dependent rule premises')
    planned=[r for r in old['findings']if Path(r['sourcePath']).name in UNCHANGED_OUTERS and r['status']in('CONTEXT_NOT_APPLICABLE','REQUIRED_CONTRACT','FALSE_POSITIVE')]
    planned +=[r for r in old['findings']if r['sourcePath']==ROOT_PATH and r['rule']=='DoNotUseThreads'and r['status']=='CONTEXT_NOT_APPLICABLE']
    if len(planned)!=12:raise ValueError('exact twelve previously held individual diagnostics')
    scope_proofs={};updates=[]
    for prior in planned:
        path=prior['sourcePath'];oldraw=subprocess.check_output(['git','show',old['source']+':'+path],cwd=ROOT,text=True);newraw=(ROOT/path).read_text()
        if sha(ROOT/path)!=proof['allSourceHashes'][path]:raise ValueError('source diagnostic binding')
        native=path==ROOT_PATH;shift=exact_scope(oldraw,newraw,'NATIVE_IO'if native else path)
        module=path.split('/')[1].removeprefix('schubert-nk-');member=path.split('/src/main/java/')[1][:-5]+('$NativeIo'if native else'');key=module+':'+member+'.class'
        oldhash=whole['allPhysicalMainSha256'][key];newhash=proof['auxClassHashes'][key]
        record={'sourcePath':path,'oldSourceSha256':hashlib.sha256(oldraw.encode()).hexdigest(),'currentSourceSha256':sha(ROOT/path),'scope':'complete NativeIo tail and opcode'if native else'outer class unchanged; only bounded nested enum edits','lineShift':shift,'declaringClass':key,'oldPhysicalSha256':oldhash,'currentPhysicalSha256':newhash}
        if native:
            snapshots=(W/'pg5566-private-monitor-green-v3/source',W/'pg5748-exception-green-v1/source');dumps=[]
            for snapshot,expected in zip(snapshots,(oldhash,newhash)):
                classes=snapshot/('src/schubert-nk-'+module+'/target/classes');p=classes/(member+'.class')
                if sha(p)!=expected:raise ValueError('actual historical/current NativeIo byte hashes')
                dumps.append(opcode(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-classpath',str(classes),member.replace('/','.')],text=True)))
            if dumps[0]!=dumps[1]:raise ValueError('NativeIo actual descriptors/opcodes/literals changed')
            record.update(opcodeSha256=hashlib.sha256(dumps[1].encode()).hexdigest(),debugDifferenceNotDiscarded=oldhash!=newhash)
        elif oldhash!=newhash:raise ValueError('actual outer owning class must be physically unchanged')
        wanted=list(coordinate(prior));wanted[2]+=shift;wanted[3]+=shift
        matches=[(i,r)for i,r in enumerate(rows)if coordinate(r)==tuple(wanted)]
        if len(matches)!=1:raise ValueError('one exact current diagnostic with shifted lines only')
        i,row=matches[0]
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE':raise ValueError('no duplicate or overridden disposition')
        if row['rule']=='UseConcurrentHashMap':reason='Method-confined mutable builder becomes Map.copyOf in immutable snapshot constructor; no concurrent mutable escape. Concurrent-access premise does not hold for this exact map.'
        elif row['rule']=='NullAssignment':reason='Finally clears pending only after current != null and current.closed(); otherwise exact pending owner is retained. Null means no remaining close obligation, not successful runtime recovery proof.'
        else:reason='Installed J2EE-managed-thread premise is inapplicable to approved standalone Java process. This finding does not certify thread safety, owned cleanup or real VM success.'
        result=copy.deepcopy(row);result.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition=prior['status'],priorFindingId=prior['findingId'],priorReason=prior.get('reason',''),reason=reason,historicalCaseIds=[v['testId']for v in prior.get('wholeCaseRefs',[])],currentWholeCaseRefs=[],currentWholeJoinPending=True,newDispositionCreated=False,rawWarningRetained=True,reviewProof=record,currentPhysicalProofSha256=sha(cp))
        rows[i]=result;scope_proofs[path]=record;updates.append({'findingId':row['findingId'],'rule':row['rule'],'sourcePath':path,'line':row['beginline'],'reason':reason})
    actual=Counter(r['rule']for r in updates)
    if actual!=Counter({'DoNotUseThreads':10,'UseConcurrentHashMap':1,'NullAssignment':1}):raise ValueError('all and only twelve held scopes')
    hits=[(i,r)for i,r in enumerate(rows)if r['sourcePath']==WEB_PATH and r['rule']=='UseProperClassLoader']
    if len(hits)!=1:raise ValueError('exact one classloader finding')
    i,row=hits[0];text=(ROOT/WEB_PATH).read_text();line=int(row['beginline'])
    if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or text.splitlines()[line-1].strip()!='context.setParentClassLoader(WebHttpServer.class.getClassLoader());':raise ValueError('exact explicit own-release loader statement')
    service=ROOT/'src/deployment/systemd/schubert-nk-web.service.template'
    if '-cp /opt/schubert-nk/current/operations/batch.jar:/opt/schubert-nk/current/operations/lib/*'not in service.read_text():raise ValueError('standalone approved JVM classpath contract')
    result=copy.deepcopy(row);result.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition='CONTEXT_NOT_APPLICABLE',reason='Installed rule explicitly assumes J2EE container context loader. SS311/343 standalone own JVM and embedded Tomcat deliberately select the release WebHttpServer loader as parent. Foreign WAR/EAR/plugin/TCCL hosting compatibility is not claimed. No rule suppression or runtime/coverage certification.',newDispositionCreated=True,currentWholeCaseRefs=[],currentWholeJoinPending=True,rawWarningRetained=True,ruleDefinition=rules['UseProperClassLoader'],deploymentSourceSha256=sha(service),owningPhysicalClassSha256=proof['auxClassHashes']['web:'+WEB_PATH.split('/src/main/java/')[1][:-5]+'.class'])
    rows[i]=result
    counts=Counter(r['status']for r in rows)
    if len(rows)!=1582 or len({r['findingId']for r in rows})!=1582 or counts['SOURCE_REBOUND_CURRENT_WHOLE_PENDING']!=384:raise ValueError('all raw diagnostic identities preserved, exact384 pending')
    value={'actualExit':0,'source':SOURCE,'priorRebindSha256':sha(sp),'priorReviewSha256':sha(oldp),'currentSourceByteProofSha256':sha(cp),'installedPmdJarSha256':sha(jar),'installedRules':rules,'recheckedHeldDispositions':12,'newDispositionsCreated':1,'changedScopeProofs':scope_proofs,'recheckedFindings':updates,'newFindingId':row['findingId'],'currentRawFindings':1582,'statusCounts':dict(counts),'currentWholeJoinPending':True,'executedPtAdded':0,'ptAlternativeCompleted':0,'rawWarningsRemoved':0,'sourceCodeChanged':False,'analyzerReexecuted':False,'historicalPtImportedAsCurrent':False,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    os.umask(0o077);OUT.mkdir()
    for name,data in(('manifest.json',value),('findings.json',rows)):
        with(OUT/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in('actualExit','source','recheckedHeldDispositions','newDispositionsCreated','currentRawFindings','statusCounts','F03Accepted')}))
    print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'findingsSha256':sha(OUT/'findings.json')}))


if __name__=='__main__':main()
