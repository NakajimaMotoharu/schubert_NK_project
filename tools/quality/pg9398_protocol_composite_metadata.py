"""Ten reviewed protocol primary responsibilities, preserving real cross-owner references."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg9360_static_companion_javap_metadata as javap
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9398-protocol-composite-metadata-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9398-protocol-composite-metadata-v1'
TC=ROOT.parent/'toolchain'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
PREFIX='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/'
PRIMARY={
 'codec/AuthenticationErrorProfileTest.java':('WBS-P002-02','codec/PayloadCodec.java'),
 'codec/MessageCodecTest.java':('WBS-P002-03','codec/HeaderCodec.java'),
 'codec/PayloadGoldenVectorTest.java':('WBS-P002-02','codec/PayloadCodec.java'),
 'codec/ScenarioRecordEncodingTest.java':('WBS-P002-02','codec/PayloadCodec.java'),
 'header/HeaderModelTest.java':('WBS-P001-01','header/CommonHeader.java'),
 'layout/IndependentNamedFieldOracle.java':('WBS-P001-03','layout/TypedPayloadValues.java'),
 'layout/LayoutMetadataTest.java':('WBS-P001-02','layout/LayoutRegistry.java'),
 'layout/SemanticFieldValueTest.java':('WBS-P001-03','layout/TypedFieldValues.java'),
 'layout/semantic/EnumWireCompatibilityTest.java':('WBS-P002-01','layout/semantic/AnswerState.java'),
 'layout/semantic/ProtocolSemanticTypeTest.java':('WBS-P002-01','layout/semantic/WireEnum.java')}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    graph_dir=BASE/'PG9386-composite-reference-graph-v3'
    raw=(graph_dir/'manifest.json').read_bytes();assert sha(raw)=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(raw);assert graph['source']==SOURCE and graph['actualExit']==0
    for path,key in (('unresolved.json','unresolvedSha256'),('main-class-sources.json','mainMapSha256'),('test-class-metadata.json','testMetadataSha256')):
        assert sha((graph_dir/path).read_bytes())==graph[key]
    unresolved={row['path']:row for row in json.loads((graph_dir/'unresolved.json').read_bytes())}
    main_classes=json.loads((graph_dir/'main-class-sources.json').read_bytes());test_classes=json.loads((graph_dir/'test-class-metadata.json').read_bytes())
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json';assert sha(normal_path.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    normal=json.loads(normal_path.read_bytes());hashes=normal['begin']['inputHashes']
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inventory['artifacts']}
    prior_path=BASE/'PG9390-composite-owner-join-v1/manifest.json';assert sha(prior_path.read_bytes())=='90b5394c4afd5f9ee468620f9ef593f49ae350969e144d5d0db9b425ee03d602'
    known={row['path']:row for row in json.loads(prior_path.read_bytes())['sourceRows']}
    selected=[row for row in test_classes if row['path'].startswith(PREFIX) and row['path'].removeprefix(PREFIX) in PRIMARY]
    assert {row['path'] for row in selected}=={PREFIX+path for path in PRIMARY}
    directory=next(Path(path) for path in graph['treePins'] if '/schubert-nk-protocol/' in path)
    os.umask(0o077);SLOT.mkdir();receipts=[];metadata={}
    for offset in range(0,len(selected),40):
        batch=selected[offset:offset+40]
        argv=[str(TC/'jdk-25.0.4/bin/javap'),'-v','-p','-classpath',str(directory)]+[row['className'].replace('/','.') for row in batch]
        process=subprocess.Popen(argv,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
        write(SLOT/(str(offset)+'-process.safe.json'),dict(pid=process.pid,ownerPid=os.getpid(),command=argv,startUTC=dt.datetime.now(dt.timezone.utc).isoformat()))
        timed_out=False
        try:stdout,stderr=process.communicate(timeout=120)
        except subprocess.TimeoutExpired:timed_out=True;process.kill();stdout,stderr=process.communicate(timeout=15)
        receipt=dict(command=argv,actualExit=process.returncode,timedOut=timed_out,stdoutSha256=sha(stdout),stderrSha256=sha(stderr),rawOutputPersisted=False)
        write(SLOT/(str(offset)+'-exit.safe.json'),receipt);receipts.append(receipt)
        assert process.returncode==0 and not stderr and not timed_out
        parsed={row['className']:row for row in javap.parse_metadata(stdout.decode())}
        assert set(parsed)=={row['className'] for row in batch}
        for row in batch:
            fresh=parsed[row['className']];assert fresh['sourceFile']==row['sourceFile'] and sha((directory/row['entry']).read_bytes())==row['sha256']
            owners={name for name,_ in fresh['refs'] if name.startswith('dev/codex/schubert/nk/')}
            assert owners=={name for name in row['references'] if name.startswith('dev/codex/schubert/nk/')}
            metadata[row['key']]=dict(path=row['path'],sourceFile=fresh['sourceFile'],projectClassReferences=sorted(owners))
    main_prefix=PREFIX.replace('/src/test/java/','/src/main/java/');candidates=[]
    for relative,(owner,subject) in sorted(PRIMARY.items()):
        path=PREFIX+relative;main=main_prefix+subject;original=unresolved[path]
        assert path not in logical and path not in known and original['sha256']==hashes[path]==sha((ROOT/path).read_bytes())
        assert hashes[main]==sha((ROOT/main).read_bytes()) and (logical[main]['owner'],logical[main]['costOwner'])==(owner,owner)
        assert owner in original['mainOwners']
        candidates.append(dict(path=path,sha256=hashes[path],owner=owner,costOwner=owner,subjectMainPath=main,subjectMainSha256=hashes[main],
          relatedOwners=sorted(set(original['mainOwners'])-{owner}),originalReferenceOwners=original['mainOwners'],
          unresolvedRuntimeReasons=original['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='LITERAL_PRIMARY_AND_RELATED_RESPONSIBILITY_1910_ORIGINAL_PT_SPEC_CURRENT_SOURCE_STATIC_ONLY'))
    names_path=ROOT/'src/schubert-nk-protocol/src/test/resources/protocol/named-types-ss323.tsv'
    assert sha(names_path.read_bytes())==hashes[str(names_path.relative_to(ROOT))]
    types=set()
    for line in names_path.read_text().splitlines():
        if not line or line.startswith('#'):continue
        cells=line.split('\t');assert len(cells)==3
        types.update(name for name in cells[1:] if name!='-')
    named={}
    for name in types:
        matches={value['path'] for value in main_classes.values() if Path(value['path']).stem==name}
        assert len(matches)==1;path=next(iter(matches));assert logical[path]['owner']==logical[path]['costOwner']=='WBS-P001-03'
        assert hashes[path]==sha((ROOT/path).read_bytes());named[name]=dict(path=path,sha256=hashes[path],owner='WBS-P001-03')
    assert len(named)==69
    jar=normal['jars']['protocol'];assert sha(Path(jar['path']).read_bytes())==jar['sha256']
    subjects=sorted({subject for _,subject in PRIMARY.values()})
    argv=[str(TC/'jdk-25.0.4/bin/javap'),'-p','-classpath',jar['path']]+['dev.codex.schubert.nk.protocol.'+p.removesuffix('.java').replace('/','.') for p in subjects]
    result=subprocess.run(argv,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120,check=False)
    assert result.returncode==0 and not result.stderr
    compiled=[line.removeprefix('Compiled from "').removesuffix('"') for line in result.stdout.decode().splitlines() if line.startswith('Compiled from "')]
    assert compiled==[Path(path).name for path in subjects]
    receipts.append(dict(command=argv,actualExit=0,stdoutSha256=sha(result.stdout),stderrSha256=sha(result.stderr),rawOutputPersisted=False))
    verify(invocation);OUT.mkdir();write(OUT/'candidates.json',candidates);write(OUT/'class-proofs.json',metadata);write(OUT/'named-dto-fixture-targets.json',named)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      graphManifestSha256=sha(raw),priorJoinSha256=sha(prior_path.read_bytes()),normalManifestSha256=sha(normal_path.read_bytes()),
      candidates=10,independentTestClasses=len(selected),subjectMainSourceFiles=len(subjects),namedDtoFixtureTypes=69,
      fixtureSha256=sha(names_path.read_bytes()),receipts=receipts,candidatesSha256=sha((OUT/'candidates.json').read_bytes()),
      classProofsSha256=sha((OUT/'class-proofs.json').read_bytes()),namedTargetsSha256=sha((OUT/'named-dto-fixture-targets.json').read_bytes()),
      originalMultipleOwnersPreserved=True,reflectionHelperExecuted=False,productTestsExecuted=0,targetCompile=0,targetRuntimeClassLoading=0,
      newAccepted=0,newTestIds=0,newMain=0,coverage=None,formalUpdated=False,wholeG13Accepted=False,effortPercent=None)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,candidates=10,testClasses=len(selected),namedFixtureTypes=69,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
