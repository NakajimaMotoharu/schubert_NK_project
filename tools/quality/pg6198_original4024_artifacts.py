"""Read only original4024 artifacts, no regression replay or actual VM/runtime operation."""
import hashlib
import json
import subprocess
import tarfile
from pathlib import PurePosixPath
import pg6042_original3976_artifacts as reader
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6193_management_primary_qualification_v2 import original_source
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates

OLD='acb5fe9c375ede57f5d15fc5fc392f2197c910d4'


def new_case_identities(source):
    changes=subprocess.check_output(['git','diff','--name-status',OLD,source,'--',':(glob)src/*/src/test/java/**/*Test.java'],cwd=ROOT,text=True).splitlines()
    added=[]
    for change in changes:
        status,path=change.split('\t')
        if status not in ('A','M'):raise ValueError('no removed/renamed Test identities')
        text=subprocess.check_output(['git','show',source+':'+path],cwd=ROOT,text=True)
        current=ordinary_names(text)
        previous=set() if status=='A' else ordinary_names(subprocess.check_output(['git','show',OLD+':'+path],cwd=ROOT,text=True))
        if not previous<=current:raise ValueError('prior whole method identities retained; no successful Test removal')
        module=path.split('/')[1].removeprefix('schubert-nk-')
        cls=path.split('/src/test/java/')[1][:-5].replace('/','.')
        for method in sorted(current-previous):
            # Surefire's ordinary zero-arg name is the first lexical candidate; Path is explicit.
            display=source_case_candidates(text,method)[0]
            added.append(dict(module=module,**{'class':cls},caseNameSha256=hashlib.sha256(display.encode()).hexdigest()))
    if len(added)!=36 or len(reader.expected_case_keys(added))!=36:
        raise ValueError('exact36 new source declarations, not PASS arithmetic')
    return added


def main():
    source=original_source();run=W/'pg6196-management-ownership-six-v1'
    original_path=run/'manifest.safe.json';original=json.loads(original_path.read_bytes())
    if not (original['source']==source and original['actualExit']==0 and original['result']['run']=='PG6196-six-v1'
            and original['result']['productionSource']==original['result']['sourceSnapshotHead']==source):
        raise ValueError('genuine original4024 terminal required; never start again for missing result')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('original source/Test/gates fixed')
    begin=json.loads((run/'begin.safe.json').read_bytes());archive=run/'source.tar'
    if sha(archive)!=begin['archiveSha256']:raise ValueError('original archive identity')
    inputs={}
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():continue
            path=PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or member.name in inputs:
                raise ValueError('unique regular original archive inputs')
            inputs[member.name]=hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    oldq=BASE/'PG6118-current3988-cases/qualification.json';oldcases=oldq.with_name('cases.json')
    if sha(oldq)!='c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23' or sha(oldcases)!='fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47':
        raise ValueError('immutable prior case identities and physical map; no result transfer')
    expected=[{k:r[k] for k in ('module','class','caseNameSha256')} for r in json.loads(oldcases.read_bytes())]+new_case_identities(source)
    qp=BASE/'PG6193-management-primary-qualification-v2/manifest.json';private=W/'pg6193-management-primary-qualification-v2/manifest.safe.json'
    q=json.loads(qp.read_bytes())
    if not(q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'])==(60,20) and sha(private)==q['privateManifestSha256']):
        raise ValueError('actual source60 qualification and all physical inputs')
    proof=json.loads(private.read_bytes());main_inputs=reader.production_source_inputs(inputs)
    if len(main_inputs)!=851 or main_inputs!=proof['allSourceHashes']:raise ValueError('all851 original source map')
    owners=subprocess.check_output(['git','diff','--name-only',OLD,source,'--',':(glob)src/*/src/main/java/**/*.java'],cwd=ROOT,text=True).splitlines()
    if len(owners)!=13:raise ValueError('exact13 grouped Production owners since prior whole')
    keys=sorted(p.split('/')[1].removeprefix('schubert-nk-')+':'+p.split('/src/main/java/')[1][:-5]+'.class' for p in owners)
    data=dict(source=source,campaign='PG6196',expectedCounts=[4024,605,1667],
        returnedOriginalResult=original['result'],archiveSha256=begin['archiveSha256'],allSourceInputs=inputs,
        expectedMainSourceInputs=main_inputs,expectedCases=expected,
        priorFullMain=json.loads(oldq.read_bytes())['allPhysicalMainSha256'],changedOwnerKeys=keys,
        physicalExpectedCounts=[1667,1667],physicalExpectedAdded=[],expectedCurrentMain=proof['allPhysicalMainSha256'],includeCoverageXml=True)
    return reader.collect(data,original_path,'pg6198-original4024-artifacts-v1',
        '/home/mini/schubert-nk-pgpt/transfer/PG6198-original4024-v1','PG6196-current4024-cases')


if __name__=='__main__':main()
