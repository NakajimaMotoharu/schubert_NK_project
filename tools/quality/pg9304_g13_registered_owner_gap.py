"""Enumerate current Java paths against explicit registry rows; unknown is not assigned."""
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9304-g13-registered-owner-gap-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
NORMAL=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
NORMAL_SHA='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
PRIOR=BASE/'PG9288-api-pure-readiness-trace-v1/manifest.json'
PRIOR_SHA='6a721ba74684d07681c61ba56593796363063f6e6eaa313cf62749dc94a2f7a6'
LOGICAL_SHA='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
HISTORICAL_SHA='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
PATTERN=re.compile(r'src/schubert-nk-(protocol|storage|bootstrap|api|web|batch)/src/(main|test)/java/.+\.java')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def dataset(value):return sha(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    assert sha(NORMAL.read_bytes())==NORMAL_SHA and sha(PRIOR.read_bytes())==PRIOR_SHA
    normal=json.loads(NORMAL.read_bytes()); prior=json.loads(PRIOR.read_bytes())
    assert normal['source']==prior['source']==SOURCE and normal['actualExit']==prior['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert dataset(inventory['artifacts'])==LOGICAL_SHA and dataset(inventory['currentPhysicalCandidate'])==HISTORICAL_SHA
    logical={row['path']:row for row in inventory['artifacts']}
    explicit={row['path']:row for row in prior['sourceRows']}
    assert len(logical)==941 and len(explicit)==len(prior['sourceRows'])==256
    hashes=normal['begin']['inputHashes']
    snapshot=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'
    rows=[]
    for path in sorted(hashes):
        match=PATTERN.fullmatch(path)
        if not match:continue
        assert sha((ROOT/path).read_bytes())==sha((snapshot/path).read_bytes())==hashes[path]
        if path in logical:
            reference=logical[path]; owner,cost=reference['owner'],reference['costOwner']
            kind='BASELINE_LOGICAL_REFERENCE'
            if path in explicit:
                assert owner==explicit[path]['canonicalOwner'] and cost==explicit[path]['canonicalCostOwner']
        elif path in explicit:
            reference=explicit[path]; assert reference['sha256']==hashes[path]
            owner,cost=reference['canonicalOwner'],reference['canonicalCostOwner']
            kind='CURRENT_EXPLICIT_REVIEWED_CANDIDATE_NOT_ACCEPTED'
        else:owner=cost=None; kind='UNKNOWN_NO_EXPLICIT_REGISTRY_ROW'
        if kind!='UNKNOWN_NO_EXPLICIT_REGISTRY_ROW':assert owner and cost
        rows.append(dict(path=path,sha256=hashes[path],module=match[1],sourceSet=match[2],
          registryStatus=kind,canonicalOwner=owner,canonicalCostOwner=cost))
    assert rows and len(rows)==len({row['path'] for row in rows})
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    counts=Counter(row['registryStatus'] for row in rows)
    by_module={}
    for row in rows:
        key=row['module']+':'+row['sourceSet']; group=by_module.setdefault(key,dict(total=0,registered=0,unregistered=0))
        group['total']+=1; group['unregistered' if row['canonicalOwner'] is None else 'registered']+=1
    verify(invocation); OUT.mkdir()
    result=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      normalManifestSha256=NORMAL_SHA,prior256ManifestSha256=PRIOR_SHA,
      original941DatasetSha256=LOGICAL_SHA,historical943DatasetSha256=HISTORICAL_SHA,
      javaPathCount=len(rows),registryCounts=dict(counts),byModuleAndSourceSet=by_module,sourceRows=rows,
      currentAndSnapshotHashesVerified=True,scope='SIX_MODULE_MAIN_TEST_JAVA_PATH_EXPLICIT_REGISTRY_COVERAGE_ONLY',
      unknownMeaning='NO_ORIGINAL_LOGICAL_OR_CURRENT256_EXPLICIT_ROW; NOT_A_PROOF_THAT_NO_POTENTIAL_RULE_EXISTS',
      physical1843MainAreDifferentUnit=True,methodAndRequirementTraceComplete=False,wholeG13Accepted=False,
      productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,whole451Accepted=False,formalUpdated=False,newAccepted=0,
      effortPercent=None,costReallocated=False,actualAllocatedPp=None,actualVmActions=0,actualDatabaseActions=0)
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,javaPaths=len(rows),counts=dict(counts),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
