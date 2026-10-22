"""Collect genuine original4189 artifacts; no replacement PT or held runtime action."""
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
from pg6748_owned_reader_whole import OLD,TESTS,SLOT,original_source,QSHA

physical_difference=reader.physical_difference


def unchanged_physical(before,after,owners,expected_counts=(1666,1667),expected_added=None):
    if owners:
        return physical_difference(before,after,owners,expected_counts,expected_added)
    if expected_added!=[] or (len(before),len(after))!=tuple(expected_counts) or before!=after:
        raise ValueError('Test-only whole requires exact complete original physical map, no added/removed/changed class')
    return [],[],len(after)


def emitted(data_hash,remote):
    raw=reader.emitted(data_hash,remote);anchor="('PG6490', (4064, 612, 1667), 1))"
    if raw.count(anchor)!=1 or raw.count("'PG6490')")!=1:raise ValueError('one original export/count binding')
    raw=raw.replace(anchor,"('PG6490', (4064, 612, 1667), 1), ('PG6748', (4189, 645, 1667), 0))",1)
    raw=raw.replace("'PG6490')","'PG6490', 'PG6748')",1)
    call='changed, added, unchanged = physical_difference('
    terminal='\nprint(json.dumps(inspect_original(json.loads(p.read_bytes()))))'
    if raw.count(call)!=1 or raw.count(terminal)!=1:raise ValueError('one physical verification and one original reader terminal')
    raw=raw.replace(call,'changed, added, unchanged = unchanged_physical(',1)
    raw=raw.replace(terminal,'\n'+inspect.getsource(unchanged_physical)+terminal,1)
    compile(raw,'<original4189 export>','exec');return raw


def collect(*args,**kwargs):
    raw=inspect.getsource(reader.collect)
    if raw.count("'PG6490')")!=1:raise ValueError('one original coverage export guard')
    scope={**vars(reader),'emitted':emitted}
    exec(compile(raw.replace("'PG6490')","'PG6490', 'PG6748')",1),'<original4189 collect>','exec'),scope)
    return scope['collect'](*args,**kwargs)


def added_cases(source):
    changes=subprocess.check_output(['git','diff','--name-status',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines()
    if set(changes)!={'A\t'+p for p in TESTS}:raise ValueError('two Test additions only, no old oracle/Main edits')
    result=[]
    for path in sorted(TESTS):
        text=subprocess.check_output(['git','show',source+':'+path],cwd=ROOT,text=True)
        for method in sorted(ordinary_names(text)):
            result.append(dict(module=path.split('/')[1].removeprefix('schubert-nk-'),
              **{'class':path.split('/src/test/java/')[1][:-5].replace('/','.')},
              caseNameSha256=hashlib.sha256(source_case_candidates(text,method)[0].encode()).hexdigest()))
    if len(result)!=5 or len(reader.expected_case_keys(result))!=5:raise ValueError('five unique independent new declarations')
    return result


def main():
    source=original_source();run=W/SLOT;op=run/'manifest.safe.json';o=json.loads(op.read_bytes())
    if not(o['source']==source and o['actualExit']==0 and o['result']['run']=='PG6748-six-v1'
           and o['result']['productionSource']==o['result']['sourceSnapshotHead']==source):raise ValueError('genuine original4189 terminal, not begin or old PASS')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('original source/Test/gates fixed')
    begin=json.loads((run/'begin.safe.json').read_bytes());archive=run/'source.tar'
    if sha(archive)!=begin['archiveSha256']:raise ValueError('original archive identity')
    inputs={}
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():continue
            p=PurePosixPath(member.name)
            if not member.isfile() or p.is_absolute() or '..' in p.parts or member.name in inputs:raise ValueError('unique regular input')
            inputs[member.name]=hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    oldq=BASE/'PG6726-current4184-cases/qualification.json';oldcases=oldq.with_name('cases.json')
    if sha(oldq)!='f131379f73f9098237fc600052b58d1c1172778c75c3b36e4e96090914662514' or sha(oldcases)!='971b309633c17805d3684fd504de0a6c860f72d3ef1ae9b24c8c6ddc8015817e':raise ValueError('old semantic identities/maps immutable, not imported PASS')
    expected=[{k:r[k] for k in ('module','class','caseNameSha256')}for r in json.loads(oldcases.read_bytes())]+added_cases(source)
    qp=BASE/'PG6746-request-read-original-v1/manifest.json';pp=W/'pg6746-request-read-original-v1/manifest.safe.json';q=json.loads(qp.read_bytes())
    if QSHA is None or sha(qp)!=QSHA or not(q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'])==(47,11) and sha(pp)==q['privateManifestSha256']):raise ValueError('actual current47 original qualification')
    proof=json.loads(pp.read_bytes());main=reader.production_source_inputs(inputs)
    if len(main)!=851 or main!=proof['allSourceHashes']:raise ValueError('all851 exact original Main')
    data=dict(source=source,campaign='PG6748',expectedCounts=[4189,645,1667],returnedOriginalResult=o['result'],archiveSha256=begin['archiveSha256'],allSourceInputs=inputs,expectedMainSourceInputs=main,expectedCases=expected,
      priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'],changedOwnerKeys=[],physicalExpectedCounts=[1667,1667],physicalExpectedAdded=[],expectedCurrentMain=proof['allPhysicalMainSha256'],includeCoverageXml=True)
    return collect(data,op,'pg6750-original4189-owned-artifacts-v1','/home/mini/schubert-nk-pgpt/transfer/PG6750-original4189-owned-v1','PG6748-current4189-cases')


def read_whole():
    qp=BASE/'PG6748-current4189-cases/qualification.json';cp=qp.with_name('cases.json')
    rp=W/'pg6750-original4189-owned-artifacts-v1/manifest.safe.json';op=W/SLOT/'manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes())for p in (qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']==original_source()
      and(q['tests'],q['suites'],q['mainClasses'])==(4189,645,1667) and q['returnedOriginalTerminalExact'] and q['currentOriginalXmlQualified']
      and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed'] and r['originalManifestSha256']==sha(op)
      and r['publicQualificationSha256']==sha(qp) and r['publicCasesSha256']==sha(cp)):raise ValueError('genuine4189 terminal/receipt/XML required')
    if subprocess.check_output(['git','diff',q['productionSource'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('current source/Test/gates fixed')
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=q['allSourceHashes']:raise ValueError('all851 current Main fixed')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4189 or any(c['source']!=q['productionSource'] or c['result']!='PASS_ORIGINAL_XML' for c in cases):raise ValueError('all genuine4189 identities')
    return qp,q,cases


if __name__=='__main__':main()
