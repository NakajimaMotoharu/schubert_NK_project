"""Independent actual whole3791/553/1650; retain all3761 old cases and exact one Main/three declarations."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from lan_server import copy,run
import pg4846_ssc301_302_whole_qualification as previous
import pg4956_expiry_success_selected as selection
from pg4968_ssc304_full import SOURCE,ROOT,W

SLOT='pg4970-ssc304-whole-qualified-v1'
MODIFIED={'batch:'+selection.REPO+'.class'}
INTERFACES={'batch:'+selection.REPO+'$'+n+'.class'for n in ('JdbcAcquire','JdbcRead','JdbcRelease')}


def added_cases():
    values=[]
    for suffix,prefix,count in (('file/BackupRetentionRejectionTest','backup4950',6),
                                ('repository/ExpirySuccessfulScopeTest','exp4956',24)):
        path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'+suffix+'.java'
        text=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT,text=True)
        names=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',text)
        if len(names)!=count or len(names)!=text.count('@Test')or len(set(names))!=count or {
            n[len(prefix):len(prefix)+3]for n in names if n.startswith(prefix)}!={str(i).zfill(3)for i in range(1,count+1)}:
            raise ValueError('exact independent newly specified Test ID inventory')
        values.extend(('dev.codex.schubert.nk.batch.'+suffix.replace('/','.'),n)for n in names)
    return values


def physical_difference(old,new,candidate):
    import re
    if any(type(m)is not dict or any(type(k)is not str or type(v)is not str or re.fullmatch('[a-f0-9]{64}',v)is None for k,v in m.items())for m in(old,new,candidate)):
        raise ValueError('strict actual SHA256 inventories')
    if len(old)!=1647 or len(new)!=1650 or set(new)!=set(old)|INTERFACES or new!=candidate:
        raise ValueError('exact all1650 actual same-source Main and three internal interfaces')
    changed={k for k in old if old[k]!=new[k]}
    if changed!=MODIFIED:raise ValueError('exact one repository outer Main changed; record/debug drift rejected')
    values=[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED'}for k in sorted(changed)]
    values.extend({'oldClass':None,'class':k,'oldSha256':None,'newSha256':new[k],'action':'ADDED_INTERNAL_INTERFACE'}for k in sorted(INTERFACES))
    return values,len(old)-len(changed)


def qualifier_source():
    raw=previous.qualifier_source()
    for old,new in (("out = base / 'runs/PG4844-six-v1'","out = base / 'runs/PG4968-six-v1'"),
        ("source = base / 'source-full-PG4844'","source = base / 'source-full-PG4968'"),
        ("old = base / 'runs/PG4694-six-v1'","old = base / 'runs/PG4844-six-v1'"),
        ('transfer/PG4844-source.tar','transfer/PG4968-source.tar')):
        if raw.count(old)!=1:raise ValueError('one original/current physical proof path '+old)
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {3739,3761,551,1647,22}:
                return ast.copy_location(ast.Constant({3739:3761,3761:3791,551:553,1647:1650,22:30}[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def candidate_main():
    selected=W/'pg4972-expiry-success-selected-v1'
    result=json.loads((selected/'manifest.safe.json').read_bytes())
    if not(type(result['actualExit'])is int and result['actualExit']==result['actualMavenExit']==0
           and result['sourceSnapshot']==SOURCE and result['tests']==59 and result['suites']==7):raise ValueError('actual59/7 selected first')
    selection.verify_main_bytes(selected/'source')
    prior=json.loads((W/'pg4846-ssc301-302-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
    old=prior['allPhysicalMainSha256'];modules=set(selection.MODULES.values())
    candidate={k:v for k,v in old.items()if k.split(':',1)[0]not in modules}
    for module in modules:
        classes=selected/'source'/('src/schubert-nk-'+module+'/target/classes')
        candidate.update({module+':'+p.relative_to(classes).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in classes.rglob('*.class')})
    physical_difference(old,candidate,candidate)
    return prior,candidate


def main():
    original=json.loads((W/'pg4968-ssc304-six-v1/manifest.safe.json').read_bytes())
    if original['actualExit']!=0 or original['source']!=SOURCE:raise ValueError('actual original whole0 required, never rerun')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT):raise ValueError('all source/Test/settings unchanged')
    selection.validate_selection();prior,candidate=candidate_main()
    before=json.loads((W/'pg4968-ssc304-six-v1/begin.safe.json').read_bytes())
    data={'source':SOURCE,'priorManifestSha256':prior['serverManifestSha256'],'priorJarHashes':prior['jarHashes'],
          'archiveSha256':before['archiveSha256'],'aliases':{},'newCases':added_cases(),'candidateMain':candidate,
          'allMainSourceSha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw='import json\nMODIFIED=set('+repr(sorted(MODIFIED))+')\nINTERFACES=set('+repr(sorted(INTERFACES))+')\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\nprint(json.dumps(qualify('+repr(data)+')))\n'
    from pyflakes.api import check
    if check(raw,'<complete actual SSC304 whole qualifier>'):raise ValueError('complete standalone static0')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py';path.write_text(raw);digest=hashlib.sha256(raw.encode()).hexdigest()
    remote='/home/mini/schubert-nk-pgpt/transfer/PG4970-whole-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only qualification namespace; recover original')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed qualifier transfer')
    code,output=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or output.split()[0]!=digest:raise ValueError('exact qualifier payload bytes')
    code,output=run('python3 -B '+remote+'/qualify.private.py',timeout=180);(out/'observer.private.log').write_text(output)
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'formalAccepted':False,'wholeReplayed':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','staticSixModules','unchangedPhysicalClasses','global100','F03Accepted')}))
    return code


if __name__=='__main__':raise SystemExit(main())
