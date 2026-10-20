"""Read original3939 artifacts only after its terminal0; never reissue full PT/runtime actions."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from pyflakes.api import check
from lan_server import run,copy
import pg5756_private_contract_qualification as prior
from pg5780_jms_primary_whole import SOURCE,ROOT,W,SLOT as ORIGINAL

SLOT='pg5782-jms-primary-qualified-v1'
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
PHYSICAL_KINDS={
 'api:dev/codex/schubert/nk/api/messaging/inbound/InboundTransactions.class':'SAME_IDENTITY_GUARDS',
 'web:dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumer.class':'SAME_IDENTITY_GUARD'}


def physical_difference(old,new,candidate):
    if set(old)!=set(new)or new!=candidate or len(new)!=1664:raise ValueError('all1664 current/prior/candidate hashes required')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for m in(old,new,candidate)for v in m.values()):raise ValueError('actual byte hashes only')
    changed={k for k in old if old[k]!=new[k]}
    if changed!=set(PHYSICAL_KINDS):raise ValueError('only two declared Main class differences; no raw delta excluded')
    return[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED','physicalKind':PHYSICAL_KINDS[k]}for k in sorted(changed)],1662


def added_cases():
    rows=subprocess.check_output(['git','diff','--name-status','9463db1ac23437043facf95b87f64b9fc7e758bd',SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();cases=[];files=0
    for row in rows:
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if action!='A'or not path.endswith('Test.java'):raise ValueError('all original3932 test bodies/resources unchanged')
        files+=1;names=re.findall(r'@Test\s+(?:public\s+)?void\s+([A-Za-z0-9_]+)\(', (ROOT/path).read_text());cls=path.split('/src/test/java/')[1][:-5].replace('/','.')
        cases.extend((cls,name)for name in names)
    if files!=2 or len(cases)!=7 or len(set(cases))!=7 or any(not re.match(r'jmsP00[1-7]',m)for _,m in cases):raise ValueError('exact seven finite independent JMS contracts')
    return sorted(cases)


def qualifier_source():
    raw=prior.qualifier_source()
    for old,new in(("out = base / 'runs/PG5754-six-v1'","out = base / 'runs/PG5780-six-v1'"),("source = base / 'source-full-PG5754'","source = base / 'source-full-PG5780'"),("old = base / 'runs/PG5716-six-v1'","old = base / 'runs/PG5754-six-v1'"),('transfer/PG5754-source.tar','transfer/PG5780-source.tar')):
        if raw.count(old)!=1:raise ValueError('exact current/prior artifact path, not global label substitution')
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3908,3932,581):return ast.copy_location(ast.Constant({3908:3932,3932:3939,581:583}[node.value]),node)
            if type(node.value)is str:node.value=node.value.replace('all3908 original identities retained plus exact24 finite private/value/null cases; no aliases','all3932 original identities retained plus exact7 independent JMS primary contracts; no aliases')
            return node
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if isinstance(node.left,ast.Call)and isinstance(node.left.func,ast.Name)and node.left.func.id=='len'and len(node.left.args)==1 and isinstance(node.left.args[0],ast.Name)and node.left.args[0].id=='additions':
                for value in node.comparators:
                    if isinstance(value,ast.Constant)and value.value==24:value.value=7
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def emitted(data):
    counters=inspect.getsource(prior.target_counters).replace('source-full-PG5754','source-full-PG5780')
    raw='import re\nPHYSICAL_KINDS='+repr(PHYSICAL_KINDS)+'\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\n'+counters+'\ndata='+repr(data)+'\nvalue=qualify(data)\nvalue["changedTargetCounters"]=target_counters(data)\nvalue["changedTargetFour100"]=all(c[k]["missed"]==0 and(c[k]["covered"]>0 or k=="BRANCH")for c in value["changedTargetCounters"].values()for k in("LINE","METHOD","CLASS","BRANCH"))\nprint(__import__("json").dumps(value))\n'
    if check(raw,'<original3939 independent reader>'):raise ValueError('standalone reader all namespace0')
    for node in ast.walk(ast.parse(raw)):
        if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and(node.func.attr in('write_text','write_bytes','unlink','mkdir')or isinstance(node.func.value,ast.Name)and node.func.value.id in('subprocess','socket','dbus')):raise ValueError('no PT/runtime/write call in artifact reader')
    return raw


def main():
    originalp=W/ORIGINAL/'manifest.safe.json';original=json.loads(originalp.read_bytes())
    if not(original['actualExit']==0 and original['source']==SOURCE and original['result']['run']=='PG5780-six-v1'and original['result']['tests']==3939):raise ValueError('original genuine3939 terminal0 first, never rerun')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('same canonical source')
    oldp=BASE/'PG5754-current3932-cases/qualification.json'
    if hashlib.sha256(oldp.read_bytes()).hexdigest()!='ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18':raise ValueError('original3932 qualified reference')
    old=json.loads(oldp.read_bytes());sp=BASE/'PG5776-jms-primary-static-v1/manifest.json'
    if hashlib.sha256(sp.read_bytes()).hexdigest()!='aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f':raise ValueError('current exact three guards/source/static proof')
    private=W/'pg5776-jms-primary-static-v1/manifest.safe.json'
    if hashlib.sha256(private.read_bytes()).hexdigest()!=json.loads(sp.read_bytes())['privateManifestSha256']:raise ValueError('actual candidate1664 proof')
    selected=json.loads(private.read_bytes());physical_difference(old['allPhysicalMainSha256'],selected['auxClassHashes'],selected['auxClassHashes'])
    if selected['source']!=SOURCE or selected['actualExit']!=0:raise ValueError('current selected compile source')
    begin=json.loads((W/ORIGINAL/'begin.safe.json').read_bytes());cases=added_cases()
    data={'source':SOURCE,'priorManifestSha256':old['serverManifestSha256'],'priorJarHashes':old['jarHashes'],'archiveSha256':begin['archiveSha256'],'aliases':{},'newCases':cases,'declaredNewCases':cases,'invocationAliases':{},'candidateMain':selected['auxClassHashes'],'allMainSourceSha256':selected['allSourceHashes'],'targetClasses':sorted(PHYSICAL_KINDS)}
    raw=emitted(data);os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5782-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new result namespace refused; no alternate path')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed reader transfer refused')
    code,text=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('actual exact reader bytes')
    code,text=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'originalReturnedManifestSha256':hashlib.sha256(originalp.read_bytes()).hexdigest(),'formalAccepted':False,'wholeReplayed':False,'vmActions':0,'refusedPtRetried':False}
    if code==0:value['result']=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','unchangedPhysicalClasses','FESFlakyNotRun','staticSixModules','changedTargetFour100','global100')}))
    return code


if __name__=='__main__':raise SystemExit(main())
