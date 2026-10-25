"""Literal owner/cost oracle plus positive-shaped metadata guards, never product execution."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import trace_owner_join_explicit_main_gaps as resolver
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9313-g13-four-main-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
SUBJECT=BASE/'PG9312-g13-four-main-join-v1/manifest.json'
SUBJECT_SHA='7fd038ec63dbf02d5f7b2d2c8b71d651a08da16b19d1bbbe518429ebe569b6b4'
# Expected values copied from the frozen responsibility decision, not resolver.DECISIONS.
GOLDEN={
  'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSession.java':'WBS-P018-03',
  'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/SystemManagerObservation.java':'WBS-P018-03',
  'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/FailedJmsIsolationException.java':'WBS-P005-03',
  'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/UnconfirmedJmsRollbackException.java':'WBS-P005-03'}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists() and sha(SUBJECT.read_bytes())==SUBJECT_SHA
    value=json.loads(SUBJECT.read_bytes()); assert value['source']==SOURCE and value['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    normal=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    prior=BASE/'PG9288-api-pure-readiness-trace-v1/manifest.json'
    assert sha(normal.read_bytes())==value['witnesses']['normal'][1]
    assert sha(prior.read_bytes())==value['witnesses']['prior'][1]
    hashes=json.loads(normal.read_bytes())['begin']['inputHashes']; old=json.loads(prior.read_bytes())['sourceRows']
    rows=value['sourceRows']; originals=value['originalInputs']; assert len(rows)==len(originals)==260
    resolver.validate(rows,originals,logical,hashes,'WBS-G13.07')
    assert {row['path'] for row in rows[256:]}==set(GOLDEN)
    for row in rows[256:]:
        assert row['canonicalOwner']==row['canonicalCostOwner']==GOLDEN[row['path']]
        assert row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
        assert sha((ROOT/row['path']).read_bytes())==hashes[row['path']]==row['sha256']
    for old_row,new_row in zip(old,rows):
        assert all(old_row[field]==new_row[field] for field in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    # The validator is first exercised with the actual canonical shape. Each negative is isolated.
    rejected=[]
    for name,mutate in (
      ('single-cost-field-forged',lambda v:v[256].update(canonicalCostOwner='WBS-G13.07')),
      ('single-owner-field-forged',lambda v:v[256].update(canonicalOwner='WBS-G13.07')),
      ('missing-row',lambda v:v.pop()),
      ('duplicate-row',lambda v:v.append(copy.deepcopy(v[0]))),
      ('candidate-falsely-accepted',lambda v:v[256].update(ownershipStatus='ACCEPTED')),
      ('source-hash-forged',lambda v:v[256].update(sha256='0'*64))):
        changed=copy.deepcopy(rows); mutate(changed)
        if name=='single-cost-field-forged':
            assert {key for key in rows[256] if rows[256][key]!=changed[256][key]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,originals,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(name)
        else:raise AssertionError('forged current canonical mapping accepted')
    for path in GOLDEN:
        neighbour=path.removesuffix('.java')+'Foreign.java'
        unknown=resolver.canonical(neighbour,logical)
        assert unknown['ownershipStatus']=='UNKNOWN' and unknown['canonicalOwner'] is unknown['canonicalCostOwner'] is None
        rejected.append('unregistered-neighbour:'+Path(path).name)
    # Baseline precedence is checked on a RAM-only logical fixture, not by editing the real inventory.
    path=next(iter(GOLDEN)); fixture={**logical,path:dict(path=path,owner='WBS-P018-08',costOwner='WBS-P018-08')}
    resolved=resolver.canonical(path,fixture)
    assert resolved['canonicalOwner']==resolved['canonicalCostOwner']=='WBS-P018-08'
    assert resolved['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE'
    assert value['javaPathDenominator']==1789 and value['explicitRegistered']==1085
    assert value['remainingUnregisteredMain']==0 and value['remainingUnregisteredTests']==704
    assert value['productTestsExecuted']==value['newTestIds']==value['newMain']==value['newAccepted']==0
    assert value['coverage'] is value['effortPercent'] is None
    assert value['wholeG13Accepted'] is value['whole451Accepted'] is value['formalUpdated'] is False
    verify(invocation); OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          joinManifestSha256=SUBJECT_SHA,literalGoldenOwners=GOLDEN,previous256CanonicalMappingPreserved=True,
          metadataCounterexamples=rejected,positiveCanonicalShapeValidatedFirst=True,costOnlyChangedField='canonicalCostOwner',
          originalBaselinePrecedenceFixture=True,registeredMain=965,totalMain=965,registeredTest=120,totalTest=824,
          methodRequirementTraceComplete=False,productTestsExecuted=0,coverage=None,newAccepted=0,wholeG13Accepted=False,
          whole451Accepted=False,formalUpdated=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,golden=4,metadataCounterexamples=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
