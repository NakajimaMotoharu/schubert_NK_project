"""Source-bound J2EE-rule applicability review only; no suppression or thread-safety claim."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SOURCE='a19a9f7d940b4f9fba47e51bd9be675f4420401b'
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
PRIOR=BASE/'PG5506-snapshot-ownership-review-v1/manifest.json'
JAR=ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
MODULES=('protocol','storage','bootstrap','api','web','batch')
FORBIDDEN=('jakarta.enterprise.concurrent','javax.enterprise.concurrent','jakarta.ejb','javax.ejb',
    'ManagedExecutorService','ManagedScheduledExecutorService','DefaultManagedExecutorService','@MessageDriven','@Stateless','@Stateful')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def descriptor(raw,artifact):
    root=ET.fromstring(raw);ns={'m':'http://maven.apache.org/POM/4.0.0'}
    if root.findtext('m:artifactId',namespaces=ns)!=artifact:raise ValueError('exact standalone project artifact')
    packaging=root.findtext('m:packaging',namespaces=ns)
    if packaging not in(None,'jar'):raise ValueError('WAR/EJB/container packaging requires a new applicability review')
    if any(token in raw for token in FORBIDDEN)or'jakarta.jakartaee-api'in raw:raise ValueError('managed enterprise runtime cannot inherit standalone disposition')
    return{'artifact':artifact,'packaging':packaging or'jar (Maven default)','sha256':sha(raw.encode())}


def rule():
    with zipfile.ZipFile(JAR)as archive:raw=archive.read('category/java/multithreading.xml')
    root=ET.fromstring(raw);nodes=[r for r in root if r.get('name')=='DoNotUseThreads']
    if len(nodes)!=1:raise ValueError('one installed rule definition')
    value=nodes[0];ns={'r':'http://pmd.sourceforge.net/ruleset/2.0.0'}
    text=value.findtext('r:description',namespaces=ns)or''
    if 'To be compliant to J2EE'not in value.get('message','')or'J2EE specification'not in text or'J2EE server'not in text:raise ValueError('J2EE-only premise must be explicit in primary installed definition')
    return{'name':value.get('name'),'version':'7.28.0','priority':value.get('priority')or value.findtext('r:priority',namespaces=ns),
        'message':value.get('message'),'description':text.strip(),'jarSha256':sha(JAR.read_bytes()),'rulesetEntrySha256':sha(raw),'isolatedRuleSha256':sha(ET.tostring(value))}


def architecture():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('fixed current Main/Test/config source first')
    poms={m:descriptor((ROOT/('src/schubert-nk-'+m+'/pom.xml')).read_text(),'schubert-nk-'+m)for m in MODULES}
    if any(token in p.read_text()for p in ROOT.glob('src/*/src/main/java/**/*.java')for token in FORBIDDEN):raise ValueError('enterprise-managed Main cannot inherit standalone context')
    units={}
    for role in('api','web','morning-controller'):
        path='src/deployment/systemd/schubert-nk-'+role+'.service.template';raw=(ROOT/path).read_text()
        if 'ExecStart='not in raw or'java'not in raw or'schubert-nk/current'not in raw:raise ValueError('actual own-process systemd launcher contract')
        units[path]=sha(raw.encode())
    entrypoints={}
    for module,name in(('api','api/bootstrap/ApiProcessMain.java'),('web','web/bootstrap/WebProcessMain.java'),('batch','batch/file/MorningProcessMain.java')):
        path='src/schubert-nk-'+module+'/src/main/java/dev/codex/schubert/nk/'+name;raw=(ROOT/path).read_bytes()
        if b'void main('not in raw:raise ValueError('own process entry, not a container-only component')
        entrypoints[path]=sha(raw)
    designs={};commit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()
    for path in('documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md',
        'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'):
        raw=subprocess.check_output(['git','show','origin/main:'+path],cwd=ROOT)
        if path.endswith('311_モジュール・package・class責務設計.md')and(b'Executable jar'not in raw or b'Library jar'not in raw):raise ValueError('approved executable/library architecture premise')
        if path.endswith('343_設定file・directory・初期data・migration・切戻し設計.md')and b'systemd'not in raw:raise ValueError('approved OS-owned lifecycle')
        designs[path]=sha(raw)
    return{'poms':poms,'ownUnitLaunchers':units,'ownProcessEntries':entrypoints,'approvedDesignCommit':commit,'approvedDesignHashes':designs,
        'embeddedServletFrameworkIsNotManagedJ2eeExecutorContract':True,'managedEnterpriseReferencesFound':0}


def main():
    raw=PRIOR.read_bytes()
    if sha(raw)!='bf739a63c02c95c7aba5b51a60c53a4d119a9acf01ae2de18ec8f4754563e270':raise ValueError('immutable historical raw classification input')
    previous=json.loads(raw);definition=rule();context=architecture();rows=[]
    for row in previous['findings']:
        if row['rule']!='DoNotUseThreads':continue
        path=ROOT/row['sourcePath'];data=path.read_bytes();lines=data.decode().splitlines(keepends=True)
        if row['status']!='NOT_REVIEWED'or sha(data)!=row['sourceSha256']:raise ValueError('each current finding source exactly equals its recorded raw diagnostic bytes')
        begin,end=int(row['beginline']),int(row['endline'])
        if not 0<begin<=end<=len(lines):raise ValueError('actual source span required')
        rows.append({k:row[k]for k in('findingId','rule','sourcePath','sourceSha256','beginline','endline','priority')}|
            {'sourceSpanSha256':sha(''.join(lines[begin-1:end]).encode()),'rawWarningRetained':True,'reviewDisposition':'NOT_APPLICABLE_J2EE_MANAGED_RUNTIME',
                'basis':'Rule prohibits app-managed threads for J2EE-managed deployment. SS311/343 require executable/library JARs and own systemd process lifecycles, not that managed-executor contract.',
                'threadSafetyCertified':False,'newDiagnosticReconciliationRequired':True})
    if len(rows)!=239 or len({r['findingId']for r in rows})!=239:raise ValueError('all239 original thread findings individually source-bound, no dropped row')
    value={'actualExit':0,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'operatorBranch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        'sourceSnapshot':SOURCE,'rawBaselineSource':previous['source'],'rawBaselineSha256':sha(raw),'ruleDefinition':definition,
        'architecture':context,'reviewedContextRows':239,'findings':rows,'originalOtherReviewsCopiedAsCurrent':False,
        'freshCurrentPmdDiagnosticRunClaimed':False,'freshDiagnosticReconciliationPending':True,'sourceCodeChanged':False,
        'ruleSuppressionAdded':False,'rawWarningsRemoved':0,'threadSafetyCertified':False,'globalOwnershipAccepted':False,'F03Accepted':False,
        'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'vmActions':0}
    out=BASE/'PG5554-thread-applicability-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':SOURCE,'reviewedContextRows':239,'sha256':sha((out/'manifest.json').read_bytes()),'freshDiagnosticReconciliationPending':True,'F03Accepted':False,'formalAccepted':False},sort_keys=True))


if __name__=='__main__':main()
