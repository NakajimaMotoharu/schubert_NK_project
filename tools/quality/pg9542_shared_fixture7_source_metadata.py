"""Shared fixture7 explicit DDL/common-contract responsibility; never SQL, child or target execution."""
import datetime as dt
import hashlib
import json
from pathlib import Path
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9542-shared-fixture7-source-metadata-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
TABLE=[
 ('batch','batch/repository/BatchDatabaseFixture','SQL','WBS-P004-01'),
 ('batch','batch/repository/BatchFixtureOwnershipTest','SQL_VIA:BatchDatabaseFixture','WBS-P004-01'),
 ('bootstrap','api/logging/ApiLogDatabaseFixture','SQL','WBS-P004-01'),
 ('bootstrap','api/logging/ApiLogFixtureOwnershipTest','SQL_VIA:ApiLogDatabaseFixture','WBS-P004-01'),
 ('web','web/logging/WebLogDatabaseFixture','SQL','WBS-P004-01'),
 ('web','web/logging/WebLogDatabaseFixtureTest','SQL_VIA:WebLogDatabaseFixture','WBS-P004-01'),
 ('bootstrap','api/file/OwnedRetentionProcess','COMMON_MAIN:ServiceProcessResources','WBS-P018-04')]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')

def consumers_of(classes,path):
    declared={c['className'] for c in classes if c['path']==path}
    assert declared and all({c['path'] for c in classes if c['className']==s}=={path} for s in declared)
    return {c['path'] for c in classes if c['path']!=path and declared.intersection(c['references'])}

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    gd=BASE/'PG9386-composite-reference-graph-v3';gr=(gd/'manifest.json').read_bytes()
    assert sha(gr)=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15';graph=json.loads(gr)
    blobs={}
    for name,key in [('test-class-metadata.json','testMetadataSha256'),('main-class-sources.json','mainMapSha256'),('unresolved.json','unresolvedSha256')]:
        raw=(gd/name).read_bytes();assert sha(raw)==graph[key];blobs[name]=json.loads(raw)
    classes=blobs['test-class-metadata.json'];mains=blobs['main-class-sources.json'];original={x['path']:x for x in blobs['unresolved.json']}
    pr=(BASE/'PG9534-fixture-consumer5-source-join-v1/manifest.json').read_bytes()
    assert sha(pr)=='69d5360bb5d7fb9f8e9eef09ca7427ecb24f01acfa3c682a5eb9bc41033a62e8'
    prior=json.loads(pr);assert prior['actualExit']==0 and prior['source']==SOURCE
    owners={x['path']:x['canonicalOwner'] for x in prior['sourceRows']}
    logical={x['path']:x for x in json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,x in logical.items():assert x['owner']==x['costOwner'];owners[path]=x['owner']
    nr=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes()
    assert sha(nr)=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(nr)['begin']['inputHashes'];snapshot=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'
    sql=sorted(p for p in logical if '/resources/db/' in p and p.endswith('.sql'))
    assert sql and all(logical[p]['owner']=='WBS-P004-01' for p in sql)
    candidates=[];witnessed={}
    for module,name,profile,primary in TABLE:
        path='src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+name+'.java'
        assert path not in owners and original[path]['mainOwners']==[]
        text=(ROOT/path).read_text();assert sha(text.encode())==hashes[path]==sha((snapshot/path).read_bytes())
        consumers=consumers_of(classes,path);paths=[];via=None;common=[]
        if profile=='SQL' or profile.startswith('SQL_VIA:'):
            assert primary=='WBS-P004-01';paths=sql
            if profile=='SQL':
                assert all(token in text for token in ('src/schubert-nk-api/src/main/resources/db','provisioning/001_roles.sql','migration','Flyway.configure()'))
            else:
                stem=profile.split(':')[1];matches={c['path'] for c in classes if c['module']==module and c['sourceFile']==stem+'.java'}
                assert len(matches)==1;via=next(iter(matches))
                declared={c['className'] for c in classes if c['path']==via}
                assert any(declared.intersection(c['references']) for c in classes if c['path']==path)
                body=(ROOT/via).read_text();assert sha(body.encode())==hashes[via]
                assert all(t in body for t in ('src/schubert-nk-api/src/main/resources/db','provisioning/001_roles.sql','migration','Flyway.configure()'))
        else:
            assert profile=='COMMON_MAIN:ServiceProcessResources' and len(consumers)==6
            sets=[{n for c in classes if c['path']==p for n in c['references'] if n in mains} for p in consumers]
            common=sorted(set.intersection(*sets))
            assert common==['dev/codex/schubert/nk/api/file/ServiceProcessResources']
            main=mains[common[0]];assert main['owner']==primary=='WBS-P018-04'
            paths=[main['path']];assert logical[paths[0]]['owner']==primary
        artifacts=[]
        for artifact in paths:
            assert sha((ROOT/artifact).read_bytes())==hashes[artifact]==sha((snapshot/artifact).read_bytes())
            w=dict(path=artifact,sha256=hashes[artifact],owner=logical[artifact]['owner'],basis='ORIGINAL941_RESOURCE_OR_MAIN_OWNER')
            artifacts.append(w);witnessed[artifact]=w
        related=sorted({owners[p] for p in consumers if p in owners}-{primary})
        candidate=dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,profile=profile,viaFixture=via,
          originalReferenceOwners=[],relatedOwners=related,reviewedArtifactWitnesses=artifacts,
          directConsumerPaths=sorted(consumers),unregisteredConsumerPaths=sorted(p for p in consumers if p not in owners),
          uniqueCommonMainClassSymbols=common,witnessScope='PRIMARY_DDL_OR_COMMON_CONTRACT_SUPPORT_NOT_ALL_METHODS_OR_RUNTIME',
          unresolvedRuntimeReasons=original[path]['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='EXACT_LITERAL_SHARED_FIXTURE_RESOURCE_OR_COMMON_MAIN_1934_NOT_RUNTIME_PT')
        candidates.append(candidate)
    assert len(candidates)==7
    verify(invocation);OUT.mkdir();write(OUT/'candidates.json',candidates);write(OUT/'artifact-proofs.json',witnessed)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      graphManifestSha256=sha(gr),priorManifestSha256=sha(pr),normalManifestSha256=sha(nr),fixtureSources=7,
      sqlArtifactCount=len(sql),uniqueArtifactWitnessFiles=len(witnessed),ownedRetentionDirectConsumers=6,
      candidatesSha256=sha((OUT/'candidates.json').read_bytes()),artifactProofsSha256=sha((OUT/'artifact-proofs.json').read_bytes()),
      targetRuntimeInvocations=0,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,fixtures=7,sqlArtifacts=len(sql),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
