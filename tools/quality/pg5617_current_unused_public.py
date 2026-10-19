"""Original stage/place/post receipt allowlist; no full11/DB/session/key bytes."""
import hashlib
import json
import os
from pg5608_current_unused_sources import W,CURRENT,SOURCE,BEFORE,BOM
from pg5590_current_static_projection import ROOT


def main():
    refs={'abi':('pg5610-frozen-v1.safe.json','79f9a554effb9800d27acab31db9b9d5d3415468249839693279e94164780ff1'),
      'stage':('pg5612-stage-v1.safe.json','f4d5d78e595e900229dc2f775d5cc0e27bd853d94f05c62d8d117df84fa07406'),
      'place':('pg5612-place-v1.safe.json','4b106639f7e81132fc794dc0c62778d993ced972cf899b970c71aa1d6b8ae025'),
      'post':('pg5614-current-unused-independent-post-v1/manifest.safe.json','2e13c88651848101e83857f9a4e398b0427eabaf723751c2e999cb36c103757a')}
    values={}
    for key,(path,digest)in refs.items():
        raw=(W/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('immutable original complete receipt, never replay')
        values[key]=json.loads(raw)
    abi,stage,place,post=(values[k]for k in('abi','stage','place','post'));r=post['result']
    if not(all(type(v['actualExit'])is int and v['actualExit']==0 for v in values.values())and abi['productionSource']==CURRENT
      and abi['candidateSource']==stage['candidateSource']==place['candidateSource']==r['candidateSource']==SOURCE
      and stage['installedSource']==place['installedSource']==post['source']==r['productionSource']==CURRENT
      and r['full11BeforeSha256']==r['privateAfterSha256']==BEFORE and r['candidateManifestSha256']==BOM and r['nativePhysicalFiles']==94
      and r['allFull11BeforeAfterEqual']and r['allTenRefsReturnedNormally']and r['candidate187SignatureVerified']and all(v['actualExit']==0 for v in abi['phases'].values())):raise ValueError('same distinct-current unused graph complete')
    abi_keys=('actualExit','operatorSource','productionSource','candidateSource','candidateManifestSha256','genuineParentBeforeSha256','bundleSha256','phases','startedUTC','completedUTC','guestMutations0')
    value={'actualExit':0,'source':SOURCE,'currentSource':CURRENT,'candidateBOM':BOM,'beforeSha256':BEFORE,
      'abi':{k:abi[k]for k in abi_keys},'stage':stage,'place':place,'independentPost':r,'postPayloadSha256':post['payloadSha256'],'postObservedUTC':post['observedUTC'],
      'originalReceiptRefs':refs,'RootOrOwnedStopReissued':False,'wholeOrSignatureReplayed':False,'currentApprovalEpochChanged':False,'businessStartsStopsReloadsSqlWrites':0,
      'rawDatabaseNativeSessionSignatureKeyPublished':False,'newSourceNativeAccepted':False,'formalAccepted':False,'F03Accepted':False,'acceptedLeafDelta':0,'effortPercent':None,
      'observationGap':{'firstTerminalObservedUTC':post['observedUTC'],'laterHostReadJST':'2026-10-19T22:16:28+09:00','cause':None,'missingUsageEstimated':False,'nextMutationRequiresOwnFreshCurrentGuard':True}}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5617-current-unused-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'currentSource':CURRENT,'unusedPostComplete':True,'sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
