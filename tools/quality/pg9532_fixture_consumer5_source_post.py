"""Independently parse all saved ClassFiles and frozen consumer table; no class loading/runtime."""
from collections import defaultdict
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import class_reference_metadata as parser
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9532-fixture-consumer5-source-post-v1'
SUBJECT=BASE/'PG9530-fixture-consumer5-source-metadata-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validate(rows,expected):
    if rows!=expected:raise ValueError('exact complete consumer symbols, source bytes and responsibility required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    spec=(ROOT/'evidence/01_PT/018_NK-OPS-001/1932_G13FixtureConsumer5_単一担当根拠仕様.md').read_bytes()
    assert sha(spec)=='824bb0e0a3a05849f56eec7af4e9b399043ff4dfa23e69b8555630d5084691a1'
    oracle={}
    for line in spec.decode().splitlines():
        if not line.startswith('|schubert-nk-'):continue
        _,relative,primary,consumers,_=line.split('|');path='src/'+relative
        assert path not in oracle;oracle[path]=(primary,set(consumers.split(',')))
    assert len(oracle)==5
    raw=(SUBJECT/'manifest.json').read_bytes();assert sha(raw)=='8442076f79987ef37da29f49b1c46c496e41141aa3f84042c28266dd323aae4a'
    subject=json.loads(raw);assert subject['source']==SOURCE and subject['actualExit']==0
    catalog=(SUBJECT/'candidates.json').read_bytes();assert sha(catalog)==subject['candidatesSha256']=='c41e36744c0b7ba066ec19079511ae30b52c1dc13edb18a6e784f1101fb17b93'
    rows=json.loads(catalog);assert len(rows)==5 and {x['path'] for x in rows}==set(oracle)
    graph_dir=BASE/'PG9386-composite-reference-graph-v3';graph_raw=(graph_dir/'manifest.json').read_bytes()
    assert sha(graph_raw)==subject['graphManifestSha256']=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(graph_raw)
    class_raw=(graph_dir/'test-class-metadata.json').read_bytes();unknown_raw=(graph_dir/'unresolved.json').read_bytes()
    assert sha(class_raw)==graph['testMetadataSha256'] and sha(unknown_raw)==graph['unresolvedSha256']
    originals={x['path']:x for x in json.loads(unknown_raw)}
    directories={Path(p).parent.parent.name.removeprefix('schubert-nk-'):Path(p) for p in graph['treePins']}
    observed=[];symbols=defaultdict(set)
    for stored in json.loads(class_raw):
        byte=(directories[stored['module']]/stored['entry']).read_bytes();assert sha(byte)==stored['sha256']
        actual=parser.read(byte)
        assert actual['className']==stored['className'] and actual['sourceFile']==stored['sourceFile']
        assert actual['references']==stored['references'] and actual['reflectiveOrDynamicLookup']==stored['reflectiveOrDynamicLookup']
        path='src/schubert-nk-'+stored['module']+'/src/test/java/'+actual['className'].rpartition('/')[0]+'/'+actual['sourceFile']
        assert path==stored['path'];symbols[actual['className']].add(path);observed.append(dict(path=path,**actual))
    assert len(observed)==1910
    prior_raw=(BASE/'PG9522-api-web42-source-join-v1/manifest.json').read_bytes()
    assert sha(prior_raw)==subject['priorManifestSha256']=='4f85bf805c3e32dbe668e6374bf6a70cb6fa6c0d93edd1ef4ea99bc30925f927'
    prior=json.loads(prior_raw);assert prior['actualExit']==0 and prior['source']==SOURCE
    owners={x['path']:(x['canonicalOwner'],x['canonicalCostOwner']) for x in prior['sourceRows']}
    for x in json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']:
        owners[x['path']]=(x['owner'],x['costOwner'])
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes()
    assert sha(normal_raw)==subject['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(normal_raw)['begin']['inputHashes'];expected=[]
    for row in rows:
        path=row['path'];primary,names=oracle[path];original=originals[path]
        assert original['mainOwners']==[] and path not in owners
        declared={x['className'] for x in observed if x['path']==path}
        assert declared and all(symbols[s]=={path} for s in declared)
        consumers={x['path'] for x in observed if x['path']!=path and declared.intersection(x['references'])}
        assert consumers and {Path(p).stem for p in consumers}==names
        assert all(p.split('/')[1]==path.split('/')[1] and owners.get(p)==(primary,primary) for p in consumers)
        witnesses=[]
        for p in sorted(consumers):
            assert sha((ROOT/p).read_bytes())==hashes[p];witnesses.append(dict(path=p,sha256=hashes[p],owner=primary))
        assert sha((ROOT/path).read_bytes())==hashes[path]
        expected.append(dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,relatedOwners=[],
          originalReferenceOwners=[],reviewedConsumerWitnesses=witnesses,fixtureClassSymbols=sorted(declared),
          witnessScope='ALL_DIRECT_SYMBOL_CONSUMERS_HAVE_ONE_REGISTERED_OWNER_NOT_DUT_OR_RUNTIME_ACCEPTANCE',
          unresolvedRuntimeReasons=original['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='EXACT_SINGLE_CANONICAL_CONSUMER_FIXTURE_RESPONSIBILITY_1932_NOT_MAIN_CP_OR_PT'))
    validate(rows,expected);rejected=[]
    for label,edit in (('cost-only',lambda v:v[0].update(costOwner='WBS-G13.07')),
      ('consumer-missing',lambda v:v[0]['reviewedConsumerWitnesses'].pop()),
      ('consumer-owner-forged',lambda v:v[0]['reviewedConsumerWitnesses'][0].update(owner='WBS-G13.07')),
      ('consumer-other-module',lambda v:v[0]['reviewedConsumerWitnesses'][0].update(path=v[0]['reviewedConsumerWitnesses'][0]['path'].replace('schubert-nk-api','schubert-nk-web'))),
      ('fixture-byte-forged',lambda v:v[0].update(sha256='0'*64)),
      ('main-reference-invented',lambda v:v[0].update(originalReferenceOwners=['WBS-G13.07'])),
      ('runtime-invented',lambda v:v[0].update(targetRuntimeAccepted=True)),
      ('symbol-forged',lambda v:v[0].update(fixtureClassSymbols=['p/Forged'])),
      ('runtime-reason-forged',lambda v:v[0].update(unresolvedRuntimeReasons=[])),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0])))):
        changed=copy.deepcopy(rows);edit(changed);assert changed!=rows
        if label=='cost-only':assert {k for k in changed[0] if changed[0][k]!=rows[0][k]}=={'costOwner'}
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged fixture responsibility accepted')
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as f:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          subjectManifestSha256=sha(raw),specSha256=sha(spec),catalogSha256=sha(catalog),primaryKeyKind='FULL_REPO_PATH',
          literalPrimaryOwners={p:x[0] for p,x in oracle.items()},independentlyParsedClassFiles=len(observed),
          sourceResponsibilitiesVerified=5,consumerSources=7,allDirectConsumerOwnersIdentical=True,notMainCpDerived=True,
          positiveBeforeNegatives=True,metadataCounterexamples=rejected,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False),f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(dict(actualExit=0,fixtures=5,parsedClassFiles=1910,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
