"""Read original3967 artifacts after terminal0; no test, service or recovery execution."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from pyflakes.api import check
from lan_server import run,copy
import pg5814_rollback_qualification as previous
from pg5832_isolation_whole import SOURCE,ROOT,W,SLOT as ORIGINAL,NEW_TESTS,CHANGED_TESTS,HELPER
from pg5830_isolation_static import MODIFIED,ADDED,class_key
from pg5828_isolation_green import TARGETS

SLOT='pg5834-isolation-qualified-v1';BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
PHYSICAL_KINDS={class_key(p):'ISOLATION_PHASE_RECEIVER_CORRECTION'for p in MODIFIED}|{class_key(ADDED):'ADDED_NONCOMMIT_ISOLATION_TYPE'}


def physical_difference(old,new,candidate):
    added={k for k in PHYSICAL_KINDS if PHYSICAL_KINDS[k]=='ADDED_NONCOMMIT_ISOLATION_TYPE'};modified=set(PHYSICAL_KINDS)-added
    if len(old)!=1665 or len(new)!=1666 or new!=candidate or set(new)-set(old)!=added or set(old)-set(new)or{k for k in old if old[k]!=new[k]}!=modified:raise ValueError('all1666 actual bytes; added1 modified6 unchanged1659 only')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for m in(old,new,candidate)for v in m.values()):raise ValueError('actual SHA256 only')
    return[{'oldClass':k if k in old else None,'class':k,'oldSha256':old.get(k),'newSha256':new[k],'action':'MODIFIED'if k in old else'ADDED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(PHYSICAL_KINDS)],1659


def added_cases():
    oldsource=previous.SOURCE;rows=subprocess.check_output(['git','diff','--name-status',oldsource,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();cases=[];newfiles=set();changed=set();helpers=set()
    for row in rows:
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if not path.endswith('.java')or'/src/test/java/dev/codex/schubert/nk/'not in path:raise ValueError('original test resources unchanged')
        key=path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5];raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT,text=True);names=previous.names(raw);cls=path.split('/src/test/java/')[1][:-5].replace('/','.')
        if action=='A'and key in NEW_TESTS:newfiles.add(key);cases.extend((cls,n)for n in names)
        elif action=='A'and key==HELPER and not names:helpers.add(key)
        elif action=='M'and key in CHANGED_TESTS:
            before=subprocess.check_output(['git','show',oldsource+':'+path],cwd=ROOT,text=True)
            if previous.names(before)!=names:raise ValueError('old Test identities unchanged')
            changed.add(key)
        else:raise ValueError('only declared new12, one finite helper and four cause supplements')
    if newfiles!=NEW_TESTS or changed!=CHANGED_TESTS or helpers!={HELPER}or len(cases)!=12 or len(set(cases))!=12:raise ValueError('exact12 independent Test identities')
    return sorted(cases)


def qualifier_source():
    raw=previous.qualifier_source()
    for old,new in(("out = base / 'runs/PG5808-six-v1'","out = base / 'runs/PG5832-six-v1'"),("source = base / 'source-full-PG5808'","source = base / 'source-full-PG5832'"),("old = base / 'runs/PG5780-six-v1'","old = base / 'runs/PG5808-six-v1'"),('transfer/PG5808-source.tar','transfer/PG5832-source.tar')):
        if raw.count(old)!=1:raise ValueError('one original/prior read-only artifact binding')
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3939,3955,587,1665):return ast.copy_location(ast.Constant({3939:3955,3955:3967,587:590,1665:1666}[node.value]),node)
            if type(node.value)is str:node.value=node.value.replace('all3939 original identities retained plus exact16 independent rollback contracts; four oracle supplements explicitly declared, no aliases','all3955 original identities retained plus exact12 independent isolation contracts; four cause supplements and one finite helper explicitly declared')
            return node
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if isinstance(node.left,ast.Call)and isinstance(node.left.func,ast.Name)and node.left.func.id=='len'and len(node.left.args)==1 and isinstance(node.left.args[0],ast.Name)and node.left.args[0].id=='additions':
                for value in node.comparators:
                    if isinstance(value,ast.Constant)and value.value==16:value.value=12
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def emitted(data):
    counters=inspect.getsource(previous.previous.prior.target_counters).replace('source-full-PG5754','source-full-PG5832')
    raw='import re\nPHYSICAL_KINDS='+repr(PHYSICAL_KINDS)+'\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\n'+counters+'\ndata='+repr(data)+'\nvalue=qualify(data)\nvalue["changedTargetCounters"]=target_counters(data)\nvalue["changedTargetFour100"]=all(c[k]["missed"]==0 and(c[k]["covered"]>0 or k=="BRANCH")for c in value["changedTargetCounters"].values()for k in("LINE","METHOD","CLASS","BRANCH"))\nvalue["coreReceiverTargetFour100"]=value["changedTargetFour100"]\nvalue["targetScopeNote"]="Eight receiver targets include unchanged UnconfirmedJmsRollbackException; seven physical changes only, not global coverage."\nprint(__import__("json").dumps(value))\n'
    if check(raw,'<independent original3967 reader>'):raise ValueError('complete reader namespace0')
    for n in ast.walk(ast.parse(raw)):
        if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and(n.func.attr in('write_text','write_bytes','unlink','mkdir')or isinstance(n.func.value,ast.Name)and n.func.value.id in('subprocess','socket','dbus')):raise ValueError('artifact read only; no PT/runtime/write')
    return raw


def main():
    originalp=W/ORIGINAL/'manifest.safe.json';original=json.loads(originalp.read_bytes())
    if not(original['actualExit']==0 and original['source']==SOURCE and original['result']['run']=='PG5832-six-v1'and original['result']['tests']==3967):raise ValueError('original genuine3967 terminal0 first; no replay')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('fixed Main/Test/config')
    oldp=BASE/'PG5808-current3955-cases/qualification.json'
    if hashlib.sha256(oldp.read_bytes()).hexdigest()!='42bdfb97cdc1f3b1944e28e144e91993ed2f05bc269a289ba6f20e6d7f29a376':raise ValueError('original3955 independently qualified reference')
    old=json.loads(oldp.read_bytes());sp=BASE/'PG5830-isolation-static-v1/manifest.json';public=json.loads(sp.read_bytes());private=W/'pg5830-isolation-static-v1/manifest.safe.json'
    if hashlib.sha256(private.read_bytes()).hexdigest()!=public['privateManifestSha256']:raise ValueError('independent current static proof hash')
    candidate=json.loads(private.read_bytes());physical_difference(old['allPhysicalMainSha256'],candidate['auxClassHashes'],candidate['auxClassHashes'])
    if candidate['source']!=SOURCE or candidate['actualExit']!=0:raise ValueError('current candidate identity')
    begin=json.loads((W/ORIGINAL/'begin.safe.json').read_bytes());cases=added_cases();core=sorted(m+':dev/codex/schubert/nk/'+c+'.class'for m,classes in TARGETS.items()for c in classes)
    data={'source':SOURCE,'priorManifestSha256':old['serverManifestSha256'],'priorJarHashes':old['jarHashes'],'archiveSha256':begin['archiveSha256'],'aliases':{},'newCases':cases,'declaredNewCases':cases,'invocationAliases':{},'candidateMain':candidate['auxClassHashes'],'allMainSourceSha256':candidate['allSourceHashes'],'targetClasses':core,'coreClasses':core}
    raw=emitted(data);os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5834-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new reader namespace unavailable; no alternate operation')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed reader transfer failed')
    code,text=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('exact reader payload')
    code,text=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'originalReturnedManifestSha256':hashlib.sha256(originalp.read_bytes()).hexdigest(),'wholeReplayed':False,'formalAccepted':False,'vmActions':0,'refusedPtRetried':False,'staticPublicManifestSha256':hashlib.sha256(sp.read_bytes()).hexdigest()}
    if code==0:value['result']=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','unchangedPhysicalClasses','FESFlakyNotRun','staticSixModules','coreReceiverTargetFour100','global100')}))
    return code


if __name__=='__main__':raise SystemExit(main())
