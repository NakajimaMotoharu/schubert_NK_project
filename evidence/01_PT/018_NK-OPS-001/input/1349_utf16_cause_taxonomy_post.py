"""Metadata-only source disposition invariants, preserving global owner/HOLD distinctions."""
from pathlib import Path
import copy,hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26824-utf16-cause-taxonomy-independent-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();p=B/'evidence/PG26820-web-principal-global-owner-supplement-v1/manifest.json';m=load(p);rows=load(R/m['updatedProjection']['path']);assert sha(R/m['updatedProjection']['path'])==m['updatedProjection']['sha256']
disposed={3,16,18,20,21,22};closed={4,5,13,33};pending=set(range(35))-disposed-closed
def check(values):
    if len(values)!=35 or {r['index'] for r in values}!=set(range(35)):
        raise ValueError('missing or duplicate source')
    for r in values:
        i=r['index']
        expected='LOCAL_CORRECTED_OR_SOURCE_NONAPPLICABLE_FOR_THIS_CAUSE' if i in disposed else ('CLOSED_BY_INDEPENDENT_OWNER_PROOF' if i in closed else 'PENDING_CALL_CONTRACT_OR_NORMAL_PROOF')
        if r['utf16CauseDisposition']!=expected or r['pendingForUtf16Cause']!=(i in pending):
            raise ValueError('unknown or inconsistent cause disposition')
        if r['globalYktTargetClosed']!=(i in closed):
            raise ValueError('changed legacy owner flags')
    return True
assert check(rows) and len(pending)==25 and sum(not r['globalYktTargetClosed'] for r in rows)==31
negatives=[]
for name,values in [('missing',rows[:-1]),('duplicate',rows[:-1]+[rows[0]])]:
    try:check(values)
    except ValueError:negatives.append(name)
    else:raise AssertionError(name)
bad=copy.deepcopy(rows);bad[0]['utf16CauseDisposition']='UNKNOWN'
try:check(bad)
except ValueError:negatives.append('unknown')
else:raise AssertionError('unknown')
assert len(negatives)==3
post=R/m['normalEvidence']['path'];n=load(post);assert sha(post)==m['normalEvidence']['sha256'] and n['actualExit']==0 and n['tests']==166 and n['fullClosureFour100'];assert n['newTestDefinitions']==4
v=dict(actualExit=0,producer=ref(p),normalProof=ref(post),allSources=35,pendingForThisCause=25,localCorrectedOrCauseNonapplicable=6,independentOwnerProofClosed=4,globalOwnerFlagFalse=31,metadataPositiveChecks=['all35_identity','exact_three_disjoint_sets','normal166_four100'],metadataNegativeChecks=negatives,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,globalClosed=False,verifier=ref(Path(__file__).resolve()));O.mkdir();(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,source35Pending25=True,metadataNegative3=True,manifestSha256=sha(O/'manifest.json'))))
