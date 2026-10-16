"""SSC298 current metadata only; original 4494 transport remains a failure."""
import hashlib
import inspect
import json
import pg4494_inspect_pair_recover as previous
import pg4512_metadata_only_stage as stage
from pg1446_current_cold_stage import W

DESIGN_MAIN='b65d1283e9dc384f761899bc8448cd50b9f572fc'
OUT=W/'pg4514-metadata-only-recover-v1'


def original_receipt():
    folder=W/'pg4494-inspect-pair-recover-v2';receipt=json.loads((folder/'manifest.safe.json').read_bytes())
    start=json.loads((folder/'start.safe.json').read_bytes())
    if type(receipt.get('actualExit'))is not int or receipt['actualExit']==0 or receipt.get('source')!='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e' or receipt.get('oldScopesNormal')is not False or receipt.get('formalAccepted')is not False:
        raise ValueError('original actual recovery failure required; never infer exit')
    if start['files']!={'keeper.py':'3d821a45b0942b453fe49f0a5f0a583578995cd1841481413dbb3ce26bfa8c87'}or start['designMain']!='3a7f50158b05227cb274e9c98951181a99c4e557':raise ValueError('exact original reserved current scope required')
    if 'SSC297_UNKNOWN'not in(folder/'tail.private.log').read_text():raise ValueError('original unknown record preserved')
    return {**receipt,'originalTailSha256':hashlib.sha256((folder/'tail.private.log').read_bytes()).hexdigest()}


def complete(v):
    expected={'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','BOM':'0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
        'boot':'79a3260a-e16d-42bf-942a-b914ed144c28','mode':'recover','oldScopesNormal':False,'newTenRefsNormalClose':True,'unitOperationsIssued':0,
        'formalAccepted':False,'allOldProcessesAndResourcesGone':True,'signalsIssued':1,'childSignalsIssued':0,'oldPostReplayed':False}
    if type(v)is not dict or any(type(v.get(k))is not type(x)or v[k]!=x for k,x in expected.items()):raise ValueError('complete metadata-only receipt required')
    post_expected={'actualExit':0,'source':expected['source'],'BOM':expected['BOM'],'newMARDDBTenRefNormalClose':True,'all24OriginalBackupNativeUnitConfigUnchanged':True,
        'oldParentNormal':False,'parent143StillFailed':True,'independentFailedDoneRecoveryPost':True,'signalStartStopReloadDbWrites':0,'formalAccepted':False}
    post=v.get('independentPost')
    if type(post)is not dict or any(type(post.get(k))is not type(x)or post[k]!=x for k,x in post_expected.items()):raise ValueError('fresh independent post required')
    return v


def main_source():
    raw=inspect.getsource(previous.main)
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('one current observer boundary')
        raw=raw.replace(old,new,1)
    once('PENDING_SSC297_MAIN','PENDING_SSC298_MAIN')
    once("frame('SSC297_OWNERS_READY ')","frame('SSC298_METADATA_READY ')")
    once("frame('SSC297_JAVA_GONE originalTransportRequired=true')","frame('SSC298_METADATA_GONE originalTransportRequired=true')")
    once("            frame('SSC297_PAIR_GONE oldCloseUnknown=true');ack()\n",'')
    once("'originalInspectActualExit':original['actualExit']","'originalRecoveryActualExit':original['actualExit']")
    return raw


def main():
    if DESIGN_MAIN=='PENDING_SSC298_MAIN':raise ValueError('final design publication before metadata TERM')
    ns={**vars(previous),'stage':stage,'OUT':OUT,'DESIGN_MAIN':DESIGN_MAIN,'original_receipt':original_receipt,'complete':complete}
    exec(compile(main_source(),'<current one metadata-only recovery>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
