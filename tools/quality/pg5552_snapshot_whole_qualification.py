"""Read the original PG5550 whole only; exact old3896/new4 and all1664 physical proof."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from pyflakes.api import check
from lan_server import copy,run
import pg5416_ownership_whole_qualification as previous
import pg5550_snapshot_required_whole as entry
from pg5540_snapshot_scratch_selected import FAULT,PACKAGE

SOURCE,ROOT,W=entry.SOURCE,entry.ROOT,entry.W
SLOT='pg5552-snapshot-whole-qualified-v1'


def physical_difference(old,new,candidate):
    import re
    for value in(old,new,candidate):
        if type(value)is not dict or len(value)!=1664 or any(type(k)is not str or type(v)is not str or re.fullmatch('[0-9a-f]{64}',v)is None for k,v in value.items()):raise ValueError('all actual1664 physical Main maps required')
    if set(old)!=set(new)or new!=candidate:raise ValueError('all1664 actual current built bytes, no addition/removal/unbuilt success')
    changed={k for k in old if old[k]!=new[k]}
    if changed!={'api:dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.class'}:raise ValueError('only declared current codec class may change')
    return[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED'}for k in sorted(changed)],1663


def qualifier_source():
    raw=previous.qualifier_source()
    for before,after in(("out = base / 'runs/PG5414-six-v1'","out = base / 'runs/PG5550-six-v1'"),
        ("source = base / 'source-full-PG5414'","source = base / 'source-full-PG5550'"),
        ("old = base / 'runs/PG5128-six-v1'","old = base / 'runs/PG5414-six-v1'"),
        ('transfer/PG5414-source.tar','transfer/PG5550-source.tar')):
        if raw.count(before)!=1:raise ValueError('one exact original/current qualifier path')
        raw=raw.replace(before,after,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in{3814,3896,562,82}:
                return ast.copy_location(ast.Constant({3814:3896,3896:3900,562:563,82:4}[node.value]),node)
            if isinstance(node.value,str):
                node.value=node.value.replace('all3814 original identities retained plus exact82 invocations with only three source-verified TempDir Path aliases','all3896 original identities retained plus exact4 independent scratch methods, no new invocation aliases')
                node.value=node.value.replace('actual qualified a2ecc3791 baseline manifest','actual qualified296/3896 baseline manifest')
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def added_cases():
    paths=subprocess.check_output(['git','diff','--name-only',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();additions=[]
    for path in paths:
        if '/src/test/java/'not in path or not path.endswith('.java'):continue
        old=subprocess.run(['git','show',previous.SOURCE+':'+path],cwd=ROOT,capture_output=True,text=True)
        if old.returncode not in(0,128):raise ValueError('old declared test source must be readable or an explicitly new path')
        current=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT,text=True)
        before=set(re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',old.stdout if old.returncode==0 else''))
        after=set(re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',current))
        if before-after:raise ValueError('no original Test removed or renamed')
        cls=path.split('/src/test/java/',1)[1][:-5].replace('/','.')
        additions.extend((cls,name)for name in sorted(after-before))
    expected={(PACKAGE+'SnapshotScratchOwnershipTest',name)for name in FAULT}
    if len(additions)!=4 or set(additions)!=expected:raise ValueError('only the four explicitly specified new cases')
    return sorted(additions)


def candidate_main():
    old=json.loads((W/previous.SLOT/'manifest.safe.json').read_bytes())
    if type(old['actualExit'])is not int or old['actualExit']!=0 or old['source']!=previous.SOURCE:raise ValueError('actual qualified296 original baseline')
    before=old['result']
    if(before['tests'],before['suites'],before['mainClasses'])!=(3896,562,1664):raise ValueError('exact original3896 whole, not another old source')
    green,_=entry.selection.load(entry.selection.audit.RUN,'fb49c8579faff830f2df86f80286f9073392d436b0b986a537b3a0bbbf8e6a78')
    if not(green['sourceSnapshot']==SOURCE and green['greenSelectedQualified']and green['actualCases']==29 and green['physicalMain']['declaredDeltaQualified']):raise ValueError('actual same-source selected29/779')
    actual=green['physicalMain']['sha256'];candidate={k:v for k,v in before['allPhysicalMainSha256'].items()if k.split(':',1)[0]not in('protocol','storage','bootstrap','api')};candidate.update(actual)
    # Unselected bytes are an oracle only. Every current server Jar must match.
    physical_difference(before['allPhysicalMainSha256'],candidate,candidate)
    return before,candidate


def main():
    original=json.loads((W/entry.SLOT/'manifest.safe.json').read_bytes())
    if type(original['actualExit'])is not int or original['actualExit']!=0 or original['source']!=SOURCE:raise ValueError('original current whole must genuinely finish0; never rerun for collection')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT):raise ValueError('same current canonical Main/Test/settings')
    prior,candidate=candidate_main();before=json.loads((W/entry.SLOT/'begin.safe.json').read_bytes());cases=added_cases()
    data={'source':SOURCE,'priorManifestSha256':prior['serverManifestSha256'],'priorJarHashes':prior['jarHashes'],
        'archiveSha256':before['archiveSha256'],'aliases':{},'newCases':cases,'declaredNewCases':cases,'invocationAliases':{},'candidateMain':candidate,
        'allMainSourceSha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw=inspect.getsource(physical_difference)+'\n'+qualifier_source()+"\nprint(__import__('json').dumps(qualify("+repr(data)+")))\n"
    if check(raw,'<all original3900 current whole independent>'):raise ValueError('all standalone dependencies before transfer')
    compile(raw,'<original3900 independent current source read>','exec')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5552-whole-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only qualifier output; inspect existing original post before any retry')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed original independent qualifier transfer')
    code,output=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or output.split()[0]!=digest:raise ValueError('actual independent reader payload SHA')
    code,output=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(output);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'formalAccepted':False,'wholeReplayed':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in value if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','staticSixModules','unchangedPhysicalClasses','global100','F03Accepted')}))
    return code


if __name__=='__main__':raise SystemExit(main())
