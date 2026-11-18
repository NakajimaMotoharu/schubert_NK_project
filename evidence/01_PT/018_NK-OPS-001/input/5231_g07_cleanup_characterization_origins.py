"""Bind published static/characterization MD5-like scanner hits to exact public provenance."""
from pathlib import Path
import re
import runpy
import subprocess

HERE=Path(__file__)
R=runpy.run_path(str(HERE.with_name('5230_g07_cleanup_characterization_delta.py')))
p=R['U']['load']('g07_cleanup_classification','5182_g07_jdbc_metrics_cached_classification.py')
R['configure'](p.t.WRAPPER)
OUT,WORK,RETAIN=map(R.get,('OUT','TEMP','RETAIN'))
p.OUT=p.t.OUT=p.B.OUT=OUT
p.WORK=p.t.WORK=p.B.WORK=WORK
p.t.PREPARE_RUNS=('PG39792',)
p.t.CLASS_PACKAGES=frozenset(('storage','bootstrap','api','batch','protocol'))
p.t.ORDINARY_BUILD_RUNS=()
B=p.B
E=OUT.parent.parent
SLOTS=('PG39826-p020-definition-green144-v1','PG39830-p020-definition-green144-v3')
BUILD=E/'PG39804-cleanup-fixed-statement-four-main-v1/compile/manifest.json'
ORIGINAL_SOURCE=p.t.checked_source
ORIGINAL_CONTENT=p.proven_content
JAVA=Path.cwd().parent/'toolchain/jdk-25.0.4/bin/java'
CLI=Path.cwd().parent/'toolchain/org.jacoco.cli-0.8.15-nodeps.jar'
BUILD_INDEX={}
STATIC_OWNERS={}
DENY=B.HELD|{'RootFailedStartRecovery','NativeNkA01Capture','NativeNkL01Capture'}


def prev_lines():
    known=set()
    path=E/'PG39780-g07-four-build-and-trace-delta-v1/scan/manifest.json'
    for f in (path,E/'PG39730-g07-weblog-session-and-comparator-public-delta-v1/scan/manifest.json'):
        manifest=B.load(f)
        assert manifest['qualifiedRangeOnly'] and manifest['confirmedSecrets']==manifest['unresolvedCandidates']==0
        for filename in ('classified-findings.json','additional-build-origins.json'):
            entry=manifest['exactPrivateProofFiles'].get(filename)
            if entry is None:
                continue
            candidate=Path(entry['path'])
            assert candidate.is_relative_to(RETAIN.parent) and B.ref(candidate)==entry
            for row in B.load(candidate):
                if row['ground'] is not None:
                    known.add((row['rule'],row['lineSha256'],row['startColumn'],row['endColumn']))
    return known,B.ref(path)


def index_known_bytes():
    current=B.load(BUILD)
    workspace=Path(current['cwd'])
    assert workspace.parent==RETAIN.parent and workspace.resolve()==workspace
    assert current['actualExit']==0 and current['inputHashesReverified']
    for mod,paths in current['physicalClassHashes'].items():
        root=workspace/f'src/schubert-nk-{mod}/target/classes'
        add_physical(root,paths,BUILD)
    for slot in (*SLOTS,'PG39822-p020-definition-red-v1','PG39828-p020-definition-green144-v2'):
        manifest=E/slot/'manifest.json'
        content=B.load(manifest)
        for key,path_field in (('mainPhysical','classesDir'),('testPhysical','testsDir')):
            root=Path(content[path_field])
            assert root.is_relative_to(RETAIN.parent) and root.resolve()==root
            add_physical(root,content[key],manifest)
        init=content['initLog']
        if init:
            f=Path(init['path'])
            assert f.is_relative_to(RETAIN.parent) and f.resolve()==f
            STATIC_OWNERS[init['sha256'].encode()]=(f,B.ref(manifest))
    return len(BUILD_INDEX)


