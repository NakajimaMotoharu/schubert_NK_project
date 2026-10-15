"""Export only source coordinates/dispositions; raw warnings remain and F03 stays open."""
import hashlib
import json
from pathlib import Path
import shlex
from lan_server import run

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3710-pmd-first-triage-v1'


def main():
    record=json.loads((W/'pg3708-pmd-first-dispositions-v1/manifest.safe.json').read_bytes());inventory=json.loads((W/'pg3706-pmd-applicability-inventory-v1/manifest.safe.json').read_bytes())
    if not(record['actualExit']==inventory['actualExit']==0 and record['result']['unclassified']==1978):raise ValueError('actual all findings partition')
    r=record['result'];payload='EXPECTED='+repr(r['dispositionSha256'])+'\n'+r'''
from pathlib import Path
import hashlib,json
p=Path('/home/mini/schubert-nk-pgpt/runs/PG3708-pmd-disposition-v1/dispositions.private.json');raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
rows=json.loads(raw);out=[]
for row in rows:
 if row['disposition']=='UNCLASSIFIED':continue
 out.append({k:row[k]for k in ['id','path','sourceSha256','rule','coordinates','disposition','basis','testOrDesignEvidence','qualityGatePass']})
assert len(rows)==2217 and len(out)==239 and all(x['qualityGatePass']is False for x in out)
print(json.dumps(out,sort_keys=True))
'''
    rc,output=run('python3 -c '+shlex.quote(payload),timeout=30)
    if rc!=0:raise ValueError('exact coordinate export refused')
    rows=json.loads(output.strip());PUBLIC.mkdir();path=PUBLIC/'dispositions239.json'
    with path.open('x')as f:json.dump(rows,f,sort_keys=True,indent=2);f.write('\n')
    data={k:v for k,v in r.items()if k not in {'recordedUTC'}}
    data.update(actualExit=0,inventoryManifestSha256=inventory['result']['serverManifestSha256'],originalIndexSha256=inventory['result']['findingsSha256'],primaryVendorRulesSha256=inventory['result']['vendorRulesSha256'],vendorDeprecatedAlias=inventory['result']['resolvedDeprecatedAliases'],findingDispositionPublicSha256=hashlib.sha256(path.read_bytes()).hexdigest(),architectureProofLogicalSlot='PG379/pg3708-pmd-first-dispositions-v1/architecture.safe.json',architectureScope='Approved origin/main SS311 executable/library jars and SS342 direct Java process; unchanged dependencies/deployment; no JavaEE platform or managed descriptors. NOT new source runtime/native qualification.',classificationMeaning='239 source-bound technical dispositions, not removal of raw2217, not F03 acceptance or PGPT progress percentage',newProductionPtCredit=0,individualAccepted=17,formalTests=1964,formalScopes=53,effortCompletionRate=None,QA051final='HELD')
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(data,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'classified':239,'unclassified':1978,'rawPmd':2217,'F03Accepted':False,'manifestSha256':hashlib.sha256((PUBLIC/'manifest.json').read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
