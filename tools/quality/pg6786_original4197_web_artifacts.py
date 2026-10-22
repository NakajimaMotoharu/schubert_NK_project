"""Original4197 Web artifacts; no PT replay or held operations."""
import hashlib
import inspect
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
import pg6784_web_management_result_whole as whole
import pg6780_web_management_result_selected as selected
from pg5940_private_lock_compile import ROOT,W,BASE,sha


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote);anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:raise ValueError('one original4197 Web tuple binding')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6784', (4197, 646, 1669), 1))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6784')",1);compile(raw,'<original4197 Web>','exec');return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one current original coverage binding')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6784')",1),'<original4197 Web collector>','exec'),scope)
    return scope['collect'](*args,**kwargs)


def main():
    source=whole.original_source();run=W/whole.SLOT;op=run/'manifest.safe.json';o=json.loads(op.read_bytes())
    if not(o['source']==source and o['actualExit']==0 and o['result']['run']=='PG6784-six-v1'and o['result']['productionSource']==o['result']['sourceSnapshotHead']==source):raise ValueError('genuine4197 Web terminal required')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('original Main/Test/gates fixed')
    begin=json.loads((run/'begin.safe.json').read_bytes());archive=run/'source.tar'
    if sha(archive)!=begin['archiveSha256']:raise ValueError('original fixed source archive')
    inputs={}
    with tarfile.open(archive)as tar:
        for m in tar:
            if m.isdir():continue
            p=PurePosixPath(m.name)
            if not m.isfile()or p.is_absolute()or'..'in p.parts or m.name in inputs:raise ValueError('unique regular original inputs')
            inputs[m.name]=hashlib.sha256(tar.extractfile(m).read()).hexdigest()
    oldq=BASE/'PG6768-current4197-cases/qualification.json';cp=oldq.with_name('cases.json')
    if sha(oldq)!='b4b22a3e1d8d2c1d0a433c0fb3fa3fb2a77c9aed795cd56e64c8f5947d7122e9'or sha(cp)!='ec82f71d9b60937c3cd0305245575ef0bc02e9bb54468c8b48d1ea568c507494':raise ValueError('immutable prior cases/map, not PASS import')
    if subprocess.check_output(['git','diff',selected.OLD,source,'--',':(glob)src/*/src/test/java/**/*'],cwd=ROOT):raise ValueError('all4197 old oracle inputs unchanged')
    expected=[{k:r[k]for k in ('module','class','caseNameSha256')}for r in json.loads(cp.read_bytes())]
    qp=BASE/'PG6782-web-management-result-original-v1/manifest.json';pp=W/'pg6782-web-management-result-original-v1/manifest.safe.json';q=json.loads(qp.read_bytes())
    if whole.QSHA is None or sha(qp)!=whole.QSHA or not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(28,10,1669)and sha(pp)==q['privateManifestSha256']):raise ValueError('same-source original28 all1669 qualified first')
    proof=json.loads(pp.read_bytes());main=reader.production_source_inputs(inputs)
    if len(main)!=851 or main!=proof['allSourceHashes']:raise ValueError('all851 Main exact')
    selected.guard(source)
    data=dict(source=source,campaign='PG6784',expectedCounts=[4197,646,1669],returnedOriginalResult=o['result'],archiveSha256=begin['archiveSha256'],allSourceInputs=inputs,expectedMainSourceInputs=main,expectedCases=expected,
      priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'],changedOwnerKeys=['web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class'],
      physicalExpectedCounts=[1669,1669],physicalExpectedAdded=[],expectedCurrentMain=proof['allPhysicalMainSha256'],includeCoverageXml=True)
    return collect(data,op,'pg6786-original4197-web-artifacts-v1','/home/mini/schubert-nk-pgpt/transfer/PG6786-original4197-web-v1','PG6784-current4197-cases')


def read_whole():
    qp=BASE/'PG6784-current4197-cases/qualification.json';cp=qp.with_name('cases.json')
    rp=W/'pg6786-original4197-web-artifacts-v1/manifest.safe.json';op=W/whole.SLOT/'manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes())for p in(qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==whole.original_source()
      and(q['tests'],q['suites'],q['mainClasses'])==(4197,646,1669)and q['returnedOriginalTerminalExact']and q['currentOriginalXmlQualified']
      and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']and r['originalManifestSha256']==sha(op)
      and r['publicQualificationSha256']==sha(qp)and r['publicCasesSha256']==sha(cp)):raise ValueError('all original4197 terminal/receipt/XML')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('Main/Test/gates fixed')
    if len(q['allSourceHashes'])!=851 or {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=q['allSourceHashes']:raise ValueError('all actual851 exact Main')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4197 or any(c['source']!=q['productionSource']or c['result']!='PASS_ORIGINAL_XML'for c in cases):raise ValueError('all4197 original identities')
    return qp,q,cases


if __name__=='__main__':main()
