"""Bind original237 limited factory partition and exact readonly bytecode to current whole."""
import copy
import hashlib
import json
import os
import subprocess
import pg5146_scope_classification as inventory
from pg5261_scope_inventory_continue import fixed_names,NATIVE_FIXED
from pg5418_readonly_ownership_bytecode import CLASSES
from pg5590_current_static_projection import ROOT,W,BASE,SOURCE

OUT=BASE/'PG5596-current-factory-scope-v1'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def validate(whole,old_scope,partition,readonly,monitor,selected):
    if not(whole['productionSource']==whole['sourceSnapshot']==SOURCE and(whole['tests'],whole['suites'],whole['mainClasses'])==(3905,563,1664)
        and whole['FESFlakyNotRun']==whole['staticSixModules']==0 and whole['allOriginalCaseIdentitiesRetained']and whole['allSixFormatBeforeAnyPt']and not whole['oldNativeImported']and not whole['formalAccepted']):raise ValueError('genuine current whole3905/563/all1664 required')
    expected={'FIXED_LIMITED':236,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':0}
    if old_scope['original237Partition']!=expected or partition['classificationCounts']!=expected or old_scope['readonlyCandidatesUnknown']!=0:raise ValueError('original limited partition plus four readonly proof, not broader completion')
    rows=copy.deepcopy(partition['files']);fixed=fixed_names(rows)
    extra=fixed-inventory.ROOT_FIXED-inventory.CALLER_FIXED-NATIVE_FIXED
    count=inventory.classify(rows,lambda p:(ROOT/p).read_bytes(),native=True,evidence_ref='018_NK-OPS-001/evidence/provisional/PG5588-current3905-cases/qualification.json',extra_fixed=extra)
    if count!=expected or sum(count.values())!=237:raise ValueError('all237 historical candidates checked against actual current sources')
    physical=whole['allPhysicalMainSha256']
    if len(physical)!=1664 or selected['physicalMain']['sha256']!=physical or selected['sourceSnapshot']!=SOURCE or selected['actualCases']!=73 or not selected['greenSelectedQualified']:raise ValueError('actual current73 classes all equal genuine current whole')
    if monitor['sourceSnapshot']!=SOURCE or monitor['actualExit']!=0 or monitor['actualSelectedCases']!=73 or sum(map(len,monitor['privateMonitorMethods'].values()))!=14:raise ValueError('current private guards and before-acquisition lock proof required')
    if readonly['readonlyCandidateCount']!=4 or sum(map(len,readonly['compilerTwrSites'].values()))!=14 or len(readonly['webPreexistingOwner']['directResourceFieldStores'])!=8:raise ValueError('all four readonly outer proofs')
    for name,module in CLASSES.items():
        key=module+':'+name.replace('.','/')+'.class'
        if readonly['classHashes'][name]['classSha256']!=physical.get(key):raise ValueError('each actual current readonly owner class must equal established full bytecode proof')
    return {'actualExit':0,'source':SOURCE,'wholeSourceQualified':True,'original237Partition':count,'original237FilesChecked':len(rows),
        'readonlyProtectedByCompilerTwr':3,'readonlyProtectedByPreexistingOwner':1,'readonlyCandidatesUnknown':0,'readonlyActualClassHashes':readonly['classHashes'],
        'currentOriginalFactorySourceHashes':{r['path']:sha((ROOT/r['path']).read_bytes())for r in rows},
        'currentMonitorMethods':14,'currentWholeCases':3905,'currentWholeMain':1664,'noOldTestSuccessImported':True,'scope':'ORIGINAL237_LIMITED_PLUS_FOUR_READONLY_NOT_ALL_FACTORY_DEFECTS',
        'wholeHorizontalComplete':False,'newSourceNativeQualified':False,'formalAccepted':False,'F03Accepted':False,'acceptedLeafDelta':0,'effortPercent':None,'vmActions':0,'mavenReissued':0}


def main():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('current fixed source')
    paths={
      'whole':BASE/'PG5588-current3905-cases/qualification.json',
      'old_scope':BASE/'PG5422-factory-whole-scope-v1/manifest.json',
      'partition':BASE/'PG5410-scope-classification-process-query-v1/manifest.json',
      'readonly':BASE/'PG5418-readonly-ownership-bytecode-v1/manifest.json',
      'monitor':W/'pg5568-monitor-bytecode-v3/manifest.safe.json',
      'selected':W/'pg5566-private-monitor-green-v3/manifest.safe.json'}
    fixed={'old_scope':'a30198c0408c2e09e54e84816897156e5eeb7207a94543a41fd73c200e4e8718','monitor':'8e852219d9ada714da01b66604238ecf21025bfae14ce76b0d33a21bf87f0d32','selected':'9eef40acd5388ebf53737907bb5d664cf60a38430894de07a4a56df31896ca73'}
    hashes={k:sha(p.read_bytes())for k,p in paths.items()}
    if any(hashes[k]!=v for k,v in fixed.items()):raise ValueError('immutable qualified proof inputs')
    prior=json.loads(paths['old_scope'].read_bytes())
    if any(prior['evidenceRefs'][k]['sha256']!=hashes[k]for k in('partition','readonly')):raise ValueError('exact established partition/bytecode proof, not arbitrary prior')
    value=validate(**{k:json.loads(p.read_bytes())for k,p in paths.items()});value['evidenceRefs']={k:{'path':str(p.relative_to(ROOT))if p.is_relative_to(ROOT)else str(p),'sha256':hashes[k]}for k,p in paths.items()}
    os.umask(0o077);OUT.mkdir()
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'original237Partition':value['original237Partition'],'readonlyUnknown':0,'sha256':sha((OUT/'manifest.json').read_bytes()),'formalAccepted':False}))


if __name__=='__main__':main()