def add_physical(root,paths,manifest):
    pin=B.ref(manifest)
    for name,value in paths.items():
        relative=Path(name)
        if relative.stem.split('$')[0] in DENY:
            continue
        assert not relative.is_absolute() and '..' not in relative.parts
        BUILD_INDEX[value.encode()]=(root/relative,pin,name)


def exact_source(path,value,commit):
    old=ORIGINAL_SOURCE(path,value,commit)
    if old:
        return old
    candidate=Path(path)
    if (candidate.is_absolute() or '..' in candidate.parts or candidate.stem.split('$')[0] in DENY or
            not path.startswith(('program/characterization/','tools/quality/static/'))):
        return None
    hit=p.t.source_versions(commit,path).get(value)
    if hit:
        oid,revision=hit
        return dict(kind='Exact non-secret characterization source/fixture Git bytes',path=path,object=oid,commit=revision)
    return None


def content_hits(line,a,z,digests,reachable):
    old=ORIGINAL_CONTENT(line,a,z,digests,reachable)
    if old:
        return old
    tokens=[token[1] for token in p.TOKEN.finditer(line)
       if max(0,min(token.end(1),z+1)-max(token.start(1),a-2))>=len(token[1])-1]
    if len(tokens)!=1:
        return None
    value=tokens[0]
    if value in BUILD_INDEX:
        path,pin,label=BUILD_INDEX[value]
        assert path.resolve()==path and B.ref(path)['sha256']==value.decode()
        return dict(kind='Exact published compiled class receipt',classPath=label,receipt=pin)
    if value in STATIC_OWNERS:
        path,pin=STATIC_OWNERS[value]
        assert B.ref(path)['sha256']==value.decode()
        return dict(kind='Exact ordinary test initialization log digest only',receipt=pin)
    return None


def qualify_exec(row,meta):
    path=Path(row['path'])
    terminal=path.with_name('manifest.json')
    begin=path.with_name('begin.json')
    receipt=B.load(terminal)
    start=B.load(begin)
    assert start['expected']==receipt['expected']==144 and start['source']==receipt['source']
    assert receipt['stages']['test']['actualExit']==receipt['stages']['main']['actualExit']==0
    expected_failed=path.parent.name==SLOTS[0]
    assert receipt['stages']['unit']['actualExit']==int(expected_failed)
    local=WORK/meta['relativeProjection']
    assert B.ref(local)['sha256']==meta['blobSha256']==B.ref(path)['sha256']
    assert B.ref(CLI)==start['tools'][CLI.name]
    cmd=[str(JAVA),'-jar',str(CLI),'execinfo',str(local)]
    proc=subprocess.run(cmd,capture_output=True,timeout=30)
    stdout=proc.stdout.decode()
    assert proc.returncode==0 and not proc.stderr
    sessions=re.findall(r'^Session "([^"]+)":',stdout,re.M)
    assert sessions==[receipt['session']]
    probes=re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',stdout,re.M)
    assert any(n=='dev/codex/schubert/characterization/ArtifactComparator' and int(hit)>0 for _,hit,_,n in probes)
    assert not any(n.startswith(('dev/codex/schubert/nk/','org/postgresql/','com/microsoft/playwright/')) for _,_,_,n in probes)
    return dict(row,actualExit=0,originalUnitExit=int(expected_failed),ordinaryProbeDataOnly=True,
                tool=ref_tool(),session=receipt['session'],rowCount=len(probes),owner=B.ref(terminal),
                parserStdoutSha256=B.sha(proc.stdout),command=cmd)


def ref_tool():
    return B.ref(CLI)


def binary_extra(rows,by_key,scan):
    converted=[]
    for row in rows:
        if row.get('actualExit')==0:
            continue
        path=Path(row['path'])
        if path.parent.name in SLOTS and path.name=='jacoco.exec':
            converted.append(qualify_exec(row,by_key[row['path'],row['blob']]))
    return converted


if __name__=='__main__':
    index_known_bytes()
    p.exact_previous=prev_lines
    p.t.checked_source=exact_source
    p.t.extra_binary=binary_extra
    p.proven_content=content_hits
    p.main()
