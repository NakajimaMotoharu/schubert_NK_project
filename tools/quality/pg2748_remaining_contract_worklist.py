"""Mechanical current native gaps -> owning WBS and methods, without acceptance or cost guesses."""
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg2674_operation_publication_sources import production


def main():
    root=Path(__file__).resolve().parents[2]
    receipt=W/'pg2746-backup-admission-native-qualified-v1/manifest.safe.json'
    value=json.loads(receipt.read_bytes())
    if type(value.get('actualExit'))is not int or value['actualExit']!=0 or value.get('productionSource')!=production():
        raise ValueError('actual current full/native receipt required')
    native=value['result']
    if native.get('classByteMismatch')!=0 or native.get('oldNativeImported')is not False or native.get('qualified2744Tests')!=3669:
        raise ValueError('exact current3669 source/member/session proof required')
    inventory=json.loads(next((root/'documents/400_PGPT/470_PMO').glob('485*.json')).read_bytes())
    owners={}
    def walk(node):
        if isinstance(node,dict):
            if isinstance(node.get('path'),str) and isinstance(node.get('owner'),str):
                old=owners.setdefault(node['path'],node['owner'])
                if old!=node['owner']:raise ValueError('unique owning artifact required')
            for child in node.values():walk(child)
        elif isinstance(node,list):
            for child in node:walk(child)
    walk(inventory)
    rows=[]
    for module,classes in native['gaps'].items():
        for cls in classes:
            path='src/schubert-nk-'+module+'/src/main/java/'+cls['class'].split('$')[0]+'.java'
            if path not in owners or not (root/path).is_file():raise ValueError('all remaining classes require exact source/owner')
            rows.append({'module':module,'class':cls['class'],'path':path,'costOwner':owners[path],
                'mainSourceSha256':hashlib.sha256((root/path).read_bytes()).hexdigest(),'missed':cls['missed'],
                'methods':cls['methods'],'sourceLines':cls['sourceFileMissedLines'],
                'status':'CONTRACT_REVIEW_REQUIRED','criteriaAccepted':False,'actualAllocatedPp':None})
    remaining={k:sum(c[k]['missed']for c in native['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']}
    report={'productionSource':production(),'nativeReceiptSha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),
        'run':'PG2748-current-contract-worklist','remainingModuleCounters':remaining,'classEntries':len(rows),
        'costOwnerCount':len({r['costOwner']for r in rows}),'rows':rows,'noCostOrAcceptanceInference':True,
        'policy':'Read exact method/line and relevant RD/UI/SS/Test evidence before next group; source-file lines may repeat across inner classes, do not sum as distinct lines; main owner only/reference costs0; current modules not historical native.'}
    out=W/'pg2748-current-contract-worklist-v1';out.mkdir(mode=0o700)
    (out/'manifest.safe.json').write_text(json.dumps(report,sort_keys=True))
    print(json.dumps({'run':report['run'],'remaining':remaining,'classEntries':len(rows),'owners':report['costOwnerCount'],'acceptedLeafDelta':0}))


if __name__=='__main__':main()
