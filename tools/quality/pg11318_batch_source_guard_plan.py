"""Add14 Test-owner exceptional lifetime guards and one executor TWR; preserve original oracle bodies."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical

OUT=data.BASE/'PG11318-batch-source-guard-plan-v1'
FILE='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchStandardMetricSourceTest.java'


def inputs():
    normal=data.read_checked(data.BASE/'PG11290-batch-standard-text-fixture-six-compile-v1/manifest.json',
        'e5f2c258d8faa0b303f3d74edae30c3dfc03adc3e8964290ac022e5d140104d9')
    review=data.read_checked(data.BASE/'PG11312-batch-resource-ownership-review-v1/manifest.json',
        'b672a132d30a89a0ef003a181f47aca733d6ceff5d07591736fd11274c52182a')
    sites=data.read_checked(data.BASE/'PG11312-batch-resource-ownership-review-v1/sites.json',review['sitesSha256'])
    methods=sorted(r['attributes']['method'] for r in sites if r['basis']['status']=='OWNER_EXCEPTIONAL_GUARD_GAP_BUG1908')
    assert len(methods)==len(set(methods))==14 and normal['actualExit']==normal['testsExecuted']==0
    assert normal['source']==review['source']=='d431ad964355c4e5c602fcb94fe0182da6ae3a61'
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    before=(snapshot/FILE).read_text()
    assert data.sha(before.encode())==normal['begin']['inputHashes'][FILE]
    return normal,before,methods


def body_span(text,name):
    matches=list(re.finditer(r'\bvoid\s+'+re.escape(name)+r'\(\)(?:\s+throws\s+Exception)?\s*\{',text))
    assert len(matches)==1
    start=matches[0].end()
    depth=1
    for m in LEX.finditer(text,start):
        if m.group()=='{':
            depth+=1
        elif m.group()=='}':
            depth-=1
        if depth==0:
            return start,m.start()
    raise ValueError('complete existing method body required')


def owner_end(body):
    matches=[m for m in LEX.finditer(body) if not m.group().startswith(('//','/*'))]
    indices=[i for i in range(len(matches)-2) if [m.group() for m in matches[i:i+3]]==['var','owner','=']]
    assert len(indices)==1
    levels={'(':0,'{':0,'[':0}
    right={')':'(','}':'{',']':'['}
    for m in matches[indices[0]:]:
        v=m.group()
        if v in levels:
            levels[v]+=1
        elif v in right:
            levels[right[v]]-=1
        if v==';' and not any(levels.values()):
            return m.end()
    raise ValueError('complete unique owner declaration required')


def transformed(before,methods):
    result=before
    spans=sorted(((*body_span(before,n),n) for n in methods),reverse=True)
    for start,end,name in spans:
        body=before[start:end]
        split=owner_end(body)
        prefix,rest=body[:split],body[split:]
        assert 'finally' not in canonical(rest) or name.startswith('batchhost016')
        if name.startswith('batchhost016'):
            old='    var executor = Executors.newFixedThreadPool(2);\n    try {'
            assert rest.count(old)==1
            rest=rest.replace(old,'    try (var executor = Executors.newFixedThreadPool(2)) {\n    try {',1)
            rest=rest.rstrip()+'\n    }\n'
        wrapped=prefix+'\n    try {\n'+rest.rstrip()+'\n    } finally {\n      owner.close();\n    }\n  '
        result=result[:start]+wrapped+result[end:]
    return result


def emit():
    _,before,methods=inputs()
    assert (data.ROOT/FILE).read_text()==before
    after=transformed(before,methods)
    diff=list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]
    return '*** Begin Patch\n*** Update File: '+str(data.ROOT/FILE)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in diff)+'\n*** End Patch\n'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,before,methods=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=FILE)
    after=(data.ROOT/FILE).read_text()
    assert canonical(after)==canonical(transformed(before,methods))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=[dict(path=FILE,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()))],
        guardedMethods=methods,ownerGuards=14,executorTwr=1,originalMethods=16,allMainAndOtherInputBytesPreserved=True,
        originalOracleInversePending=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
