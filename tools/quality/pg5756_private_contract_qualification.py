"""Independently read original PG5754 artifacts; never reexecute PT or touch guest runtime."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from pyflakes.api import check
from lan_server import run,copy
import pg5718_exec_generation_qualification as prior
from pg5754_private_contract_whole import SOURCE,ROOT,W,SLOT as ORIGINAL

SLOT='pg5756-private-contract-qualified-v1'
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'


def changed_types():
    p=BASE/'PG5584-field-accessor-inspection-v1/manifest.json'
    if hashlib.sha256(p.read_bytes()).hexdigest()!='31a2a4f92e8a5a2ad0c320a1e6d78008bd560f61e4e3284388ed0a560217bc04':raise ValueError('typed original64 inventory')
    result={}
    for row in json.loads(p.read_bytes())['fields']:
        path=row['sourcePath'];member=path.split('/src/main/java/')[1][:-5];declared=member.replace('/','.')
        suffix=row['declaringType'][len(declared):]
        if not row['declaringType'].startswith(declared)or suffix and not suffix.startswith('.'):raise ValueError('exact declared class path')
        key=path.split('/')[1].removeprefix('schubert-nk-')+':'+member+suffix.replace('.','$')+'.class'
        result[key]='PRIVATE_ENUM_FIELD'if row['ownerKind']=='ENUM'else'PRIVATE_THROWABLE_FIELD_AND_DECLARED_NULL_GUARDS'
    if len(result)!=53:raise ValueError('all64 fields belong to exact53 declaring classes')
    result['web:dev/codex/schubert/nk/web/revocation/RevocationPayloadCodec.class']='DECLARED_EQUIVALENT_NULL_GUARD'
    return result


def physical_difference(old,new,candidate):
    if set(old)!=set(new)or new!=candidate or len(new)!=1664:raise ValueError('all1664 actual byte hashes from same source required')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for m in(old,new,candidate)for v in m.values()):raise ValueError('exact byte hashes')
    changed={k for k in old if old[k]!=new[k]}
    if changed!=set(PHYSICAL_KINDS):raise ValueError('only53 private declaring types and one codec; no ignored raw difference')
    return[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(changed)],1610


def added_cases():
    rows=subprocess.check_output(['git','diff','--name-status','6db56fe',SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();added=[]
    for row in rows:
        status,path=row.split('\t')
        if '/src/test/'not in path:continue
        if status!='A'or not path.endswith('Test.java'):raise ValueError('original tests/resources must be unchanged')
        raw=(ROOT/path).read_text();names=re.findall(r'@Test\s+(?:public\s+)?void\s+([A-Za-z0-9_]+)\(',raw)
        if not names:raise ValueError('source-declared exact finite cases')
        cls=path.split('/src/test/java/')[1][:-5].replace('/','.')
        added.extend((cls,name)for name in names)
    if len(added)!=24 or len(set(added))!=24:raise ValueError('exact24 new finite independent tests')
    return sorted(added)


def qualifier_source():
    raw=prior.qualifier_source()
    for old,new in(("out = base / 'runs/PG5716-six-v1'","out = base / 'runs/PG5754-six-v1'"),("source = base / 'source-full-PG5716'","source = base / 'source-full-PG5754'"),("old = base / 'runs/PG5588-six-v1'","old = base / 'runs/PG5716-six-v1'"),('transfer/PG5716-source.tar','transfer/PG5754-source.tar')):
        if raw.count(old)!=1:raise ValueError('one original artifact binding')
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3905,3908,563):return ast.copy_location(ast.Constant({3905:3908,3908:3932,563:581}[node.value]),node)
            if type(node.value)is str:node.value=node.value.replace('all3900 original identities retained plus exact5 independent monitor and runtime-canary methods, no new invocation aliases','all3908 original identities retained plus exact24 finite private/value/null cases; no aliases')
            return node
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if isinstance(node.left,ast.Call)and isinstance(node.left.func,ast.Name)and node.left.func.id=='len'and len(node.left.args)==1 and isinstance(node.left.args[0],ast.Name)and node.left.args[0].id=='additions':
                for value in node.comparators:
                    if isinstance(value,ast.Constant)and value.value==3:value.value=24
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def target_counters(data):
    from pathlib import Path
    import xml.etree.ElementTree as E
    result={}
    for key in data['targetClasses']:
        module,member=key.removesuffix('.class').split(':',1)
        report=Path('/home/mini/schubert-nk-pgpt/source-full-PG5754')/('src/schubert-nk-'+module+'/target/site/jacoco/jacoco.xml')
        rows=[c for c in E.parse(report).getroot().findall('package/class')if c.get('name')==member]
        if len(rows)!=1:raise ValueError('each actual changed class coverage present exactly once')
        counters={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in rows[0].findall('counter')}
        result[key]={k:counters.get(k,{'covered':0,'missed':0})for k in('LINE','METHOD','CLASS','BRANCH')}
    return result


def emitted(data):
    raw='import re\nPHYSICAL_KINDS='+repr(changed_types())+'\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\n'+inspect.getsource(target_counters)+'\ndata='+repr(data)+'\nvalue=qualify(data)\nvalue["changedTargetCounters"]=target_counters(data)\nvalue["changedTargetFour100"]=all(c[k]["missed"]==0 and (c[k]["covered"]>0 or k=="BRANCH") for c in value["changedTargetCounters"].values() for k in ("LINE","METHOD","CLASS","BRANCH"))\nprint(__import__("json").dumps(value))\n'
    if check(raw,'<original3932 artifact qualification>'):raise ValueError('complete reader static namespace0')
    compile(raw,'<original3932 read only>','exec')
    for n in ast.walk(ast.parse(raw)):
        if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and (n.func.attr in('write_text','write_bytes','unlink','mkdir')or isinstance(n.func.value,ast.Name)and n.func.value.id in('subprocess','socket','dbus')):raise ValueError('reader must not issue test/runtime/writes')
    return raw


def main():
    op=W/ORIGINAL/'manifest.safe.json';original=json.loads(op.read_bytes())
    if original['actualExit']!=0 or original['source']!=SOURCE or original['result']['run']!='PG5754-six-v1'or original['result']['tests']!=3932:raise ValueError('original genuine3932 zero only')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('same canonical source only')
    oldp=BASE/'PG5716-current3908-cases/qualification.json'
    if hashlib.sha256(oldp.read_bytes()).hexdigest()!='f50213cf1b2ca3e5dce87ba4220c59ac1eac7b67622910ed3f573175b53fa9c9':raise ValueError('qualified original3908 exact reference')
    old=json.loads(oldp.read_bytes());staticp=W/'pg5750-exception-static-v1/manifest.safe.json';selected=json.loads(staticp.read_bytes())
    if selected['source']!=SOURCE or selected['actualExit']!=0:raise ValueError('current selected all1664 byte/source proof')
    global PHYSICAL_KINDS
    PHYSICAL_KINDS=changed_types();physical_difference(old['allPhysicalMainSha256'],selected['auxClassHashes'],selected['auxClassHashes'])
    begin=json.loads((W/ORIGINAL/'begin.safe.json').read_bytes());cases=added_cases()
    data={'source':SOURCE,'priorManifestSha256':old['serverManifestSha256'],'priorJarHashes':old['jarHashes'],'archiveSha256':begin['archiveSha256'],'aliases':{},'newCases':cases,'declaredNewCases':cases,'invocationAliases':{},'candidateMain':selected['auxClassHashes'],'allMainSourceSha256':selected['allSourceHashes'],'targetClasses':sorted(PHYSICAL_KINDS)}
    raw=emitted(data);os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5756-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new result reader refused; preserve no alternate path')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed result reader transfer refused')
    code,text=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('exact reader bytes before use')
    code,text=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'originalReturnedManifestSha256':hashlib.sha256(op.read_bytes()).hexdigest(),'formalAccepted':False,'wholeReplayed':False,'vmActions':0,'refusedPtRetried':False}
    if code==0:value['result']=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','unchangedPhysicalClasses','FESFlakyNotRun','staticSixModules','changedTargetFour100','global100')}))
    return code


if __name__=='__main__':raise SystemExit(main())
