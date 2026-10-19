"""Conservative F03 applicability source reauthentication, never imports old PT/native success."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from collections import Counter,defaultdict
from pg5540_snapshot_scratch_selected import ROOT,sha

ALLOWED={'CONTEXT_NOT_APPLICABLE','FALSE_POSITIVE','REQUIRED_CONTRACT'}
SOURCE='9463db1ac23437043facf95b87f64b9fc7e758bd'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5758-current-dispositions-v1'


def coordinate(row):return(row['sourcePath'],row['rule'],*(int(row[k])for k in('beginline','endline','begincolumn','endcolumn')))


def bind_one(row,candidates,raw,before_classes,current_classes):
    result=copy.deepcopy(row)
    if len(candidates)!=1:return result,'NO_OR_AMBIGUOUS_PRIOR'
    old=candidates[0]
    if old.get('status')not in ALLOWED:return result,'PRIOR_NOT_DISPOSITIONED'
    if old['sourceSha256']!=row['sourceSha256']:return result,'SOURCE_CHANGED'
    if hashlib.sha256(raw).hexdigest()!=row['sourceSha256']:raise ValueError('actual current source must match exact diagnostic')
    types=re.findall(rb'^(?:(?:public|final|abstract|sealed|non-sealed|strictfp)\s+)*(?:class|record|enum|interface)\s+([A-Za-z_$][A-Za-z0-9_$]*)',raw,re.M)
    path=row['sourcePath'];name=Path(path).stem
    if types!=[name.encode()]:return result,'OWNER_MAPPING_AMBIGUOUS'
    module=path.split('/')[1].removeprefix('schubert-nk-');member=path.split('/src/main/java/')[1][:-5];prefix=module+':'+member
    before={k:v for k,v in before_classes.items()if k==prefix+'.class'or k.startswith(prefix+'$')}
    current={k:v for k,v in current_classes.items()if k==prefix+'.class'or k.startswith(prefix+'$')}
    if not current or current!=before:return result,'OWNER_PHYSICAL_BYTES_CHANGED'
    result.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition=old['status'],priorFindingId=old['findingId'],
      priorReason=old.get('reason',''),historicalCaseIds=[r['testId']for r in old.get('wholeCaseRefs',[])],currentWholeCaseRefs=[],
      currentWholeJoinPending=True,newDispositionCreated=False,rawWarningRetained=True,sourceAndCoordinatesExact=True,
      owningPhysicalClassesCount=len(current),owningPhysicalClassesSha256=hashlib.sha256(json.dumps(current,sort_keys=True).encode()).hexdigest())
    return result,'REBOUND'


def main():
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';w=ROOT.parent/'pgpt-runs/PG379'
    oldpath=base/'PG5690-current-identity-review-v1/manifest.json'
    if sha(oldpath)!='7d318fea2b0cdddaf7af4de85aaf6453356689ab0b06d42e9d7dcaa24ee4c53e':raise ValueError('immutable prior individual dispositions')
    old=json.loads(oldpath.read_bytes());wholepath=base/'PG5588-current3905-cases/qualification.json'
    if sha(wholepath)!=old['currentWholeSha256']:raise ValueError('actual old-source physical-class proof')
    before=json.loads(wholepath.read_bytes())
    if before['productionSource']!=old['source']or before['mainClasses']!=1664:raise ValueError('prior source correspondence')
    sp=base/'PG5750-exception-static-v1/manifest.json'
    if sha(sp)!='70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9':raise ValueError('current immutable static projection')
    pub=json.loads(sp.read_bytes());private=w/'pg5750-exception-static-v1/manifest.safe.json'
    if sha(private)!=pub['privateManifestSha256']:raise ValueError('exact current actual source/byte map')
    proof=json.loads(private.read_bytes())
    if proof['source']!=SOURCE or proof['actualExit']!=0:raise ValueError('actual current source static first')
    if subprocess.check_output(['git','diff',old['source'],SOURCE,'--','pom.xml','.mvn','mvnw',':(glob)src/*/pom.xml','src/deployment','program/characterization'],cwd=ROOT):raise ValueError('review architecture/dependencies/templates changed; no automatic context transfer')
    actual={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if actual!=proof['allSourceHashes']:raise ValueError('current fixed source only, no source drift during whole')
    source_rows=json.loads(sp.with_name('findings.json').read_bytes());index=defaultdict(list)
    for row in old['findings']:index[coordinate(row)].append(row)
    rows=[];counts=Counter();rebound=Counter();owners={}
    for row in source_rows:
        new,kind=bind_one(row,index[coordinate(row)],(ROOT/row['sourcePath']).read_bytes(),before['allPhysicalMainSha256'],proof['auxClassHashes'])
        counts[kind]+=1
        if kind=='REBOUND':
            new.update(priorReviewSource=old['source'],priorReviewManifestSha256=sha(oldpath),currentPhysicalProofSha256=sha(private))
            rebound[new['priorDisposition']]+=1;owners[row['sourcePath']]={'count':new['owningPhysicalClassesCount'],'sha256':new['owningPhysicalClassesSha256']}
        rows.append(new)
    if len(rows)!=1582 or len({r['findingId']for r in rows})!=1582 or [r['findingId']for r in rows]!=[r['findingId']for r in source_rows]:raise ValueError('all1582 current raw diagnostic identities preserved')
    # Explicitly preserve the three later sink reviews without importing their old twelve PT.
    ap=base/'PG5740-local-audit-review-v1/manifest.json'
    if sha(ap)!='ed89cff2381e047f146067d0f85a0e35f62ff09f8e655a5742e8112ae3cc7ccc':raise ValueError('later exact sink review')
    audit=json.loads(ap.read_bytes());ar=json.loads(ap.with_name('findings.json').read_bytes());aindex=defaultdict(list)
    for r in ar:
        if r['status']=='REQUIRED_CONTRACT':aindex[coordinate(r)].append(r)
    apk=w/'pg5738-local-audit-selected-v1/manifest.safe.json'
    if sha(apk)!=audit['selectedManifestSha256']:raise ValueError('actual historical sink class bytes')
    audit_classes=json.loads(apk.read_bytes())['allPhysicalMainSha256'];audit_count=0
    for i,row in enumerate(rows):
        if coordinate(row)not in aindex:continue
        new,kind=bind_one(row,aindex[coordinate(row)],(ROOT/row['sourcePath']).read_bytes(),audit_classes,proof['auxClassHashes'])
        if kind!='REBOUND':raise ValueError('three exact unchanged sink source/owner bindings')
        if row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':raise ValueError('no double classification')
        new.update(priorReviewSource=audit['source'],priorReviewManifestSha256=sha(ap),currentPhysicalProofSha256=sha(private),historicalTestRefs=aindex[coordinate(row)][0]['testRefs'])
        rows[i]=new;audit_count+=1
    if audit_count!=3:raise ValueError('only three later sink rows')
    value={'actualExit':0,'source':SOURCE,'currentRawFindings':1582,'diagnosticIdsPreserved':1582,'priorReviewSource':old['source'],'priorReviewManifestSha256':sha(oldpath),'priorPhysicalWholeSha256':sha(wholepath),'currentStaticManifestSha256':sha(sp),'currentPrivateSourceByteProofSha256':sha(private),'priorDispositionRebound':sum(rebound.values()),'reboundPriorDispositionCounts':dict(rebound),'laterExactSinkRebound':audit_count,'bindingOutcomes':dict(counts),'statusCounts':dict(Counter(r['status']for r in rows)),'owningSourceProofs':owners,'newDispositionsCreated':0,'currentWholeJoinPending':True,'historicalTestsImportedAsCurrent':False,'executedPtAdded':0,'ptAlternativeCompleted':0,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    os.umask(0o077);OUT.mkdir(parents=True)
    for name,data in [('manifest.json',value),('findings.json',rows)]:
        with(OUT/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in('actualExit','source','currentRawFindings','priorDispositionRebound','reboundPriorDispositionCounts','laterExactSinkRebound','bindingOutcomes','statusCounts','F03Accepted')}))
    print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'findingsSha256':sha(OUT/'findings.json')}))


if __name__=='__main__':main()
