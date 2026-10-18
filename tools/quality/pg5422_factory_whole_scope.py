"""Bind current limited237 partition to actual whole1664 and four protected outer owners."""
import hashlib
import json
import os
from pg5416_ownership_whole_qualification import SOURCE,ROOT

BASE='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'
REFS={
 'selected':BASE+'pg5404-process-query-green-v3-metadata-v2/manifest.json',
 'partition':BASE+'PG5410-scope-classification-process-query-v1/manifest.json',
 'whole':BASE+'PG5414-current3896-cases/qualification.json',
 'cases':BASE+'PG5414-current3896-cases/manifest.json',
 'readonly':BASE+'PG5418-readonly-ownership-bytecode-v1/manifest.json'}


def validate(values,hashes):
    selected,partition,whole,cases,readonly=(values[key] for key in ('selected','partition','whole','cases','readonly'))
    if selected['actualExit']!=0 or selected['productionCandidateSource']!=SOURCE or selected['tests']!=1164:
        raise ValueError('same-source selected all owner test cases first')
    if partition['source']!=SOURCE or partition['qualificationSha256']!=hashes['selected'] or partition['classificationCounts']!={
        'FIXED_LIMITED':236,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':0}:
        raise ValueError('exact current original237 partition and independent source binding')
    if (whole['productionSource'],whole['sourceSnapshot'],whole['tests'],whole['suites'],whole['mainClasses'])!=(SOURCE,SOURCE,3896,562,1664) or (
        whole['FESFlakyNotRun']!=0 or whole['staticSixModules']!=0 or whole['allSixFormatBeforeAnyPt'] is not True or whole['oldNativeImported'] is not False):
        raise ValueError('genuine same-source all-six whole qualification, never selected result arithmetic')
    current=selected['mainDelta']['physicalSha256'];physical=whole['allPhysicalMainSha256']
    if len(current)!=767 or len(physical)!=1664 or any(physical.get(key)!=digest for key,digest in current.items()):
        raise ValueError('all current selected767 recompiled into the original qualified whole1664')
    if cases['source']!=SOURCE or cases['projectionActualExit']!=0 or cases['tests']!=3896 or cases['testExecutionsIssued']!=0:
        raise ValueError('all genuine whole XML case projection, no replay')
    if readonly['actualExit']!=0 or readonly['source']!=SOURCE or readonly['readonlyCandidateCount']!=4 or (
        readonly['wholeQualificationSha256']!=cases['qualificationManifestSha256'] or
        sum(map(len,readonly['compilerTwrSites'].values()))!=14 or len(readonly['webPreexistingOwner']['directResourceFieldStores'])!=8):
        raise ValueError('all four actual TWR/preowner candidates, not source grep alone')
    if any(value['formalAccepted'] is not False for value in (selected,partition,whole,readonly)):
        raise ValueError('limited/source qualification cannot rewrite formal acceptance')
    return {'source':SOURCE,'actualExit':0,'original237Partition':partition['classificationCounts'],
        'wholeSourceQualified':True,'allSelected767ClassBytesMatchActualWhole1664':True,
        'readonlyProtectedByCompilerTwr':3,'readonlyProtectedByPreexistingOwner':1,'readonlyCandidatesUnknown':0,
        'additionalFactoriesLimitedSeparateDenominator':4,'formalAccepted':False,'wholeHorizontalComplete':False,
        'newSourceNativeQualified':False,'nativeImported':False,'acceptedLeafDelta':0,'effortPercent':None,
        'actualAllocatedPp':None,'vmActions':0,'mavenReissued':0,'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],
        'unaccepted':['current source native and all four100','F03 applicability','CHR/DIF/451/trace','QA051final and handoff'],
        'evidenceRefs':{key:{'path':REFS[key],'sha256':hashes[key]} for key in REFS}}


def main():
    values={key:json.loads((ROOT/path).read_bytes()) for key,path in REFS.items()}
    hashes={key:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for key,path in REFS.items()}
    value=validate(values,hashes)
    out=ROOT/(BASE+'PG5422-factory-whole-scope-v1');os.umask(0o077);out.mkdir(parents=True)
    path=out/'manifest.json'
    with path.open('x') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'actualExit':0,'partition':value['original237Partition'],'readonlyUnknown':0,
        'wholeSourceQualified':True,'formalAccepted':False,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
