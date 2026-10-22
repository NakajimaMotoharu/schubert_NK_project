"""Original4209 only: old4203 identities plus six declarations, never PASS addition or replay."""
import hashlib
import inspect
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
import pg6862_web_deadline_whole as whole
import pg6850_web_deadline_selected as selected
import pg6844_observation_boundaries_selected as data
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote);anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:raise ValueError('one original4209 dimension binding')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6862', (4209, 653, 1669), 1))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6862')",1);compile(raw,'<original4209 export>','exec');return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one original coverage guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6862')",1),'<original4209 collector>','exec'),scope);return scope['collect'](*args,**kwargs)


def added_cases(source):
    selected.green_guard(source);tests=set(data.TESTS)|{selected.TEST}
    changes=subprocess.check_output(['git','diff','--name-status','4c0343a55b5fe41dad766a520558363e81f01541',source,'--',':(glob)src/*/src/test/java/**/*Test.java'],cwd=ROOT,text=True).splitlines()
    if set(changes)!={'A\t'+p for p in tests}or len(changes)!=3:raise ValueError('only three new Test files, all old oracle bytes fixed')
    rows=[]
    for path in sorted(tests):
        text=subprocess.check_output(['git','show',source+':'+path],cwd=ROOT,text=True)
        rows.extend(dict(module=path.split('/')[1].removeprefix('schubert-nk-'),**{'class':path.split('/src/test/java/')[1][:-5].replace('/','.')},
          caseNameSha256=hashlib.sha256(source_case_candidates(text,n)[0].encode()).hexdigest())for n in ordinary_names(text))
    if len(rows)!=6:raise ValueError('six independent new JUnit declarations, not vector counts')
    return rows


def main():
    source=whole.original_source();run=W/whole.SLOT;op=run/'manifest.safe.json';o=json.loads(op.read_bytes())
    if not(o['source']==source and o['actualExit']==0 and o['result']['run']=='PG6862-six-v1'and o['result']['productionSource']==o['result']['sourceSnapshotHead']==source):raise ValueError('genuine4209 original terminal required')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('original Main/Test/gates remain fixed')
    begin=json.loads((run/'begin.safe.json').read_bytes());archive=run/'source.tar'
    if sha(archive)!=begin['archiveSha256']:raise ValueError('original archive')
    inputs={}
    with tarfile.open(archive)as tar:
        for item in tar:
            if item.isdir():continue
            path=PurePosixPath(item.name)
            if not item.isfile()or path.is_absolute()or'..'in path.parts or item.name in inputs:raise ValueError('unique regular original inputs')
            inputs[item.name]=hashlib.sha256(tar.extractfile(item).read()).hexdigest()
    oldq=BASE/'PG6828-current4203-cases/qualification.json';cp=oldq.with_name('cases.json')
    if sha(oldq)!='87d3de1b887514b10838d3cef748e9421f17574c87ae89a37f5b616a8e1f4dc0'or sha(cp)!='88b3f5061c56b9665061d888d846763ad2a8affd17730e56a0b440bb5a0895dc':raise ValueError('fixed old4203 identity map, not PASS import')
    expected=[{k:r[k]for k in('module','class','caseNameSha256')}for r in json.loads(cp.read_bytes())]+added_cases(source)
    qp=BASE/'PG6854-web-deadline-original-v1/manifest.json';pp=W/'pg6854-web-deadline-original-v1/manifest.safe.json';q=json.loads(qp.read_bytes())
    if whole.QSHA is None or sha(qp)!=whole.QSHA or not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(42,15,1669)and sha(pp)==q['privateManifestSha256']):raise ValueError('same-source original42 first')
    proof=json.loads(pp.read_bytes());main=reader.production_source_inputs(inputs)
    if len(main)!=851 or main!=proof['allSourceHashes']:raise ValueError('all851 Main exact')
    payload=dict(source=source,campaign='PG6862',expectedCounts=[4209,653,1669],returnedOriginalResult=o['result'],archiveSha256=begin['archiveSha256'],allSourceInputs=inputs,expectedMainSourceInputs=main,expectedCases=expected,
      priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'],changedOwnerKeys=['web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class'],
      physicalExpectedCounts=[1669,1669],physicalExpectedAdded=[],expectedCurrentMain=proof['allPhysicalMainSha256'],includeCoverageXml=True)
    return collect(payload,op,'pg6864-original4209-artifacts-v1','/home/mini/schubert-nk-pgpt/transfer/PG6864-original4209-v1','PG6862-current4209-cases')


def read_whole():
    qp=BASE/'PG6862-current4209-cases/qualification.json';cp=qp.with_name('cases.json');rp=W/'pg6864-original4209-artifacts-v1/manifest.safe.json';op=W/whole.SLOT/'manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes())for p in(qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==whole.original_source()
      and(q['tests'],q['suites'],q['mainClasses'])==(4209,653,1669)and q['returnedOriginalTerminalExact']and q['currentOriginalXmlQualified']
      and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']and r['originalManifestSha256']==sha(op)
      and r['publicQualificationSha256']==sha(qp)and r['publicCasesSha256']==sha(cp)):raise ValueError('all genuine original4209 receipt/XML')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('Main/Test/gates fixed')
    if len(q['allSourceHashes'])!=851 or{p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=q['allSourceHashes']:raise ValueError('all current actual851 Main exact')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4209 or any(c['source']!=q['productionSource']or c['result']!='PASS_ORIGINAL_XML'for c in cases):raise ValueError('all original4209 case identities')
    return qp,q,cases


if __name__=='__main__':main()
