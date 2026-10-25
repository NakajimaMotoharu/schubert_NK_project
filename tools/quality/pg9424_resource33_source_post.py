"""Independent frozen Markdown oracle plus original artifact owners; never run subject tests."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9424-resource33-source-post-v1'
SUBJECT=BASE/'PG9422-resource33-source-metadata-v1'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1914_G13Resource33_製造artifact対応仕様.md'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validate(rows,expected):
    if rows!=expected:raise ValueError('frozen document primary/artifact/hash/runtime scope required')

def expected_profile(owner,description,logical):
    unit='src/deployment/systemd/'
    if owner=='WBS-P004-01':
        versions=re.findall(r'\bV\d{3}\b',description)
        if versions:
            assert len(versions)==1;paths=[p for p in logical if '/db/migration/'+versions[0]+'__' in p];assert len(paths)==1
            return versions[0],paths
        assert '全28' in description
        return 'SQL_ALL',sorted(p for p in logical if '/resources/db/' in p and p.endswith('.sql'))
    if owner=='WBS-C03':return 'PG_CONFIG',sorted(p for p in logical if p.startswith('src/deployment/postgresql/'))
    if owner=='WBS-C02':
        if 'API/Web' in description:return 'API_WEB_UNITS',[unit+'schubert-nk-api.service.template',unit+'schubert-nk-web.service.template']
        if '全C02' in description:return 'ALL_UNITS',sorted(p for p in logical if logical[p]['owner']=='WBS-C02')
        if 'artemis.service' in description:return 'ARTEMIS_UNIT',[unit+'artemis.service']
        if 'cleanup.service' in description:return 'CLEANUP_UNIT',[unit+'schubert-nk-cleanup.service.template']
        assert 'morning-controller/target' in description
        return 'MORNING_UNITS',[unit+'schubert-nk-morning-controller.service.template',unit+'schubert-nk-morning.target.template']
    if owner=='WBS-C08':return 'INSPECTOR_SCRIPT',['src/deployment/operations/inbox-inspector.sh.template',unit+'schubert-nk-inbox-inspector.service','src/deployment/config/inbox-inspector.env.template']
    if owner=='WBS-C04':return 'BROKER',['src/deployment/artemis/etc/broker.xml']
    if owner=='WBS-F02':
        module='batch' if 'batch/pom.xml' in description else 'web';assert module+'/pom.xml' in description
        return module.upper()+'_POM',['src/schubert-nk-'+module+'/pom.xml']
    assert owner=='WBS-P016-25' and description.endswith('.js')
    return description,['src/schubert-nk-web/src/main/resources/static/js/'+description]

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    spec_raw=SPEC.read_bytes();assert sha(spec_raw)=='6f5183ecbd3485723567f15d59b40eea9e094d9fddeae71a1e14a65ce344b365'
    oracle={}
    for line in spec_raw.decode().splitlines():
        if not line.startswith(('|api/','|batch/','|web/')):continue
        _,label,owner,description,_=line.split('|');module,name=label.split('/',1)
        path='src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+name+'.java'
        assert path not in oracle;oracle[path]=(owner,description)
    assert len(oracle)==33
    raw=(SUBJECT/'manifest.json').read_bytes();assert sha(raw)=='376d762a7f0806073fe2cc57692eca7842fb3323243e92b5fea3ac947081ab78'
    value=json.loads(raw);assert value['source']==SOURCE and value['actualExit']==0
    catalog=(SUBJECT/'candidates.json').read_bytes();assert sha(catalog)==value['candidatesSha256']=='cd7eee9a232333d120e0cd8a2262a300ae25b16a7bd12da11ae498a1c1ccb3ae'
    rows=json.loads(catalog);assert len(rows)==33 and {row['path'] for row in rows}==set(oracle)
    inv=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inv['artifacts']}
    graph_raw=(BASE/'PG9386-composite-reference-graph-v3/manifest.json').read_bytes();assert sha(graph_raw)==value['graphManifestSha256']=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(graph_raw);unresolved_raw=(BASE/'PG9386-composite-reference-graph-v3/unresolved.json').read_bytes();assert sha(unresolved_raw)==graph['unresolvedSha256']
    originals={row['path']:row for row in json.loads(unresolved_raw)}
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes();assert sha(normal_raw)==value['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(normal_raw)['begin']['inputHashes'];expected=[];witness_paths=set()
    for row in rows:
        path=row['path'];primary,description=oracle[path];original=originals[path];assert original['mainOwners']==[]
        profile,paths=expected_profile(primary,description,logical);witnesses=[]
        for artifact in paths:
            digest=sha((ROOT/artifact).read_bytes());assert digest==hashes[artifact]
            if artifact in logical:
                owner=logical[artifact]['owner'];assert owner==logical[artifact]['costOwner'];mode='ORIGINAL941_ARTIFACT_OWNER'
            else:assert primary=='WBS-F02' and artifact.endswith('/pom.xml');owner=primary;mode='EXPLICIT_481_F02_BUILD_DEPENDENCY_SCOPE_NOT_ORIGINAL941_ENTRY'
            witnesses.append(dict(path=artifact,sha256=digest,owner=owner,basis=mode));witness_paths.add(artifact)
        assert primary in {item['owner'] for item in witnesses} and sha((ROOT/path).read_bytes())==hashes[path]
        expected.append(dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,profile=profile,
          relatedOwners=sorted({item['owner'] for item in witnesses}-{primary}),originalReferenceOwners=[],reviewedArtifactWitnesses=witnesses,
          witnessScope='PRIMARY_RESPONSIBILITY_REVIEW_ONLY_NOT_EXHAUSTIVE_DEPENDENCIES',unresolvedRuntimeReasons=original['unresolvedReasons'],
          targetRuntimeAccepted=False,basis='EXACT_LITERAL_RESOURCE_SQL_UNIT_JS_BUILD_PRIMARY_1914_NOT_RUNTIME_PT'))
    validate(rows,expected);assert len(witness_paths)==value['uniqueArtifactWitnessFiles']==54
    for name,key in (('artifact-proofs.json','artifactProofsSha256'),('class-proofs.json','classProofsSha256')):assert sha((SUBJECT/name).read_bytes())==value[key]
    rejected=[]
    for label,edit in (('cost-only',lambda v:v[0].update(costOwner='WBS-G13.07')),('primary-forged',lambda v:v[0].update(owner='WBS-F01')),
      ('resource-owner-forged',lambda v:v[0]['reviewedArtifactWitnesses'][0].update(owner='WBS-F01')),('resource-byte-forged',lambda v:v[0]['reviewedArtifactWitnesses'][0].update(sha256='0'*64)),
      ('runtime-invented',lambda v:v[0].update(targetRuntimeAccepted=True)),('profile-forged',lambda v:v[0].update(profile='UNKNOWN')),
      ('complete-dependencies-invented',lambda v:v[0].update(witnessScope='ALL_DEPENDENCIES_VERIFIED')),('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0])))):
        changed=copy.deepcopy(rows);edit(changed)
        if label=='cost-only':assert {k for k in rows[0] if rows[0][k]!=changed[0][k]}=={'costOwner'}
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged artifact responsibility accepted')
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          subjectManifestSha256=sha(raw),specSha256=sha(spec_raw),catalogSha256=sha(catalog),primaryKeyKind='FULL_REPO_PATH',
          literalPrimaryOwners={p:row[0] for p,row in oracle.items()},primaryArtifactsVerified=54,sourceResponsibilitiesVerified=33,
          originalResourceOwnersPreserved=True,f02NotF01BuildScope=True,primaryWitnessNotExhaustiveDependencies=True,
          positiveBeforeNegatives=True,metadataCounterexamples=rejected,productTestsExecuted=0,newAccepted=0,coverage=None,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,sourceResponsibilities=33,artifactWitnesses=54,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
