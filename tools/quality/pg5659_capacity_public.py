"""Allowlisted same-current online-capacity recovery results, no raw data or keys."""
import hashlib
import json
import os
from pg5656_capacity_current_post import current,BEFORE,AFTER,GROW
from pg5590_current_static_projection import ROOT


def main():
    w=current.post.role.W
    paths={'preflight':'pg5654-capacity-preflight-v2/manifest.safe.json','before':BEFORE+'/manifest.safe.json',
      'grow':GROW+'/manifest.safe.json','after':AFTER+'/manifest.safe.json','originalCapacityRefusal':'pg5632-new-current-readonly-v1/manifest.safe.json'}
    raw={k:(w/p).read_bytes()for k,p in paths.items()};v={k:json.loads(r)for k,r in raw.items()}
    if not(all(type(v[k]['actualExit'])is int and v[k]['actualExit']==0 for k in('preflight','before','grow','after'))
      and type(v['originalCapacityRefusal']['actualExit'])is int and v['originalCapacityRefusal']['actualExit']==1
      and v['preflight']['layers']==4 and v['preflight']['hostReadRecoveredNotReplayed']is True
      and v['grow']['guest']['sameBoot']is True and v['grow']['guest']['nonRootPartitionsUnchanged']is True
      and v['after']['result']['guestFreeBytes']>=12884901888 and v['after']['result']['productionSource']==current.SOURCE
      and v['after']['result']['full11AfterSha256']==current.context()and v['after']['result']['native94Preserved']is True
      and v['after']['result']['newRootNotStarted']is True):raise ValueError('all genuine capacity/full11 post predicates')
    value={'actualExit':0,'source':current.SOURCE,'BOM':current.BOM,'preflight':v['preflight'],'grow':v['grow'],
      'before':v['before'],'after':v['after'],'originalCapacityRefusal':v['originalCapacityRefusal'],
      'originalReceiptRefs':{k:{'path':paths[k],'sha256':hashlib.sha256(r).hexdigest()}for k,r in raw.items()},
      'BUG':['BUG-1467','BUG-1468'],'YKT':['YKT-1230','YKT-1231'],'dataDeletionOrReboot':False,
      'oldNativeImported':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5659-current-capacity-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
