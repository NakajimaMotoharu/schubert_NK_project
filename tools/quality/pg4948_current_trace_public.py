"""Allowlisted trace receipt and current per-Java-owner counters, never acceptance credit."""
import collections
import json
import os
import pg4946_current_physical_trace as update
from pg3282_wbs_current_source_apply import group_coverage

PUBLIC=update.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4946-current-physical-trace-v1'
COUNTERS=update.trace.COUNTERS
require=update.require
sha=update.sha


def owner_measurement(artifacts,data):
    owners={};seen=set();declared=set()
    for artifact in artifacts:
        if artifact['kind']!='JAVA':continue
        identity=(artifact['module'],artifact['class'])
        require(identity not in seen,'one Java family one owner');seen.add(identity)
        counts=data.get(identity[0],{}).get(identity[1])
        row=owners.setdefault(artifact['owner'],{'families':0,'declarationOnlyFamilies':0,'unmeasuredFamilies':[],
            'missed':{k:0 for k in COUNTERS},'covered':{k:0 for k in COUNTERS}})
        row['families']+=1
        if counts is None:
            require(identity[0]=='characterization'and artifact['owner']=='WBS-P020-01'
                    and artifact.get('path','').startswith('program/characterization/src/main/java/'),
                    'no missing current Production Java family')
            # These four retained compatibility-tool classes are outside the six
            # Production module XML. Keep them unmeasured, never infer zero/pass.
            row['unmeasuredFamilies'].append(identity[1]);continue
        require(set(counts)==set(COUNTERS)and all(len(v)==2 and all(type(n)is int and n>=0 for n in v)for v in counts.values()),'complete current owner family counters')
        if all(sum(v)==0 for v in counts.values()):row['declarationOnlyFamilies']+=1;declared.add(identity)
        for k in COUNTERS:row['missed'][k]+=counts[k][0];row['covered'][k]+=counts[k][1]
    missing=[]
    for module,families in data.items():
        for name,counts in families.items():
            if (module,name)not in seen and any(counts[k][0]for k in COUNTERS):missing.append((module,name))
    require(not missing,'no unmapped missed executable families')
    remaining={k:sum(r['missed'][k]for r in owners.values())for k in COUNTERS}
    for row in owners.values():
        if row['unmeasuredFamilies']:
            row['status']='SEPARATE_CHARACTERIZATION_EVIDENCE_REQUIRED'
            row['measuredPartialMissed']=row['missed'];row['measuredPartialCovered']=row['covered']
            row['missed']=row['covered']=None
        else:row['status']='TECHNICAL_COUNTERS_CLOSED'if not any(row['missed'].values())else'TECHNICAL_GAPS'
        row['accepted']=False
    return {'javaOwners':len(owners),'javaFamilies':len(seen),'zeroCounterFamilies':len(declared),
            'counts':dict(collections.Counter(r['status']for r in owners.values())),
            'remaining':remaining,'remainingScope':'SIX_PRODUCTION_MODULES_ONLY',
            'rows':owners,'acceptedLeafDelta':0,'effortPercent':None}


def main():
    record=json.loads((update.OUT/'stage.safe.json').read_bytes());applied=json.loads((update.OUT/'apply.safe.json').read_bytes())
    require(type(record['actualExit'])is int and record['actualExit']==0 and type(applied['actualExit'])is int and applied['actualExit']==0,'actual original staged/application0')
    for n in update.NAMES:require(sha((update.PMO/n).read_bytes())==record['after'][n],'applied metadata hash stable')
    require(all(record['before'][n]==record['after'][n]for n in update.NAMES[:2]),'master/acceptance/budget bytes unchanged')
    inventory=update.audit.read_json(update.PMO/update.NAMES[2]);candidate=inventory['currentPhysicalCandidate']
    observed=update.trace.verify_candidate(inventory)
    require(observed==applied['audit']['currentPhysicalCandidate'],'same strict applied current observation')
    proof=update.audit.read_json(update.ROOT/update.PUBLIC);owners=owner_measurement(candidate['artifacts'],group_coverage(proof))
    require(owners['remaining']==observed['remaining'],'all current missed counters assigned once')
    old={a['path']:a for a in inventory['artifacts']}
    changed=sum(a['historicalPath']==a['path']and a['sha256']!=old[a['historicalPath']]['sha256']for a in candidate['artifacts'])
    value={'actualExit':0,'productionSource':update.SOURCE,'canonicalAcceptanceSource':inventory['source'],
           'kind':'CURRENT_PHYSICAL_TRACE_NOT_ACCEPTANCE','historicalArtifacts':len(old),'currentArtifacts':len(candidate['artifacts']),
           'samePathHashChanges':changed,'approvedRelocations':len(update.trace.MOVES),
           'beforeFileHashes':record['before'],'afterFileHashes':record['after'],
           'stageReceiptSha256':sha((update.OUT/'stage.safe.json').read_bytes()),'applyReceiptSha256':sha((update.OUT/'apply.safe.json').read_bytes()),
           'measurementManifest':update.PUBLIC,'measurementManifestSha256':update.PROOF,
           'currentMeasurement':observed,'currentJavaOwnerCounters':owners,'historicalAcceptedTasks':17,
           'acceptedLeafDelta':0,'formalAccepted':False,'effortPercent':None,'vmOperations':0,'productionChanges':0}
    os.umask(0o077);PUBLIC.mkdir(mode=0o755)
    path=PUBLIC/'manifest.json'
    with path.open('x')as f:json.dump(value,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'manifest':str(path.relative_to(update.ROOT)),'sha256':sha(path.read_bytes()),'javaOwners':owners['javaOwners'],'currentCounterCounts':owners['counts'],'acceptedLeafDelta':0}));return 0


if __name__=='__main__':raise SystemExit(main())
