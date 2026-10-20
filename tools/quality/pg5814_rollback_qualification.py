"""Independent original3955 artifact qualification only after true terminal0; never reissue PT."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from pyflakes.api import check
from lan_server import run,copy
import pg5782_jms_primary_qualification as previous
from pg5808_rollback_whole import SOURCE,ROOT,W,SLOT as ORIGINAL,NEW_TESTS,CHANGED_TESTS
from pg5804_rollback_static import MODIFIED,ADDED,class_key
from pg5800_rollback_green import TARGETS

SLOT='pg5814-rollback-qualified-v1';BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
PHYSICAL_KINDS={class_key(p):'DECLARED_RECEIVER_ROLLBACK_OR_WEB_FATAL_ASSEMBLY'for p in MODIFIED}|{class_key(ADDED):'ADDED_UNCONFIRMED_ROLLBACK_TYPE'}


def physical_difference(old,new,candidate):
    added={k for k in PHYSICAL_KINDS if PHYSICAL_KINDS[k]=='ADDED_UNCONFIRMED_ROLLBACK_TYPE'};modified=set(PHYSICAL_KINDS)-added
    if len(old)!=1664 or len(new)!=1665 or new!=candidate or set(new)-set(old)!=added or set(old)-set(new)or{k for k in old if old[k]!=new[k]}!=modified:raise ValueError('all1665 actual bytes, added1 modified8 unchanged1656 only')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for m in(old,new,candidate)for v in m.values()):raise ValueError('actual SHA256 only')
    return[{'oldClass':k if k in old else None,'class':k,'oldSha256':old.get(k),'newSha256':new[k],'action':'MODIFIED'if k in old else'ADDED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(PHYSICAL_KINDS)],1656


def names(raw):
    result=re.findall(r'@Test\s+(?:@[A-Za-z0-9_.]+(?:\([^)]*\))?\s+)*(?:public\s+)?void\s+(\w+)\s*\([^{}]*\)',raw)
    if len(result)!=len(re.findall(r'@Test\b',raw))or len(set(result))!=len(result):raise ValueError('one exact ordinary Test source identity')
    return set(result)


def added_cases():
    rows=subprocess.check_output(['git','diff','--name-status','2bbb85a297d7f7bd1b0c243d343e0da509faf99a',SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();added=[];newfiles=set();changed=set()
    for row in rows:
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if not path.endswith('Test.java')or'/src/test/java/dev/codex/schubert/nk/'not in path:raise ValueError('all original test resources/oracles outside declared four files unchanged')
        key=path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5];current=names((ROOT/path).read_text());cls=path.split('/src/test/java/')[1][:-5].replace('/','.')
        if action=='A'and key in NEW_TESTS:
            newfiles.add(key);added.extend((cls,name)for name in current)
        elif action=='M'and key in CHANGED_TESTS:
            old=subprocess.check_output(['git','show','2bbb85a297d7f7bd1b0c243d343e0da509faf99a:'+path],cwd=ROOT,text=True)
            if names(old)!=current:raise ValueError('declared prior oracle supplement retains every old Test identity')
            changed.add(key)
        else:raise ValueError('only four named additions and four reviewed prior oracle supplements')
    if newfiles!=NEW_TESTS or changed!=CHANGED_TESTS or len(added)!=16 or len(set(added))!=16:raise ValueError('exact independent16 additions, no aliases/removals')
    return sorted(added)


def qualifier_source():
    raw=previous.qualifier_source()
    for old,new in(("out = base / 'runs/PG5780-six-v1'","out = base / 'runs/PG5808-six-v1'"),("source = base / 'source-full-PG5780'","source = base / 'source-full-PG5808'"),("old = base / 'runs/PG5754-six-v1'","old = base / 'runs/PG5780-six-v1'"),('transfer/PG5780-source.tar','transfer/PG5808-source.tar')):
        if raw.count(old)!=1:raise ValueError('one original/prior artifact binding')
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3932,3939,583,1664):return ast.copy_location(ast.Constant({3932:3939,3939:3955,583:587,1664:1665}[node.value]),node)
            if type(node.value)is str:node.value=node.value.replace('all3932 original identities retained plus exact7 independent JMS primary contracts; no aliases','all3939 original identities retained plus exact16 independent rollback contracts; four oracle supplements explicitly declared, no aliases')
            return node
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if isinstance(node.left,ast.Call)and isinstance(node.left.func,ast.Name)and node.left.func.id=='len'and len(node.left.args)==1 and isinstance(node.left.args[0],ast.Name)and node.left.args[0].id=='additions':
                for value in node.comparators:
                    if isinstance(value,ast.Constant)and value.value==7:value.value=16
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def emitted(data):
    counters=inspect.getsource(previous.prior.target_counters).replace('source-full-PG5754','source-full-PG5808')
    raw='import re\nPHYSICAL_KINDS='+repr(PHYSICAL_KINDS)+'\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\n'+counters+'\ndata='+repr(data)+'\nvalue=qualify(data)\nvalue["changedTargetCounters"]=target_counters(data)\nvalue["changedTargetFour100"]=all(c[k]["missed"]==0 and(c[k]["covered"]>0 or k=="BRANCH")for c in value["changedTargetCounters"].values()for k in("LINE","METHOD","CLASS","BRANCH"))\nvalue["coreReceiverTargetFour100"]=all(value["changedTargetCounters"][name][k]["missed"]==0 and(value["changedTargetCounters"][name][k]["covered"]>0 or k=="BRANCH")for name in data["coreClasses"]for k in("LINE","METHOD","CLASS","BRANCH"))\nprint(__import__("json").dumps(value))\n'
    if check(raw,'<independent original3955 reader>'):raise ValueError('complete reader namespace0')
    for n in ast.walk(ast.parse(raw)):
        if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and(n.func.attr in('write_text','write_bytes','unlink','mkdir')or isinstance(n.func.value,ast.Name)and n.func.value.id in('subprocess','socket','dbus')):raise ValueError('artifact read only; no PT/runtime/write')
    return raw


def main():
    originalp=W/ORIGINAL/'manifest.safe.json';original=json.loads(originalp.read_bytes())
    if not(original['actualExit']==0 and original['source']==SOURCE and original['result']['run']=='PG5808-six-v1'and original['result']['tests']==3955):raise ValueError('original genuine3955 terminal0 first; no replay')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('same fixed Main/Test/config')
    oldp=BASE/'PG5780-current3939-cases/qualification.json'
    if hashlib.sha256(oldp.read_bytes()).hexdigest()!='1a5a5db819bde6bf01c85b4bb43017b8aae15bd59407b66adfbc4f5a0ca23c45':raise ValueError('original3939 independently qualified reference only')
    old=json.loads(oldp.read_bytes());sp=BASE/'PG5810-rollback-static-reauth-v1/manifest.json'
    if hashlib.sha256(sp.read_bytes()).hexdigest()!='68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23':raise ValueError('current850/1665 static reauthentication')
    private=W/'pg5810-rollback-static-reauth-v1/manifest.safe.json'
    if hashlib.sha256(private.read_bytes()).hexdigest()!=json.loads(sp.read_bytes())['privateManifestSha256']:raise ValueError('actual current Main class/source map')
    candidate=json.loads(private.read_bytes());physical_difference(old['allPhysicalMainSha256'],candidate['auxClassHashes'],candidate['auxClassHashes'])
    if candidate['source']!=SOURCE or candidate['actualExit']!=0:raise ValueError('current candidate identity')
    begin=json.loads((W/ORIGINAL/'begin.safe.json').read_bytes());cases=added_cases();core=sorted(m+':dev/codex/schubert/nk/'+c+'.class'for m,classes in TARGETS.items()for c in classes)
    data={'source':SOURCE,'priorManifestSha256':old['serverManifestSha256'],'priorJarHashes':old['jarHashes'],'archiveSha256':begin['archiveSha256'],'aliases':{},'newCases':cases,'declaredNewCases':cases,'invocationAliases':{},'candidateMain':candidate['auxClassHashes'],'allMainSourceSha256':candidate['allSourceHashes'],'targetClasses':sorted(PHYSICAL_KINDS),'coreClasses':core}
    raw=emitted(data);os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5814-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new reader namespace unavailable; preserve, no alternate operation')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed reader transfer failed')
    code,text=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('actual exact reader payload')
    code,text=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'originalReturnedManifestSha256':hashlib.sha256(originalp.read_bytes()).hexdigest(),'wholeReplayed':False,'formalAccepted':False,'vmActions':0,'refusedPtRetried':False}
    if code==0:value['result']=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','unchangedPhysicalClasses','FESFlakyNotRun','staticSixModules','changedTargetFour100','coreReceiverTargetFour100','global100')}))
    return code


if __name__=='__main__':raise SystemExit(main())
