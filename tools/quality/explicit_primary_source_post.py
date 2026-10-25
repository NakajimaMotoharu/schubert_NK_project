"""Frozen Markdown primary table and full related/runtime metadata, independent of resolver code."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validate(rows,expected):
    if rows!=expected:raise ValueError('frozen fullpath primary/related/runtime source metadata required')

def run(library,out,subject_name,subject_sha,catalog_sha,spec_path,spec_sha,source_prefix,line_prefixes,expected_count,main_subjects,source_path_mutator=None,source_mutator_vectors=0):
    invocation=capture(library);assert not out.exists();subject=BASE/subject_name
    spec_raw=(ROOT/spec_path).read_bytes();assert sha(spec_raw)==spec_sha
    oracle={}
    for line in spec_raw.decode().splitlines():
        if not line.startswith(tuple('|'+prefix for prefix in line_prefixes)):continue
        _,relative,primary,_,_=line.split('|');path=source_prefix+relative
        assert path not in oracle;oracle[path]=primary
    assert len(oracle)==expected_count
    raw=(subject/'manifest.json').read_bytes();assert sha(raw)==subject_sha
    value=json.loads(raw);assert value['source']==SOURCE and value['actualExit']==0 and value['frozenPrimaryOwners']==oracle
    catalog=(subject/'candidates.json').read_bytes();assert sha(catalog)==value['candidatesSha256']==catalog_sha
    rows=json.loads(catalog);assert len(rows)==expected_count and {row['path'] for row in rows}==set(oracle)
    graph_raw=(BASE/'PG9386-composite-reference-graph-v3/manifest.json').read_bytes();assert sha(graph_raw)==value['graphManifestSha256']=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(graph_raw);reference_raw=(BASE/'PG9386-composite-reference-graph-v3/unresolved.json').read_bytes();assert sha(reference_raw)==graph['unresolvedSha256']
    original={row['path']:row for row in json.loads(reference_raw)}
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes();assert sha(normal_raw)==value['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(normal_raw)['begin']['inputHashes'];expected=[]
    for row in rows:
        path=row['path'];primary=oracle[path];before=original[path]
        assert primary in before['mainOwners'] and sha((ROOT/path).read_bytes())==hashes[path]==before['sha256']
        expected.append(dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,
          relatedOwners=sorted(set(before['mainOwners'])-{primary}),originalReferenceOwners=before['mainOwners'],
          unresolvedRuntimeReasons=before['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='FROZEN_LITERAL_SOURCE_PRIMARY_AND_RELATED_SCOPES_RUNTIME_UNCERTAINTY_RETAINED_NOT_PT'))
    validate(rows,expected)
    main_raw=(subject/'main-source-proofs.json').read_bytes();class_raw=(subject/'class-proofs.json').read_bytes()
    assert sha(main_raw)==value['mainProofsSha256'] and sha(class_raw)==value['classProofsSha256']
    mains=json.loads(main_raw);classes=json.loads(class_raw)
    assert len(mains)==value['independentMainClassDeclarations'] and len({item['path'] for item in mains.values()})==value['independentUniqueMainSourceFiles']
    assert len(classes)==value['independentClassMetadata']
    logical={row['path']:row for row in json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for name,primary in main_subjects.items():
        matches=[item for key,item in mains.items() if key.rsplit('/',1)[-1]==name]
        assert len(matches)==1;item=matches[0]
        assert item['owner']==logical[item['path']]['owner']==logical[item['path']]['costOwner']==primary
        assert item['sha256']==hashes[item['path']]==sha((ROOT/item['path']).read_bytes())
    for item in classes.values():
        assert sha((ROOT/item['path']).read_bytes())==hashes[item['path']]
    rejected=[]
    mutate_source=source_path_mutator or (lambda path:path.replace('schubert-nk-api','schubert-nk-web'))
    for label,edit in (('cost-only',lambda v:v[0].update(costOwner='WBS-G13.07')),('primary-forged',lambda v:v[0].update(owner='WBS-F01')),
      ('related-forged',lambda v:v[0].update(relatedOwners=['FORGED'])),('runtime-reason-forged',lambda v:v[0].update(unresolvedRuntimeReasons=['FORGED'])),
      ('runtime-success-invented',lambda v:v[0].update(targetRuntimeAccepted=True)),('source-byte-forged',lambda v:v[0].update(sha256='0'*64)),
      ('source-other-module',lambda v:v[0].update(path=mutate_source(v[0]['path']))),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0])))):
        changed=copy.deepcopy(rows);edit(changed);assert changed!=rows
        if label=='cost-only':assert {k for k in rows[0] if rows[0][k]!=changed[0][k]}=={'costOwner'}
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged source responsibility accepted')
    verify(invocation);out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          subjectManifestSha256=sha(raw),specSha256=spec_sha,catalogSha256=sha(catalog),primaryKeyKind='FULL_REPO_PATH',literalPrimaryOwners=oracle,
          sourceResponsibilitiesVerified=expected_count,relatedOwnersAndRuntimeReasonsPreserved=True,mainSubjects=main_subjects,
          independentTestClassDeclarations=len(classes),independentMainClassDeclarations=len(mains),independentUniqueMainSourceFiles=len({item['path'] for item in mains.values()}),
          sourceOtherModuleMutationVectors=source_mutator_vectors,positiveBeforeNegatives=True,metadataCounterexamples=rejected,productTestsExecuted=0,newAccepted=0,coverage=None,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,literalSourceResponsibilities=expected_count,metadataNegatives=len(rejected),manifestSha256=sha((out/'manifest.json').read_bytes()))))
