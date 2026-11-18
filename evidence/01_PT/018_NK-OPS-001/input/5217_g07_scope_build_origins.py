"""Ground exact positions, logical build evidence and the one new selected JaCoCo exec."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import gzip
import json
import re

ENTRY=Path(__file__).resolve()
spec=spec_from_file_location('g07_scope_range',ENTRY.with_name('5216_g07_scope_build_delta.py'))
r=module_from_spec(spec)
spec.loader.exec_module(r)
p=r.load('g07_scope_cached_origins','5182_g07_jdbc_metrics_cached_classification.py')
r.configure(p.t.WRAPPER)
p.OUT=p.t.OUT=p.B.OUT=r.OUT
p.WORK=p.t.WORK=p.B.WORK=r.TEMP
p.t.PREPARE_RUNS=('PG39752',)
p.t.ORDINARY_BUILD_RUNS=()
B=p.B
BEFORE=r.EVIDENCE/'PG39730-g07-weblog-session-and-comparator-public-delta-v1/scan/manifest.json'
POST=r.EVIDENCE/'PG39760-process-resource-scope-post-v1/manifest.json'
BUILD=r.EVIDENCE/'PG39764-process-resource-scope-four-main-v1/compile/manifest.json'
TARGET='dev/codex/schubert/nk/batch/platform/ProcessResourceScope'


def previous_lines():
    previous=B.load(BEFORE)
    assert previous['qualifiedRangeOnly'] and previous['confirmedSecrets']==previous['unresolvedCandidates']==0
    hits=set()
    for key in ('classified-findings.json','additional-build-origins.json'):
        pin=previous['exactPrivateProofFiles'][key]
        where=Path(pin['path'])
        assert where.is_relative_to(r.RETAIN.parent) and B.ref(where)==pin
        for location in B.load(where):
            if location['ground'] is not None:
                hits.add((location['rule'],location['lineSha256'],location['startColumn'],location['endColumn']))
    return hits,B.ref(BEFORE)


def measurement():
    old=B.load(POST)
    execinfo=POST.with_name('unit-execinfo.stdout')
    original=gzip.decompress(execinfo.with_suffix('.stdout.gz').read_bytes())
    assert B.sha(original)==old['files'][execinfo.name]
    assert old['tests']==4 and old['actualExit']==0 and old['oldExecCombined'] is False
    lines=original.decode().splitlines()
    sessions=[x for x in lines if x.startswith('Session ')]
    assert len(sessions)==1 and old['run'] in sessions[0]
    return old,lines


def crc_match(location,key,value):
    if location!=POST or len(value)!=16:
        return None
    old,lines=measurement()
    if old['classIds'].get(key)!=value:
        return None
    probes=[line.split() for line in lines if line.split() and line.split()[-1]==key]
    if len(probes)==1 and probes[0][0]==value:
        return dict(kind='Original resource-scope selected exec CRC',receipt=B.ref(POST),classReference=key)
    return None


def binary(rows,by_key,scan):
    result=[]
    for row in rows:
        file=Path(row['path'])
        if row.get('actualExit')==0 or file!=POST.with_name('jacoco.exec'):
            continue
        props=by_key[(row['path'],row['blob'])]
        target=r.TEMP/props['relativeProjection']
        old,lines=measurement()
        assert B.ref(target)['sha256']==props['blobSha256']==old['files']['jacoco.exec']
        codes=[line for line in lines if re.fullmatch(r'[0-9a-f]{16}\s+\d+ of\s+\d+\s+\S+',line)]
        assert any(line.split()[-1]==TARGET for line in codes)
        result.append(dict(row,actualExit=0,owner=B.ref(POST),derivedRows=len(codes),
                           scope='Original local four-memory-tests JaCoCo receipt, no runtime verification'))
    return result


def current_build_class_digests():
    m=B.load(BUILD)
    assert m['actualExit']==0 and m['inputHashesReverified']
    folder=Path(m['cwd'])
    assert folder.is_relative_to(r.RETAIN.parent) and folder.resolve()==folder
    result={}
    for module,classes in m['physicalClassHashes'].items():
        for name,digest in classes.items():
            assert Path(name).stem.split('$')[0] not in B.HELD
            path=folder/f'src/schubert-nk-{module}/target/classes'/name
            result[digest.encode()]=(path,name)
    assert len(result)==1101
    return result


def content(line,first,last,digests,reachable):
    decision=original_content(line,first,last,digests,reachable)
    if decision:
        return decision
    candidates=[token for token in p.TOKEN.finditer(line)
       if max(0,min(token.end(1),last+1)-max(token.start(1),first-2))>=len(token[1])-1]
    if len(candidates)!=1:
        return None
    raw=candidates[0][1]
    if raw not in classes:
        return None
    path,name=classes[raw]
    assert path.resolve()==path and B.ref(path)['sha256']==raw.decode()
    return dict(kind='Exact compiled class from the fixed four-module build',receipt=B.ref(BUILD),classReference=name)


original_content=p.proven_content
classes={}
if __name__=='__main__':
    classes.update(current_build_class_digests())
    p.exact_previous=previous_lines
    p.t.checked_run_id=crc_match
    p.t.extra_binary=binary
    p.proven_content=content
    p.main()
