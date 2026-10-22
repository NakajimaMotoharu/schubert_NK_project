"""Genuine combined4202 artifacts, no test replay or held operational actions."""
import hashlib
import inspect
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
import pg6802_web_correlation_whole as whole
import pg6806_correlation_positive_selected as selected
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote);anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:raise ValueError('one original4202 dimension binding')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6802', (4202, 649, 1669), 1))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6802')",1);compile(raw,'<original4202 export>','exec');return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one current original coverage guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6802')",1),'<original4202 collector>','exec'),scope);return scope['collect'](*args,**kwargs)


def added_cases(source):
    selected.guard(source)
    changes=subprocess.check_output(['git','diff','--name-status',selected.OLD,source,'--',':(glob)src/*/src/test/java/**/*Test.java'],cwd=ROOT,text=True).splitlines()
    if set(changes)!={'A\t'+p for p in selected.TESTS}:raise ValueError('exact three additions, every prior oracle unchanged')
    result=[]
    for p in sorted(selected.TESTS):
        text=subprocess.check_output(['git','show',source+':'+p],cwd=ROOT,text=True)
        for name in sorted(ordinary_names(text)):
            result.append(dict(module='batch',**{'class':p.split('/src/test/java/')[1][:-5].replace('/','.')},caseNameSha256=hashlib.sha256(source_case_candidates(text,name)[0].encode()).hexdigest()))
    if len(result)!=5 or len(reader.expected_case_keys(result))!=5:raise ValueError('all five unique independent declarations')
    return result


def main():
    source=whole.original_source();run=W/whole.SLOT;op=run/'manifest.safe.json';o=json.loads(op.read_bytes())
    if not(o['source']==source and o['actualExit']==0 and o['result']['run']=='PG6802-six-v1'and o['result']['productionSource']==o['result']['sourceSnapshotHead']==source):raise ValueError('genuine4202 terminal required')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('all original Main/Test/gates fixed')
    begin=json.loads((run/'begin.safe.json').read_bytes());archive=run/'source.tar'
    if sha(archive)!=begin['archiveSha256']:raise ValueError('original source archive identity')
    inputs={}
    with tarfile.open(archive)as tar:
        for m in tar:
            if m.isdir():continue
            p=PurePosixPath(m.name)
            if not m.isfile()or p.is_absolute()or'..'in p.parts or m.name in inputs:raise ValueError('unique regular original inputs')
            inputs[m.name]=hashlib.sha256(tar.extractfile(m).read()).hexdigest()
    oldq=BASE/'PG6784-current4197-cases/qualification.json';cp=oldq.with_name('cases.json')
    if sha(oldq)!='0e7d0f359c06b1fa33a3352cc38c63304a9cdd3d284884530f29a100bf7d8fe4'or sha(cp)!='80e1b52649598deab72ca5c3de269bcaf83190c9e3e56e7192135371f7361297':raise ValueError('immutable prior4197 identity/map, not PASS import')
    expected=[{k:r[k]for k in ('module','class','caseNameSha256')}for r in json.loads(cp.read_bytes())]+added_cases(source)
    qp=BASE/'PG6808-web-correlation-original-v2/manifest.json';pp=W/'pg6808-web-correlation-original-v2/manifest.safe.json';q=json.loads(qp.read_bytes())
    if whole.QSHA is None or sha(qp)!=whole.QSHA or not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(48,16,1669)and sha(pp)==q['privateManifestSha256']):raise ValueError('same-source original48 first')
    proof=json.loads(pp.read_bytes());main=reader.production_source_inputs(inputs)
    if len(main)!=851 or main!=proof['allSourceHashes']:raise ValueError('all851 Main exact')
    data=dict(source=source,campaign='PG6802',expectedCounts=[4202,649,1669],returnedOriginalResult=o['result'],archiveSha256=begin['archiveSha256'],allSourceInputs=inputs,expectedMainSourceInputs=main,expectedCases=expected,
      priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'],changedOwnerKeys=['web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class'],
      physicalExpectedCounts=[1669,1669],physicalExpectedAdded=[],expectedCurrentMain=proof['allPhysicalMainSha256'],includeCoverageXml=True)
    return collect(data,op,'pg6804-original4202-artifacts-v1','/home/mini/schubert-nk-pgpt/transfer/PG6804-original4202-v1','PG6802-current4202-cases')


def read_whole():
    qp=BASE/'PG6802-current4202-cases/qualification.json';cp=qp.with_name('cases.json');rp=W/'pg6804-original4202-artifacts-v1/manifest.safe.json';op=W/whole.SLOT/'manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes())for p in(qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==whole.original_source()
      and(q['tests'],q['suites'],q['mainClasses'])==(4202,649,1669)and q['returnedOriginalTerminalExact']and q['currentOriginalXmlQualified']
      and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']and r['originalManifestSha256']==sha(op)
      and r['publicQualificationSha256']==sha(qp)and r['publicCasesSha256']==sha(cp)):raise ValueError('all genuine original4202 receipt/XML')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('Main/Test/gates fixed')
    if len(q['allSourceHashes'])!=851 or {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=q['allSourceHashes']:raise ValueError('all actual851 exact Main')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4202 or any(c['source']!=q['productionSource']or c['result']!='PASS_ORIGINAL_XML'for c in cases):raise ValueError('all4202 original case identities')
    return qp,q,cases


if __name__=='__main__':main()
