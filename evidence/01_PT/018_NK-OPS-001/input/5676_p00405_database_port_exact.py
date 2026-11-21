import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

R=Path('evidence/01_PT/018_NK-OPS-001/evidence')
out=R/'PG41436-p00405-database-port-exact-v1'
s=next(Path('documents/400_PGPT/470_PMO').glob('601_*/1809_*'))
context=json.loads(s.read_bytes())['values']
core=context['productionCoreMain']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()

def pin(path):
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def find(n):
    return next(R.glob(n+'-*/manifest.json'))

def data(n):
    return json.loads(find(n).read_bytes())

def blob(commit,path):
    return subprocess.check_output(['git','rev-parse',f'{commit}:{path}'],text=True).strip()

def write(path,value):
    with path.open('x') as fd:
        json.dump(value,fd,ensure_ascii=False,indent=2)
        fd.write('\n')

old_tree=data('PG39862')
old_unit=data('PG39866')
old=data('PG39868')
archive=data('PG41322')['packagingProof']['artifacts']
assert {'unit':0,'execinfo':0} == old_unit['actualExits']
assert old_unit['source']==old['source']==old_tree['sourceCore']
assert old['unitSource']==old_unit['unitSource']
assert old['tests']==32 and sum(old[key] for key in ('failures','errors','skipped','notRun'))==0
items=[name.replace('.','/') for name in old_unit['tests']]
fixture_paths=['src/schubert-nk-bootstrap/src/test/java/'+name+'.java' for name in items]
fixture_blobs={p:blob(old['unitSource'],p) for p in fixture_paths}
assert fixture_blobs=={p:blob(head,p) for p in fixture_paths}
allowed={'bootstrap':{
 'dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures',
 'dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraph',
 'dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseAdmission',
 'dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseSource',
 'dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseSource$Connector',
 'dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseSource$StateAction'},
'storage':{
 'dev/codex/schubert/nk/storage/ServiceConfigFiles$Service',
 'dev/codex/schubert/nk/storage/StorageIoException',
 'dev/codex/schubert/nk/storage/StorageIoException$Reason'}}
assert set().union(*allowed.values())==old['classes'].keys()
members=[]
for module,names in sorted(allowed.items()):
    current=archive[module]
    jar=Path(current['artifact']['path'])
    assert pin(jar)['sha256']==current['artifact']['sha256']
    with ZipFile(jar) as z:
        assert len({info.filename for info in z.infolist()})==len(z.infolist())
        for name in sorted(names):
            member=name+'.class'
            source=f'src/schubert-nk-{module}/src/main/java/{name.split("$",1)[0]}.java'
            assert blob(current['archiveSource'],source)==blob(core,source)==blob(old['source'],source)
            actual=hashlib.sha256(z.read(member)).hexdigest()
            expected=old_tree['physicalClassHashes'][module][member]
            members.append(dict(module=module,entry=member,currentClassSha256=actual,oldClassSha256=expected,
                exact=actual==expected,source=source,oldRuntimeCounters=old['classes'][name]['counters']))
observed_xml=Path(old['actualWholeCases']['path'])
assert pin(observed_xml)==old['actualWholeCases']
tests=ET.parse(observed_xml).getroot().findall('testcase')
assert len(tests)==32 and all(not x.findall('failure') and not x.findall('error') and not x.findall('skipped') for x in tests)
assert {x.attrib['classname'] for x in tests}==set(old_unit['tests'])
original_exec=find('PG39866').parent/'jacoco.exec'
assert pin(original_exec)['sha256']==old_unit['files']['jacoco.exec']
unmatched=[row['entry'] for row in members if not row['exact']]
target=[row for row in members if Path(row['entry']).name in ('ServiceDatabaseAdmission.class','ServiceDatabaseSource.class')]
assert len(target)==2
target_missed={Path(row['entry']).stem:{key:row['oldRuntimeCounters'][key]['missed'] for key in ('LINE','METHOD','CLASS','BRANCH','INSTRUCTION')} for row in target}
out.mkdir()
manifest=dict(run=out.name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),core=core,
    originalProductCore=old['source'],originalUnitSource=old['unitSource'],
    sources=[pin(find(n)) for n in ('PG39862','PG39866','PG39868','PG41322')],
    originalJUnitOutcome=old['actualWholeCases'],originalSingleExec=pin(original_exec),
    currentFixtureBlobs=fixture_blobs,eligibleNineMembers=members,exactPhysical=len(members)-len(unmatched),
    differingPhysical=unmatched,localTwoTargetHistoricalCounterMisses=target_missed,
    metadataReadFirstExit=1, metadataReadFirstCause='Earlier static stage PG39864 had pre-fix fixture source so was removed from original unit identity rather than counted as the final fixture.',
    relatedOriginalTestCasesCorresponded=0 if unmatched else len(tests),newProductTests=0,
    separateOwners='WBS-P018-05 local supporting witnesses for WBS-P004-05 JDBC; no added ownership or cost',
    currentCoverageMeasured=0,originalCasesRerun=0,newCoverageUnion=False,whole451=False,formalDelta=0,
    next=['API pool and actual transaction/DB scope remains held', 'Complete F02/F03 and 451 and unique owners before formal acceptance'],
    auditTool=pin(Path(__file__).resolve().relative_to(Path.cwd())))
write(out/'manifest.json',manifest)
print('exact',manifest['exactPhysical'],'different',unmatched,'qualified original cases',manifest['relatedOriginalTestCasesCorresponded'],'local prior counter misses',target_missed)
