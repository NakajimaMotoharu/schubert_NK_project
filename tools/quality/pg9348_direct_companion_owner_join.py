"""Promote enumerated source responsibilities only, never execution or formal acceptance."""
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import trace_owner_join_direct_companion as owner
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9348-direct-companion-owner-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    pins={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'priorOwners':('PG9334-g13-storage-residual-join-v1/manifest.json','69df39386cdb70e792f3ab31de0c050c6c465a4d9a6b0264e17f29b9d1390ffd'),
      'primaryAst':('PG9344-direct-companion-ast-v1/manifest.json','6a8bea332ad27bccd567949395166f4cef2334bc9770063c3a7ed0d0f405c5d0'),
      'independentJdk':('PG9346-direct-companion-jdk-post-v1/manifest.json','5858a76efb999092d1dfe0471f797c61b2260482fa271908555ca186f2dd9879')}
    proof={}
    for name,(path,digest) in pins.items():
        assert sha((BASE/path).read_bytes())==digest;proof[name]=json.loads((BASE/path).read_bytes())
        assert proof[name]['source']==SOURCE and proof[name]['actualExit']==0
    assert proof['primaryAst']['proposedCandidates']==proof['independentJdk']['confirmedCandidates']==280
    assert proof['independentJdk']['unconfirmedCandidates']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']};old=proof['priorOwners']['sourceRows'];assert len(old)==289
    known={row['path']:row for row in old};hashes=proof['normal']['begin']['inputHashes']
    originals=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    for path,item in sorted(owner.DECISIONS.items()):
        assert path not in logical and path not in known and path.endswith('Test.java')
        main=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        assert item['mainPath']==main and item['owner']==item['costOwner']
        if main in logical:expected=(logical[main]['owner'],logical[main]['costOwner'])
        else:expected=(known[main]['canonicalOwner'],known[main]['canonicalCostOwner'])
        assert expected==(item['owner'],item['costOwner'])
        assert sha((ROOT/path).read_bytes())==hashes[path]==item['sha256']
        assert sha((ROOT/main).read_bytes())==hashes[main]==item['mainSha256']
        originals.append(dict(path=path,sha256=hashes[path],owner=None))
    joined=owner.join_rows(originals,logical,hashes,'WBS-G13.07');owner.validate(joined,originals,logical,hashes,'WBS-G13.07')
    for before,after in zip(old,joined):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    assert len(joined)==569 and len({row['path'] for row in joined})==569
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          witnesses=pins,catalogSha256=owner.CATALOG_SHA,sourceRows=joined,originalInputs=originals,
          previous289CanonicalPreserved=True,newExactTestSourceCandidates=280,sourceCount=569,
          newCandidateOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined[289:])),
          javaPaths=1789,registered=1394,registeredMain=965,totalMain=965,registeredTest=429,totalTest=824,
          unregisteredTest=395,productTestsExecuted=0,targetClassLoading=0,newTestIds=0,newMain=0,coverage=None,
          formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False,
          wholeWbsAudit='HOLD_CURRENT_SOURCE_NOT_WHOLE_QUALIFIED',costReallocated=False,actualAllocatedPp=None),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,newOwnerCandidates=280,registered=1394,unregistered=395,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
