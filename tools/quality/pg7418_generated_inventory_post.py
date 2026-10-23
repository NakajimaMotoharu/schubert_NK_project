"""Independent bounded inventory accounting/source-domain review; no generated contract accepted by enumeration."""
import copy
import datetime
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7418-generated-inventory-post-v1'
PINS={
 'inventory':('PG7416-generated-value-inventory-v1/manifest.json','92f7329fa38699d44f0c913a49b7d71e4521318f5e7e6d74a2a655a7e492149b'),
 'physical':('PG7408-api-generated-contract-six-post-v1/manifest.json','2c4db84ee9a0c354aca88ef4dd03220d8b6ea9cd8eb8b80e44e2b39b9877924b'),
 'generated':('PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')}

def require(value,message):
    if not value:raise ValueError(message)

def validate(rows,physical,known):
    require(len(rows)==500 and len({(r['role'],r['className']) for r in rows})==500,'exact unique whole generated candidates')
    counts={};verified=0;records=0;enums=0
    domains={'api':physical['currentApi'],'batch':physical['historicalBatch'],'web':physical['historicalWeb']}
    for row in rows:
        role=row['role'];name=row['className'];known_key=role=='api' and name in known
        require(row['currentSourceExecutionAccepted'] is known_key and row['metadataEnumerationOnly'] is (not known_key),
          'only actual source-specific known contracts, not namespace or inherited PASS')
        require(row['formalAccepted'] is False and row['effortPercent'] is None,'no phase acceptance/effort inference')
        if known_key:
            require(row['sha256']==known[name]['sha256'] and row['contractStatus']=='CURRENT_SOURCE_API_CONTRACT_VERIFIED'
              and row['contractWitness']['source']==physical['source'],'actual qualified API type/source/hash only')
            verified+=1
        else:
            require(row['contractStatus']=='PENDING_EVIDENCE_AND_SAFETY_REVIEW_NOT_EXECUTION_AUTHORIZED'
              and 'contractWitness' not in row,'unmatched is pending, not untested/failed or execution permission')
        if '/monitoring/' in name and role in domains:
            require(domains[role]['physicalClasses'][role+':'+name+'.class']==row['sha256'],
              'monitoring candidate exact current or historical bytes only, never role alias')
        require(row['kind'] in ('RECORD','ENUM'),'actual record/enum only')
        records+=row['kind']=='RECORD';enums+=row['kind']=='ENUM'
        counts[role]=counts.get(role,0)+1
        if row['kind']=='ENUM':
            require(sum(m['shape']=='ENUM_VALUES_FACTORY' for m in row['methods'])==1
              and sum(m['shape']=='ENUM_VALUEOF_FACTORY' for m in row['methods'])==1,'all actual enum factory inventories, no subtype aliases')
    require((records,enums,verified)==(356,144,6),'actual whole candidate counts/known source contracts, no progression arithmetic')
    require(counts=={'api':146,'batch':138,'bootstrap':31,'protocol':126,'storage':11,'web':48},'all six exact role inventories')
    return dict(record=records,enum=enums,independentlyVerified=verified,pending=500-verified)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only independent inventory post')
    proofs={}
    for key,(path,sha) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==sha,'exact immutable original proof');proofs[key]=json.loads(file.read_bytes())
    inventory=proofs['inventory'];physical=proofs['physical'];generated=proofs['generated']
    require(inventory['source']==physical['source']==generated['source']=='fcedc05b1b61b74b6b8a3fe3d9e5ea8d19859650'
      and inventory['actualExit']==0 and inventory['physicalClassCount']==1738
      and all(r['actualExit']==0 for r in inventory['receipts']),'actual original metadata steps/1738/source, not begin-only')
    require(host.sha(host.ROOT/'tools/quality/architecture/GeneratedValueInventory.java')==inventory['sourceToolSha256']
      and host.sha(host.ROOT/'tools/quality/architecture/GeneratedValueInventoryProbe.java')==inventory['probeToolSha256'],
      'original actual helper/probe source unchanged')
    require(inventory['targetJarsOnHelperClasspath'] is False and inventory['targetClassInitialized'] is False
      and inventory['productionTestsExecuted']==0 and inventory['newContractAcceptanceFromEnumeration']==0
      and inventory['expansionClosed'] is False,'metadata is not PT/safety permission/expansion closure')
    known={r['className']:r for r in generated['generatedTypes']};rows=inventory['generatedTypes']
    totals=validate(rows,physical,known);guards=[]
    for kind in ('historical-accepted','unknown-witness','known-type-byte','namespace-alias','pending-marked-failed'):
        changed=copy.deepcopy(rows)
        unknown=next(r for r in changed if r['role']=='batch' and '/monitoring/' in r['className'])
        actual=next(r for r in changed if r['currentSourceExecutionAccepted'])
        if kind=='historical-accepted':unknown['currentSourceExecutionAccepted']=True
        elif kind=='unknown-witness':unknown['contractWitness']={'source':physical['source']}
        elif kind=='known-type-byte':actual['sha256']='0'*64
        elif kind=='namespace-alias':unknown['role']='api'
        else:unknown['contractStatus']='UNTESTED_FAILED'
        try:validate(changed,physical,known)
        except (ValueError,KeyError):guards.append(dict(kind=kind,rejected=True))
        else:raise ValueError('unjustified source/acceptance/status mutation accepted')
    selected={role:[r for r in rows if r['role']==role and '/monitoring/' in r['className']]
      for role in ('batch','web')}
    require(len(selected['batch'])==19 and len(selected['web'])==5,'bounded C07 evidence/source review candidates only')
    value=dict(actualExit=0,source=inventory['source'],invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      witnesses=PINS,totals=totals,roleCounts=inventory['roleCounts'],negativeGuards=guards,
      nextEvidenceAndSafetyReview={role:[dict(className=r['className'],sha256=r['sha256'],sourcePath=r['sourcePath'],
        kind=r['kind'],status='CANDIDATE_FOR_BOUNDED_SOURCE_EVIDENCE_REVIEW_NOT_TEST_EXECUTION_AUTHORIZATION') for r in values]
        for role,values in selected.items()},
      sourceEvidenceMissingDoesNotMeanUntested=True,additionalDefectsInferred=0,
      productionTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None,expansionClosed=False,
      actualVmActions=0,actualDatabaseActions=0,targetClassInitialized=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,totals=totals,batchReviewCandidates=19,webReviewCandidates=5,
      negativeGuards=len(guards),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
