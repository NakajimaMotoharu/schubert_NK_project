"""Original4197/1669 qualification, no PT replay or held operational action."""
import hashlib
import inspect
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates
import pg6768_transfer_io_whole as whole
import pg6760_transfer_io_selected as selected


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote);anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:raise ValueError('one exact original export dimension guard')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6768', (4197, 646, 1669), 1))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6768')",1);compile(raw,'<original4197 export>','exec');return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one coverage export guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6768')",1),'<original4197 collector>','exec'),scope)
    return scope['collect'](*args,**kwargs)


def added_cases(source):
    selected.guard(source)
    changes=subprocess.check_output(['git','diff','--name-status',whole.OLD,source,'--',':(glob)src/*/src/test/java/**/*Test.java'],cwd=ROOT,text=True).splitlines()
    if changes!=['A\t'+selected.TEST]:raise ValueError('one eight-Test addition, every prior oracle unchanged')
    text=subprocess.check_output(['git','show',source+':'+selected.TEST],cwd=ROOT,text=True)
    result=[dict(module='batch',**{'class':selected.TEST.split('/src/test/java/')[1][:-5].replace('/','.')},
      caseNameSha256=hashlib.sha256(source_case_candidates(text,name)[0].encode()).hexdigest())for name in sorted(ordinary_names(text))]
    if len(result)!=8 or len(reader.expected_case_keys(result))!=8:raise ValueError('eight unique independent declarations')
    return result


def main():
    source=whole.original_source();run=W/whole.SLOT;op=run/'manifest.safe.json';o=json.loads(op.read_bytes())
    if not(o['source']==source and o['actualExit']==0 and o['result']['run']=='PG6768-six-v1' and o['result']['productionSource']==o['result']['sourceSnapshotHead']==source):raise ValueError('genuine4197 terminal, never replace missing or failed run')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('original Main/Test/gates fixed')
    begin=json.loads((run/'begin.safe.json').read_bytes());archive=run/'source.tar'
    if sha(archive)!=begin['archiveSha256']:raise ValueError('original archive identity')
    inputs={}
    with tarfile.open(archive)as tar:
        for member in tar:
            if member.isdir():continue
            p=PurePosixPath(member.name)
            if not member.isfile()or p.is_absolute()or'..'in p.parts or member.name in inputs:raise ValueError('unique regular original inputs')
            inputs[member.name]=hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    oldq=BASE/'PG6748-current4189-cases/qualification.json';cp=oldq.with_name('cases.json')
    if sha(oldq)!='491bbf38afd9008426bb1909ff1e45edb73c3254310939d4b020d1ebaa5b5821' or sha(cp)!='d13356eef6134f40988b254deca35396bf27ff251768c9fc0e53421a44a19640':raise ValueError('immutable4189 identities/physical map, not PASS import')
    expected=[{k:r[k]for k in ('module','class','caseNameSha256')}for r in json.loads(cp.read_bytes())]+added_cases(source)
    qp=BASE/'PG6766-transfer-io-original-v2/manifest.json';pp=W/'pg6766-transfer-io-original-v2/manifest.safe.json';q=json.loads(qp.read_bytes())
    if whole.QSHA is None or sha(qp)!=whole.QSHA or not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(27,10,1669)and sha(pp)==q['privateManifestSha256']):raise ValueError('same-source original27 all1669 qualified first')
    proof=json.loads(pp.read_bytes());main=reader.production_source_inputs(inputs)
    if len(main)!=851 or main!=proof['allSourceHashes']:raise ValueError('all851 original Main exact')
    owners=subprocess.check_output(['git','diff','--name-only',whole.OLD,source,'--',':(glob)src/*/src/main/java/**/*.java'],cwd=ROOT,text=True).splitlines()
    if owners!=[selected.MAIN]:raise ValueError('one necessary Transfer Main only')
    data=dict(source=source,campaign='PG6768',expectedCounts=[4197,646,1669],returnedOriginalResult=o['result'],archiveSha256=begin['archiveSha256'],allSourceInputs=inputs,expectedMainSourceInputs=main,expectedCases=expected,
      priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'],changedOwnerKeys=['batch:dev/codex/schubert/nk/batch/file/TransferCleanup.class'],
      physicalExpectedCounts=[1667,1669],physicalExpectedAdded=sorted(selected.ADDED),expectedCurrentMain=proof['allPhysicalMainSha256'],includeCoverageXml=True)
    return collect(data,op,'pg6770-original4197-transfer-artifacts-v1','/home/mini/schubert-nk-pgpt/transfer/PG6770-original4197-transfer-v1','PG6768-current4197-cases')


def read_whole():
    qp=BASE/'PG6768-current4197-cases/qualification.json';cp=qp.with_name('cases.json')
    rp=W/'pg6770-original4197-transfer-artifacts-v1/manifest.safe.json';op=W/whole.SLOT/'manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes())for p in(qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==whole.original_source()
      and(q['tests'],q['suites'],q['mainClasses'])==(4197,646,1669)and q['returnedOriginalTerminalExact']and q['currentOriginalXmlQualified']
      and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']and r['originalManifestSha256']==sha(op)
      and r['publicQualificationSha256']==sha(qp)and r['publicCasesSha256']==sha(cp)):raise ValueError('genuine4197 terminal/receipt/XML required')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('Main/Test/gates fixed')
    if len(q['allSourceHashes'])!=851 or {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=q['allSourceHashes']:raise ValueError('all actual851 exact Main')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4197 or any(c['source']!=q['productionSource']or c['result']!='PASS_ORIGINAL_XML'for c in cases):raise ValueError('all4197 actual original case identities')
    return qp,q,cases


if __name__=='__main__':main()
