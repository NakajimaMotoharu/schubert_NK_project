"""Original RO18 stage/prepare/independent post only; no private snapshot or secret."""
import hashlib
import json
import os
from pg5616_current_ro_sources import W,CURRENT,SOURCE,BEFORE,BOM
from pg5590_current_static_projection import ROOT


def main():
    refs={'abi':('pg5618-frozen-v1.safe.json','3b2a730e45a6743a3a967bf6bcc4852bc59862ae493ed609ca60383348d512bb'),
      'stage':('pg5620-stage-v1.safe.json','98e21922a320a1fc4feb118ab68c014379eb7242daa2c1e28e3c88873338182c'),
      'prepare':('pg5620-prepare-ro-v1.safe.json','10814d14e62c5c47faaabde0d047ca2bcfd3dfd0369c0215dc19d8cbeb4e061d'),
      'post':('pg5622-current-ro-independent-post-v1/manifest.safe.json','e61c618ca4165955ff6cc01fed8125c66a9477cf1e41fc74b13c38d923247425')}
    values={}
    for key,(path,digest)in refs.items():
        raw=(W/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('actual original RO receipt, no replay')
        values[key]=json.loads(raw)
    abi,stage,prepare,post=(values[k]for k in('abi','stage','prepare','post'));r=post['result']
    if not(all(type(v['actualExit'])is int and v['actualExit']==0 for v in values.values())and r['candidateHostReadonlyVerified']
      and r['productionSource']==CURRENT and r['candidateSource']==SOURCE and r['candidateManifestSha256']==BOM
      and r['nativePhysicalFiles']==94 and r['full11BeforeSha256']==r['privateAfterSha256']==BEFORE
      and prepare['currentApprovalEpochChanged']is False and all(v['actualExit']==0 for v in abi['phases'].values())):raise ValueError('complete RO/current/candidate post predicates')
    keys=('actualExit','operatorSource','productionSource','candidateSource','candidateManifestSha256','genuineParentBeforeSha256','phases','startedUTC','completedUTC','guestMutations0')
    value={'actualExit':0,'source':SOURCE,'currentSource':CURRENT,'candidateBOM':BOM,'beforeSha256':BEFORE,
      'abi':{k:abi[k]for k in keys},'stage':stage,'prepare':prepare,'independentPost':r,'postObservedUTC':post['observedUTC'],'postPayloadSha256':post['payloadSha256'],
      'originalReceiptRefs':refs,'currentApprovalEpochChanged':False,'businessStartsStopsReloadsSqlWrites':0,'privateFull11OrDbOrSessionPublished':False,
      'oldNativeImported':False,'formalAccepted':False,'F03Accepted':False,'acceptedLeafDelta':0,'effortPercent':None}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5623-current-ro-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'candidateReadonlyAcceptedTechnical':True,'currentLinkChanged':False,'sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
