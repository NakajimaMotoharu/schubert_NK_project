"""Allowlisted original finite publication results; no full snapshot or secret."""
import hashlib
import json
import os
from pg5624_current_publication_sources import W,CURRENT,SOURCE,BOM
from pg5590_current_static_projection import ROOT


def main():
    paths={'abi':'pg5626-frozen-v1.safe.json','stage':'pg5628-stage-v1.safe.json',
      'activate':'pg5628-activate-v1.safe.json','post':'pg5630-current-publication-independent-post-v1/manifest.safe.json'}
    raw={k:(W/p).read_bytes()for k,p in paths.items()};values={k:json.loads(v)for k,v in raw.items()}
    abi,stage,activate,post=(values[k]for k in('abi','stage','activate','post'));r=post['result']
    if not(all(type(v['actualExit'])is int and v['actualExit']==0 for v in values.values())
      and r['productionSource']==SOURCE and r['candidateManifestSha256']==BOM
      and r['sevenFinitePhasesVerified']is True and r['originalBackupNative94Preserved']is True
      and r['newSourceParentNotStarted']is True and r['newTenReferencesReturnedNormally']is True
      and activate['currentApprovalEpochChanged']is True and all(v['actualExit']==0 for v in abi['phases'].values())):
        raise ValueError('original complete seven-phase newCurrent post required')
    keys=('actualExit','operatorSource','productionSource','candidateSource','candidateManifestSha256','genuineParentBeforeSha256','phases','startedUTC','completedUTC','guestMutations0')
    value={'actualExit':0,'source':SOURCE,'previousCurrent':CURRENT,'candidateBOM':BOM,'abi':{k:abi[k]for k in keys},
      'stage':stage,'activate':activate,'independentPost':r,'postObservedUTC':post['observedUTC'],'postPayloadSha256':post['payloadSha256'],
      'originalReceiptRefs':{k:{'path':paths[k],'sha256':hashlib.sha256(v).hexdigest()}for k,v in raw.items()},
      'oldNativeImported':False,'privateFull11OrDbOrSessionPublished':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5631-current-publication-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
