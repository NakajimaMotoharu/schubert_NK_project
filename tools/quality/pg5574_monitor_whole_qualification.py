"""Original3904 result-only qualification: old3900 retained, four new, all11 raw changes."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from pyflakes.api import check
from lan_server import copy,run
import pg5552_snapshot_whole_qualification as previous
import pg5572_monitor_required_whole as entry
from pg5566_private_monitor_selected import EXPECTED_CHANGES

SOURCE,ROOT,W=entry.SOURCE,entry.ROOT,entry.W
SLOT='pg5574-monitor-whole-qualified-v1'
PHYSICAL_KINDS={k:'DECLARED_CODE_CHANGE'for k in EXPECTED_CHANGES}|{k:'DEBUG_ONLY'for k in(
 'batch:dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$2.class',
 'batch:dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient$NativeStart.class',
 'bootstrap:dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeGate.class',
 'bootstrap:dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeObservation.class',
 'bootstrap:dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission.class')}
ADDED={
 ('dev.codex.schubert.nk.batch.platform.BackupUnitStartClientTest','monitor001CallerLockCannotBlockOwnedStartStatus'),
 ('dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClientTest','monitor002CallerLockCannotBlockOwnedStopStatus'),
 ('dev.codex.schubert.nk.bootstrap.ServiceStartupAdmissionTest','monitor003CallerLockCannotBlockReadyInformationOrRelease'),
 ('dev.codex.schubert.nk.web.bootstrap.WebProcessLifetimeTest','monitor004CallerLockCannotBlockConfirmedLifetimeClose')}


def physical_difference(old,new,candidate):
    import re
    for value in(old,new,candidate):
        if type(value)is not dict or len(value)!=1664 or any(type(k)is not str or type(v)is not str or re.fullmatch('[0-9a-f]{64}',v)is None for k,v in value.items()):raise ValueError('all1664 actual fixed physical Main maps required')
    if set(old)!=set(new)or new!=candidate:raise ValueError('no missing/additional/unbuilt Main or source mismatch')
    changed={k for k in old if old[k]!=new[k]}
    if changed!=set(PHYSICAL_KINDS):raise ValueError('exact six code plus five debug raw differences; none discarded')
    return[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(changed)],1653


def qualifier_source():
    raw=previous.qualifier_source()
    for before,after in(("out = base / 'runs/PG5550-six-v1'","out = base / 'runs/PG5572-six-v1'"),
        ("source = base / 'source-full-PG5550'","source = base / 'source-full-PG5572'"),
        ("old = base / 'runs/PG5414-six-v1'","old = base / 'runs/PG5550-six-v1'"),
        ('transfer/PG5550-source.tar','transfer/PG5572-source.tar')):
        if raw.count(before)!=1:raise ValueError('one exact original/current path binding')
        raw=raw.replace(before,after,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3896,3900):return ast.copy_location(ast.Constant({3896:3900,3900:3904}[node.value]),node)
            if isinstance(node.value,str):node.value=node.value.replace('actual qualified296/3896 baseline manifest','actual qualifieda19/3900 baseline manifest').replace('all3896 original identities retained plus exact4 independent scratch methods','all3900 original identities retained plus exact4 independent caller-monitor methods')
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def added_cases():
    paths=subprocess.check_output(['git','diff','--name-only',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();added=[]
    for path in paths:
        if '/src/test/java/'not in path or not path.endswith('.java'):continue
        old=subprocess.run(['git','show',previous.SOURCE+':'+path],cwd=ROOT,capture_output=True,text=True)
        if old.returncode not in(0,128):raise ValueError('old source is readable or explicitly new test fixture')
        current=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT,text=True)
        before=set(re.findall(r'@Test\s+(?:public\s+)?void\s+([A-Za-z0-9_]+)\(',old.stdout if old.returncode==0 else''))
        after=set(re.findall(r'@Test\s+(?:public\s+)?void\s+([A-Za-z0-9_]+)\(',current))
        if before-after:raise ValueError('no original test renamed/removed')
        cls=path.split('/src/test/java/',1)[1][:-5].replace('/','.')
        added.extend((cls,name)for name in sorted(after-before))
    if len(added)!=4 or set(added)!=ADDED:raise ValueError('only four independently specified caller-monitor cases')
    return sorted(added)


def main():
    original=json.loads((W/entry.SLOT/'manifest.safe.json').read_bytes())
    if type(original['actualExit'])is not int or original['actualExit']!=0 or original['source']!=SOURCE:raise ValueError('original3904 must genuinely finish0 first, never rerun for collection')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT):raise ValueError('fixed canonical2fc source')
    before_raw=(W/previous.SLOT/'manifest.safe.json').read_bytes()
    if hashlib.sha256(before_raw).hexdigest()!='892c226284831d450792e601fe7a618e1951b828c58e4eca839613b806cb901f':raise ValueError('actual immutable qualifieda19 original3900')
    prior=json.loads(before_raw)['result']
    selected_raw=(W/'pg5566-private-monitor-green-v2/manifest.safe.json').read_bytes();proof_raw=(W/'pg5568-monitor-bytecode-v2/manifest.safe.json').read_bytes()
    if hashlib.sha256(selected_raw).hexdigest()!='27d1b35269b9a4e8848100565e7d6b901f425cd599805c6afe1031dc874ced50'or hashlib.sha256(proof_raw).hexdigest()!='fb7917b4b9d9944f0cf3a6fb286d173569e31193ab1e8fbc31cf3f2f91d554ec':raise ValueError('immutable actual current71/14/11 physical proof')
    selected=json.loads(selected_raw);proof=json.loads(proof_raw)
    if not(selected['sourceSnapshot']==proof['sourceSnapshot']==SOURCE and selected['greenSelectedQualified']and proof['actualExit']==0
        and{r['class']:r['classification']for r in proof['allPhysicalDifferenceClassifications']}==PHYSICAL_KINDS):raise ValueError('actual all11 qualified code/debug classifications')
    candidate=selected['physicalMain']['sha256'];physical_difference(prior['allPhysicalMainSha256'],candidate,candidate)
    begin=json.loads((W/entry.SLOT/'begin.safe.json').read_bytes());cases=added_cases()
    data={'source':SOURCE,'priorManifestSha256':prior['serverManifestSha256'],'priorJarHashes':prior['jarHashes'],
        'archiveSha256':begin['archiveSha256'],'aliases':{},'newCases':cases,'declaredNewCases':cases,'invocationAliases':{},'candidateMain':candidate,
        'allMainSourceSha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw='PHYSICAL_KINDS='+repr(PHYSICAL_KINDS)+'\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+"\nprint(__import__('json').dumps(qualify("+repr(data)+")))\n"
    if check(raw,'<actual original3904 independent reader>'):raise ValueError('all standalone namespace before output')
    compile(raw,'<original3904 result only>','exec')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5574-monitor-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only independent result namespace, inspect original on collision')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed independent reader transfer')
    code,output=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or output.split()[0]!=digest:raise ValueError('actual reader payload SHA')
    code,output=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(output);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'formalAccepted':False,'wholeReplayed':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','staticSixModules','unchangedPhysicalClasses','global100','F03Accepted')}))
    return code


if __name__=='__main__':raise SystemExit(main())
