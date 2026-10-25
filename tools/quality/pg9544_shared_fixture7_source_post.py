"""Independent raw class and frozen SQL/common-Main fixture proof; no target execution."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import class_reference_metadata as parser
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9544-shared-fixture7-source-post-v1'
SUBJECT=BASE/'PG9542-shared-fixture7-source-metadata-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validate(rows,expected):
    if rows!=expected:raise ValueError('exact frozen shared fixture resource/common-Main contract required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    spec=(ROOT/'evidence/01_PT/018_NK-OPS-001/1934_G13SharedFixture7_資源・共通Main責任仕様.md').read_bytes()
    assert sha(spec)=='2ebcefb49135c8c941960481ad15a1e3b4d8df3a27ba226e9e71a315b1f2285d'
    oracle={}
    for line in spec.decode().splitlines():
        if not line.startswith('|schubert-nk-'):continue
        _,relative,owner,description,_=line.split('|');path='src/'+relative
        assert path not in oracle;oracle[path]=(owner,description.split(';')[0])
    assert len(oracle)==7
    sr=(SUBJECT/'manifest.json').read_bytes();assert sha(sr)=='5e231aad063060ee16adb8eb4bf6e281df3a6ac3e8eca6d0b20de9ead46ea513'
    subject=json.loads(sr);assert subject['actualExit']==0 and subject['source']==SOURCE
    cr=(SUBJECT/'candidates.json').read_bytes();assert sha(cr)==subject['candidatesSha256']=='554b712174726e9bea65c9cdd387703ab0167995428e9190d741951e18ee6163'
    rows=json.loads(cr);assert len(rows)==7 and {r['path'] for r in rows}==set(oracle)
    gd=BASE/'PG9386-composite-reference-graph-v3';gr=(gd/'manifest.json').read_bytes()
    assert sha(gr)==subject['graphManifestSha256']=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(gr);inputs={}
    for name,key in [('test-class-metadata.json','testMetadataSha256'),('main-class-sources.json','mainMapSha256'),('unresolved.json','unresolvedSha256')]:
        data=(gd/name).read_bytes();assert sha(data)==graph[key];inputs[name]=json.loads(data)
    original={x['path']:x for x in inputs['unresolved.json']};mains=inputs['main-class-sources.json']
    dirs={Path(p).parent.parent.name.removeprefix('schubert-nk-'):Path(p) for p in graph['treePins']}
    classes=[]
    for stored in inputs['test-class-metadata.json']:
        raw=(dirs[stored['module']]/stored['entry']).read_bytes();assert sha(raw)==stored['sha256']
        actual=parser.read(raw);assert all(actual[k]==stored[k] for k in ('className','sourceFile','references','reflectiveOrDynamicLookup'))
        p='src/schubert-nk-'+stored['module']+'/src/test/java/'+actual['className'].rpartition('/')[0]+'/'+actual['sourceFile']
        assert p==stored['path'];classes.append(dict(path=p,module=stored['module'],**actual))
    assert len(classes)==1910
    pr=(BASE/'PG9534-fixture-consumer5-source-join-v1/manifest.json').read_bytes()
    assert sha(pr)==subject['priorManifestSha256']=='69d5360bb5d7fb9f8e9eef09ca7427ecb24f01acfa3c682a5eb9bc41033a62e8'
    prior=json.loads(pr);assert prior['actualExit']==0 and prior['source']==SOURCE
    owners={r['path']:r['canonicalOwner'] for r in prior['sourceRows']}
    logical={r['path']:r for r in json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for p,r in logical.items():assert r['owner']==r['costOwner'];owners[p]=r['owner']
    nr=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes()
    assert sha(nr)==subject['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(nr)['begin']['inputHashes'];sql=sorted(p for p in logical if '/resources/db/' in p and p.endswith('.sql'))
    assert len(sql)==subject['sqlArtifactCount']==29 and all(owners[p]=='WBS-P004-01' for p in sql)
    expected=[];all_artifacts=set()
    for row in rows:
        path=row['path'];primary,profile=oracle[path];assert path not in owners and original[path]['mainOwners']==[]
        assert sha((ROOT/path).read_bytes())==hashes[path]
        declared={c['className'] for c in classes if c['path']==path}
        assert declared and all({c['path'] for c in classes if c['className']==symbol}=={path} for symbol in declared)
        consumers={c['path'] for c in classes if c['path']!=path and declared.intersection(c['references'])}
        via=None;common=[];module=path.split('/')[1].removeprefix('schubert-nk-')
        if profile in ('SQL','SQL_VIA:BatchDatabaseFixture','SQL_VIA:ApiLogDatabaseFixture','SQL_VIA:WebLogDatabaseFixture'):
            assert primary=='WBS-P004-01';paths=sql
            if profile=='SQL':fixture=path
            else:
                stem=profile.split(':')[1];matches={c['path'] for c in classes if c['module']==module and c['sourceFile']==stem+'.java'}
                assert len(matches)==1;fixture=via=next(iter(matches));symbols={c['className'] for c in classes if c['path']==fixture}
                assert any(symbols.intersection(c['references']) for c in classes if c['path']==path)
            text=(ROOT/fixture).read_text();assert sha(text.encode())==hashes[fixture]
            assert all(s in text for s in ('src/schubert-nk-api/src/main/resources/db','provisioning/001_roles.sql','migration','Flyway.configure()'))
        else:
            assert profile=='COMMON_MAIN:ServiceProcessResources' and primary=='WBS-P018-04' and len(consumers)==6
            sets=[{r for c in classes if c['path']==p for r in c['references'] if r in mains} for p in consumers]
            common=sorted(set.intersection(*sets));assert common==['dev/codex/schubert/nk/api/file/ServiceProcessResources']
            paths=[mains[common[0]]['path']];assert mains[common[0]]['owner']==owners[paths[0]]==primary
        witnesses=[]
        for p in paths:
            assert sha((ROOT/p).read_bytes())==hashes[p]
            witnesses.append(dict(path=p,sha256=hashes[p],owner=owners[p],basis='ORIGINAL941_RESOURCE_OR_MAIN_OWNER'));all_artifacts.add(p)
        expected.append(dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,profile=profile,viaFixture=via,
          originalReferenceOwners=[],relatedOwners=sorted({owners[p] for p in consumers if p in owners}-{primary}),
          reviewedArtifactWitnesses=witnesses,directConsumerPaths=sorted(consumers),
          unregisteredConsumerPaths=sorted(p for p in consumers if p not in owners),uniqueCommonMainClassSymbols=common,
          witnessScope='PRIMARY_DDL_OR_COMMON_CONTRACT_SUPPORT_NOT_ALL_METHODS_OR_RUNTIME',
          unresolvedRuntimeReasons=original[path]['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='EXACT_LITERAL_SHARED_FIXTURE_RESOURCE_OR_COMMON_MAIN_1934_NOT_RUNTIME_PT'))
    assert len(all_artifacts)==subject['uniqueArtifactWitnessFiles']==30
    validate(rows,expected);rejected=[]
    for label,edit in (('cost-only',lambda v:v[0].update(costOwner='WBS-G13.07')),
      ('artifact-owner-forged',lambda v:v[0]['reviewedArtifactWitnesses'][0].update(owner='WBS-G13.07')),
      ('artifact-byte-forged',lambda v:v[0]['reviewedArtifactWitnesses'][0].update(sha256='0'*64)),
      ('common-main-forged',lambda v:v[-1].update(uniqueCommonMainClassSymbols=['p/Forged'])),
      ('consumer-missing',lambda v:v[-1]['directConsumerPaths'].pop()),
      ('unregistered-consumers-hidden',lambda v:v[0].update(unregisteredConsumerPaths=['FORGED'])),
      ('profile-forged',lambda v:v[0].update(profile='SQL_VIA:Foreign')),
      ('runtime-invented',lambda v:v[0].update(targetRuntimeAccepted=True)),
      ('all-dependencies-invented',lambda v:v[0].update(witnessScope='ALL_DEPENDENCIES_ACCEPTED')),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0])))):
        changed=copy.deepcopy(rows);edit(changed);assert changed!=rows
        if label=='cost-only':assert {k for k in changed[0] if changed[0][k]!=rows[0][k]}=={'costOwner'}
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged shared fixture responsibility accepted')
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as f:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          subjectManifestSha256=sha(sr),specSha256=sha(spec),catalogSha256=sha(cr),primaryKeyKind='FULL_REPO_PATH',
          literalPrimaryOwners={p:v[0] for p,v in oracle.items()},independentlyParsedClassFiles=1910,sourceResponsibilitiesVerified=7,
          primaryArtifactWitnessFiles=30,sqlArtifacts=29,uniqueCommonMainContracts=1,ownedRetentionDirectConsumers=6,
          metadataCounterexamples=rejected,positiveBeforeNegatives=True,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False),f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(dict(actualExit=0,fixtures=7,artifactWitnesses=30,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
