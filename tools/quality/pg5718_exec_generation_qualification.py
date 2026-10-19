"""Read original PG5716 XML/Jars only. No PT, VM, service, DB, process or ownership operation."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from pyflakes.api import check
from lan_server import run,copy
import pg5574_monitor_whole_qualification as previous
from pg5714_exec_generation_proof import SOURCE,ROOT,W

SLOT='pg5718-exec-generation-qualified-v1'
PREFIX='batch:dev/codex/schubert/nk/batch/platform/RootStartupContext'
PHYSICAL_KINDS={PREFIX+'.class':'DECLARED_CODE_CHANGE',PREFIX+'$NativeIo.class':'DEBUG_ONLY'}
ADDED={
 ('dev.codex.schubert.nk.batch.platform.RootStartupContextTest','execgen309001TransientZombieIsPendingGenerationNeverAnExit'),
 ('dev.codex.schubert.nk.batch.platform.RootStartupContextTest','execgen309002StrictCaptureAndForeignGenerationRemainRejected'),
 ('dev.codex.schubert.nk.batch.platform.MorningServiceReadinessTest','execgen309003PendingGenerationNeedsOrdinaryCommandSocketAndHttp')}


def physical_difference(old,new,candidate):
    if set(old)!=set(new)or new!=candidate or len(new)!=1664:raise ValueError('all actual1664 original/current/selected maps required')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for m in(old,new,candidate)for v in m.values()):raise ValueError('exact physical byte hashes')
    changed={k for k in old if old[k]!=new[k]}
    if changed!=set(PHYSICAL_KINDS):raise ValueError('one code/one debug difference, no exclusions')
    return[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(changed)],1662


def qualifier_source():
    raw=previous.qualifier_source()
    for old,new in(("out = base / 'runs/PG5588-six-v1'","out = base / 'runs/PG5716-six-v1'"),
      ("source = base / 'source-full-PG5588'","source = base / 'source-full-PG5716'"),
      ("old = base / 'runs/PG5550-six-v1'","old = base / 'runs/PG5588-six-v1'"),
      ('transfer/PG5588-source.tar','transfer/PG5716-source.tar')):
        if raw.count(old)!=1:raise ValueError('one exact existing artifact path')
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3900,3905):return ast.copy_location(ast.Constant({3900:3905,3905:3908}[node.value]),node)
            return node
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if isinstance(node.left,ast.Call)and isinstance(node.left.func,ast.Name)and node.left.func.id=='len'and len(node.left.args)==1 and isinstance(node.left.args[0],ast.Name)and node.left.args[0].id=='additions':
                for n in node.comparators:
                    if isinstance(n,ast.Constant)and n.value==5:n.value=3
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def source(data):
    raw='import re\nPHYSICAL_KINDS='+repr(PHYSICAL_KINDS)+'\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+"\nprint(__import__('json').dumps(qualify("+repr(data)+")))\n"
    if check(raw,'<read only original PG5716 result>'):raise ValueError('complete emitted static0')
    tree=ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and isinstance(node.func.value,ast.Name)and node.func.value.id in('subprocess','dbus','socket'):raise ValueError('artifact reader cannot launch commands or access runtime')
    return raw


def main():
    original_path=W/'pg5716-exec-generation-six-v1/manifest.safe.json';original=json.loads(original_path.read_bytes())
    if hashlib.sha256(original_path.read_bytes()).hexdigest()!='d9cbc1a5755f52decf19aaf8b8cfa2f8f94381f2c49e04d73e07c6e152037355' or original['actualExit']!=0 or original['source']!=SOURCE or original['result']['run']!='PG5716-six-v1' or original['result']['tests']!=3908:raise ValueError('original returned producer0 first; never dispatch PT')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('same fixed source before reading results')
    old_path=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5588-current3905-cases/qualification.json'
    if hashlib.sha256(old_path.read_bytes()).hexdigest()!='b34549edfd627c6b4606abbbb9a50eadf47153b37e7b3ad7e3f2aa2a30732878':raise ValueError('original3905 reference, not imported success')
    old=json.loads(old_path.read_bytes());selected=json.loads((W/'pg5708-exec-generation-green-v1/manifest.safe.json').read_bytes());proof=json.loads((W/'pg5714-exec-generation-independent-v1/manifest.safe.json').read_bytes())
    if not(selected['sourceSnapshot']==proof['source']==SOURCE and selected['greenSelectedQualified']and proof['actualExit']==0 and proof['tests']==62):raise ValueError('actual selected/new-byte proof')
    physical_difference(old['allPhysicalMainSha256'],selected['allPhysicalMainSha256'],selected['allPhysicalMainSha256'])
    begin=json.loads((W/'pg5716-exec-generation-six-v1/begin.safe.json').read_bytes())
    data={'source':SOURCE,'priorManifestSha256':old['serverManifestSha256'],'priorJarHashes':old['jarHashes'],'archiveSha256':begin['archiveSha256'],
      'aliases':{},'newCases':sorted(ADDED),'declaredNewCases':sorted(ADDED),'invocationAliases':{},'candidateMain':selected['allPhysicalMainSha256'],
      'allMainSourceSha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw=source(data);os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5718-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new only result reader directory refused; no alternate path/retry')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed result reader transfer refused')
    code,text=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('exact artifact reader bytes')
    code,text=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'formalAccepted':False,'wholeReplayed':False,'vmActions':0,'refusedPtRetried':False}
    if code==0:value['result']=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','staticSixModules','unchangedPhysicalClasses','FESFlakyNotRun','global100')}))
    return code


if __name__=='__main__':raise SystemExit(main())
