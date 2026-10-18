"""Independent original whole XML/CRC inventories and exact82 additions; no Maven replay."""
import ast
import hashlib
import inspect
import json
import os
import re
import subprocess
from lan_server import run,copy
import pg5130_root_whole_qualification as previous
import pg5414_ownership_whole as entry

SOURCE,ROOT,W=entry.SOURCE,entry.ROOT,entry.W
SLOT='pg5416-ownership-whole-qualified-v1'
# Standalone payload replaces these with the independently checked named expected delta.
MODIFIED=set()
ADDED=set()
REMOVED=set()


def physical_difference(old,new,candidate):
    import re
    for image in (old,new,candidate):
        if type(image) is not dict or any(type(key) is not str or type(value) is not str or re.fullmatch('[0-9a-f]{64}',value) is None for key,value in image.items()):
            raise ValueError('all actual physical Main SHA256 inventories required')
    if len(old)!=1654 or len(new)!=1664 or new!=candidate or set(old)-set(new)!=REMOVED or set(new)-set(old)!=ADDED:
        raise ValueError('exact current1664 including new owners and explicitly removed old private owner')
    changed={key for key in old.keys()&new.keys() if old[key]!=new[key]}
    if changed!=MODIFIED:raise ValueError('all named actual semantic/debug changes only; no unbuilt success import')
    values=[{'oldClass':key,'class':key,'oldSha256':old[key],'newSha256':new[key],'action':'MODIFIED'} for key in sorted(changed)]
    values.extend({'oldClass':None,'class':key,'oldSha256':None,'newSha256':new[key],'action':'ADDED_INTERNAL_OWNER_OR_PORT'} for key in sorted(ADDED))
    values.extend({'oldClass':key,'class':None,'oldSha256':old[key],'newSha256':None,'action':'REMOVED_OLD_PRIVATE_OWNER'} for key in sorted(REMOVED))
    return values,len(old)-len(changed)-len(REMOVED)


def qualifier_source():
    raw=previous.qualifier_source()
    for before,after in (("out = base / 'runs/PG5128-six-v1'","out = base / 'runs/PG5414-six-v1'"),
        ("source = base / 'source-full-PG5128'","source = base / 'source-full-PG5414'"),
        ("old = base / 'runs/PG4968-six-v1'","old = base / 'runs/PG5128-six-v1'"),
        ('transfer/PG5128-source.tar','transfer/PG5414-source.tar')):
        if raw.count(before)!=1:raise ValueError('one original/current namespace '+before)
        raw=raw.replace(before,after,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value) is int and node.value in {3791,3814,556,1654,23}:
                return ast.copy_location(ast.Constant({3791:3814,3814:3896,556:562,1654:1664,23:82}[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def added_cases():
    paths=subprocess.check_output(['git','diff','--name-only',entry.previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines()
    additions=[]
    for path in paths:
        if '/src/test/java/' not in path or not path.endswith('.java'):continue
        old=subprocess.run(['git','show',entry.previous.SOURCE+':'+path],cwd=ROOT,capture_output=True,text=True)
        current=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT,text=True)
        before=set(re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',old.stdout if old.returncode==0 else ''))
        after=set(re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',current))
        if before-after:raise ValueError('original Test method removed/renamed; never silently accept a new baseline')
        cls=path.split('/src/test/java/',1)[1][:-5].replace('/','.')
        additions.extend((cls,name) for name in sorted(after-before))
    if len(additions)!=82 or len(set(additions))!=82:raise ValueError('exact82 explicitly added no-arg methods only')
    return sorted(additions)


def candidate_main():
    current=json.loads((W/entry.RUN/'manifest.safe.json').read_bytes())
    if current['actualExit']!=0 or current['sourceSnapshot']!=SOURCE or current['tests']!=1164 or current['suites']!=137:
        raise ValueError('same-source genuine selected first')
    entry.selected.configure()
    if entry.selected.selected.main_delta(W/entry.RUN/'source','factory')!=current['mainDelta']:
        raise ValueError('all current selected767 physical bytes')
    prior=json.loads((W/'pg5130-root-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
    old=prior['allPhysicalMainSha256'];actual=current['mainDelta']['physicalSha256']
    candidate={key:value for key,value in old.items() if key.split(':',1)[0] not in ('storage','bootstrap','batch')}
    candidate.update(actual)
    difference={'modified':{key for key in old.keys()&candidate.keys() if old[key]!=candidate[key]},
        'added':set(candidate)-set(old),'removed':set(old)-set(candidate)}
    # Every expected unbuilt byte is still only an oracle until current server jars are checked.
    return prior,candidate,difference


def main():
    from pyflakes.api import check
    original=json.loads((W/'pg5414-ownership-query-six-v1/manifest.safe.json').read_bytes())
    if type(original['actualExit']) is not int or original['actualExit']!=0 or original['source']!=SOURCE:
        raise ValueError('genuine original whole0 required; never rerun it for collection')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT):
        raise ValueError('same current immutable Main/Test/config source')
    prior,candidate,difference=candidate_main()
    before=json.loads((W/'pg5414-ownership-query-six-v1/begin.safe.json').read_bytes())
    data={'source':SOURCE,'priorManifestSha256':prior['serverManifestSha256'],'priorJarHashes':prior['jarHashes'],
        'archiveSha256':before['archiveSha256'],'aliases':{},'newCases':added_cases(),'candidateMain':candidate,
        'allMainSourceSha256':{path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw='import json\n'+''.join(name+'=set('+repr(sorted(difference[key]))+')\n' for name,key in (
        ('MODIFIED','modified'),('ADDED','added'),('REMOVED','removed')))+inspect.getsource(physical_difference)+'\n'+qualifier_source()+"\nprint(json.dumps(qualify("+repr(data)+")))\n"
    if check(raw,'<complete current all1664 original XML independent>'):raise ValueError('complete standalone static0 before output/transfer')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    path=out/'qualify.private.py'
    with path.open('x') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5416-whole-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only original qualifier namespace; inspect existing job instead of replay')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed independent payload transfer')
    code,output=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or output.split()[0]!=digest:raise ValueError('exact qualifier bytes before read-only execution')
    code,output=run('python3 -B '+remote+'/qualify.private.py',timeout=180)
    with(out/'observer.private.log').open('x') as stream:stream.write(output);stream.flush();os.fsync(stream.fileno())
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'formalAccepted':False,'wholeReplayed':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    with(out/'manifest.safe.json').open('x') as stream:json.dump(value,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({key:value[key] for key in value if key!='result'}))
    if code==0:print(json.dumps({key:value['result'][key] for key in ('tests','suites','mainClasses','staticSixModules','unchangedPhysicalClasses','global100','F03Accepted')}))
    return code


if __name__=='__main__':raise SystemExit(main())
