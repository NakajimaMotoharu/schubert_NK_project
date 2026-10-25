"""Bind static reference catalog to current source/Main responsibility without PT claims."""
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import trace_owner_join_static_companion as owner
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9364-static-companion-owner-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    pins={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'prior':('PG9348-direct-companion-owner-join-v1/manifest.json','fa2817d4f7b37d4d5cf2325edb2e1dd8b0763276fe0477805147606e86660f20'),
      'staticCompile':('PG9358-static-companion-compile55-v1/manifest.json','1e6283063e08ae26c4abe5b9cd2d4eb4fce69a45365c4aae14b996641f61d751'),
      'javap':('PG9360-static-companion-javap-v1/manifest.json','a6cc01273a2d12b966524fdf7366ec90f9650d4826b5fcffc944cb1e115a65b6'),
      'asm':('PG9362-static-companion-asm-v1/manifest.json','5a98abbe4cf6ddbaf7259b72c6b68996e46f5feaeaaba51455756f5d1d53ff37')}
    proof={}
    for key,(path,digest) in pins.items():
        assert sha((BASE/path).read_bytes())==digest;proof[key]=json.loads((BASE/path).read_bytes())
        assert proof[key]['source']==SOURCE and proof[key]['actualExit']==0
    assert proof['asm']['confirmedCandidates']==55 and proof['asm']['unconfirmedCandidates']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']};old=proof['prior']['sourceRows'];known={row['path']:row for row in old}
    assert len(old)==569;hashes=proof['normal']['begin']['inputHashes']
    originals=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    for path,item in sorted(owner.DECISIONS.items()):
        assert path not in logical and path not in known and path.endswith('Test.java')
        main=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        assert main==item['mainPath'] and item['owner']==item['costOwner']
        expected=(logical[main]['owner'],logical[main]['costOwner']) if main in logical else (known[main]['canonicalOwner'],known[main]['canonicalCostOwner'])
        assert expected==(item['owner'],item['costOwner'])
        assert sha((ROOT/path).read_bytes())==hashes[path]==item['sha256']
        assert sha((ROOT/main).read_bytes())==hashes[main]==item['mainSha256']
        originals.append(dict(path=path,sha256=hashes[path],owner=None))
    joined=owner.join_rows(originals,logical,hashes,'WBS-G13.07');owner.validate(joined,originals,logical,hashes,'WBS-G13.07')
    for before,after in zip(old,joined):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    assert len(joined)==len({row['path'] for row in joined})==624
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          witnesses=pins,catalogSha256=owner.CATALOG_SHA,sourceRows=joined,originalInputs=originals,previous569CanonicalPreserved=True,
          newExactTestSourceCandidates=55,sourceCount=624,newOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined[569:])),
          javaPaths=1789,registered=1449,registeredMain=965,totalMain=965,registeredTest=484,totalTest=824,unregisteredTest=340,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,
          wholeG13Accepted=False,whole451Accepted=False,wholeWbsAudit='HOLD_CURRENT_SOURCE_NOT_WHOLE_QUALIFIED',
          costReallocated=False,actualAllocatedPp=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,newCandidates=55,registered=1449,unregistered=340,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
