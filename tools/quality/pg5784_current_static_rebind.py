"""Current2bbb reauthentication only; original3932 PT references remain historical until3939."""
import copy
import json
import os
from collections import Counter,defaultdict
from pg5540_snapshot_scratch_selected import ROOT,sha
from static_disposition_overlay import load,BASE
from pg5758_static_rebind import bind_one,coordinate
from pg5780_jms_primary_whole import SOURCE,W

OUT=BASE/'PG5784-current-dispositions-v1'
OLD_SOURCE='9463db1ac23437043facf95b87f64b9fc7e758bd'


def main():
    oldp=BASE/'PG5772-primary-capture27-v1/manifest.json';oldsha='b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487';oldrows=load(oldp,oldsha,OLD_SOURCE)
    qp=BASE/'PG5754-current3932-cases/qualification.json'
    if sha(qp)!='ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18':raise ValueError('original qualified old-source whole class map')
    oldq=json.loads(qp.read_bytes());sp=BASE/'PG5776-jms-primary-static-v1/manifest.json';rp=sp.with_name('findings.json')
    if sha(sp)!='aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f'or sha(rp)!='207c64bdb95dedd001056d79318acf1ff6c53ec00b7c17d55e3ba3bd9530c186':raise ValueError('all1585 current exact diagnostics')
    pub=json.loads(sp.read_bytes());private=W/'pg5776-jms-primary-static-v1/manifest.safe.json'
    if sha(private)!=pub['privateManifestSha256']:raise ValueError('actual current849/1664 selected compile proof')
    proof=json.loads(private.read_bytes())
    if proof['source']!=SOURCE or proof['actualExit']!=0 or oldq['productionSource']!=OLD_SOURCE:raise ValueError('source correspondence, no borrowed current success')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('all849 current source fixed during original whole')
    index=defaultdict(list);decided={}
    for row in oldrows:
        if row['status']=='NOT_REVIEWED_CURRENT_SOURCE':continue
        value=copy.deepcopy(row);value['wholeCaseRefs']=value.get('currentWholeCaseRefs',[]);value['reason']=value.get('reason')or value.get('priorReason','')
        if not value['reason']:raise ValueError('prior individual rationale must exist')
        index[coordinate(value)].append(value);decided[value['findingId']]=value
    current=json.loads(rp.read_bytes());rows=[];outcomes=Counter();dispositions=Counter();used=set()
    for row in current:
        value,kind=bind_one(row,index[coordinate(row)],(ROOT/row['sourcePath']).read_bytes(),oldq['allPhysicalMainSha256'],proof['auxClassHashes']);outcomes[kind]+=1
        if kind=='REBOUND':
            used.add(value['priorFindingId']);dispositions[value['priorDisposition']]+=1
            value.update(priorReviewSource=OLD_SOURCE,priorReviewManifestSha256=oldsha,currentPhysicalProofSha256=sha(private),historicalWholeQualificationSha256=sha(qp),currentWholeCaseRefs=[],currentWholeJoinPending=True,historicalPtImportedAsCurrent=False)
        rows.append(value)
    held=[{'findingId':ident,'sourcePath':decided[ident]['sourcePath'],'rule':decided[ident]['rule'],'priorBeginline':decided[ident]['beginline'],'reason':'SOURCE_OR_COORDINATES_CHANGED; no automatic transfer'}for ident in sorted(set(decided)-used)]
    if len(rows)!=1585 or len(used)!=472 or len(held)!=1 or not held[0]['sourcePath'].endswith('/ArtemisReplyConsumer.java')or held[0]['rule']!='CompareObjectsWithEquals':raise ValueError('only exact472 unchanged and one moved/changed owner scope held')
    if [r['findingId']for r in rows]!=[r['findingId']for r in current]or len({r['findingId']for r in rows})!=1585:raise ValueError('all diagnostic identities/order preserved')
    os.umask(0o077);OUT.mkdir();target=OUT/'findings.json'
    with target.open('x')as f:json.dump(rows,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value={'actualExit':0,'source':SOURCE,'priorReviewSource':OLD_SOURCE,'priorReviewManifestSha256':oldsha,'priorWholePhysicalProofSha256':sha(qp),'currentStaticProofSha256':sha(sp),'currentFindingsSha256':sha(rp),'currentActualSourceByteProofSha256':sha(private),'currentRawFindings':1585,'reauthenticatedUnchangedDispositions':len(used),'priorDispositionCounts':dict(dispositions),'bindingOutcomes':dict(outcomes),'heldPriorDispositions':held,'statusCounts':dict(Counter(r['status']for r in rows)),'inventoryFile':'findings.json','inventorySha256':sha(target),'newDispositionsCreated':0,'currentWholeJoinPending':True,'currentWholeCaseRefs':[],'historicalPtImportedAsCurrent':False,'executedPtAdded':0,'ptAlternativeCompleted':0,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k not in('currentWholeCaseRefs',)}));print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'findingsSha256':sha(target)}))


if __name__=='__main__':main()
