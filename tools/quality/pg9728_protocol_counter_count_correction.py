"""Append correction for zero-counter class count; preserve original reports and no product rerun."""
import copy
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from class_counter_applicability import classify
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
OUT = BASE / 'PG9728-protocol-counter-count-correction-v1'
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    post = data.read_checked(BASE / 'PG9724-protocol-module-post-v2/manifest.json',
        '5eb3672c1838e6ef522e57f724392e946c437b0499967f7623d889504227cd77')
    generated = data.read_checked(BASE / 'PG9726-protocol-generated-shape-post-v1/manifest.json',
        'c5e2b600dfadfca7c1a8a889fec5d605e775b7e75e36955bc4a70cf5298290b5')
    assert post['actualExit'] == generated['actualExit'] == 0 and post['source'] == generated['source'] == SOURCE
    detail = data.read_checked(BASE / 'PG9724-protocol-module-post-v2/whole-module-counters.json',post['moduleCounterDetailsSha256'])
    zero = {k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    branchless = {k:dict(missed=0,covered=1 if k != 'BRANCH' else 0) for k in zero}
    assert classify(zero) == 'NO_COUNTERS_NOT_A_MEASURED_PASS'
    assert classify(branchless) == 'FOUR100_MEASURED_APPLICABLE'
    partial = copy.deepcopy(branchless)
    partial['BRANCH'] = dict(missed=1,covered=1)
    assert classify(partial) == 'MISSED_COUNTERS'
    absent = copy.deepcopy(branchless)
    absent['CLASS'] = dict(missed=0,covered=0)
    assert classify(absent) == 'INCOMPLETE_APPLICABILITY_NOT_A_MEASURED_PASS'
    rejected = []
    negative = copy.deepcopy(branchless)
    negative['LINE']['covered'] = -1
    boolean = copy.deepcopy(branchless)
    boolean['METHOD']['missed'] = False
    for label,value in [('null',None),('missing-kind',{}),('negative',negative),('boolean',boolean)]:
        try:
            classify(value)
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('invalid counter accepted')
    classifications = {name:classify(row['counters']) for name,row in detail['physicalClasses'].items()}
    measured = sorted(n for n,v in classifications.items() if v == 'FOUR100_MEASURED_APPLICABLE')
    no_counters = sorted(n for n,v in classifications.items() if v == 'NO_COUNTERS_NOT_A_MEASURED_PASS')
    assert len(classifications) == 169 and len(measured) == 159 and len(no_counters) == 10
    assert set(no_counters) == set(generated['classes']) | {n for n in post['structuralNoCodeClasses'] if n in detail['physicalClasses']}
    prior = data.read_checked(BASE / 'PG9716-typed-boundaries-component-post-v1/manifest.json',
        'a0947660f456b9aee73a43e8e4f50748edf58b43ea2adbab5251d1c3737912fc')
    prior_detail = data.read_checked(BASE / 'PG9716-typed-boundaries-component-post-v1/source-unit-counters.json',prior['sourceUnitCountersSha256'])
    assert len(prior_detail['physicalClasses']) == 75 and all(classify(r['counters']) == 'FOUR100_MEASURED_APPLICABLE' for r in prior_detail['physicalClasses'].values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        originalModulePostSha256='5eb3672c1838e6ef522e57f724392e946c437b0499967f7623d889504227cd77',
        originalReportedFour100ExecutableClassCount=post['four100ExecutableClassCount'],correctedMeasuredFour100ClassCount=len(measured),
        physicalInventory=176,reportedClasses=169,packageAnnotationNotReported=7,noCodeInterfaces=6,standardFilteredCompilerHelpers=4,
        classifications=classifications,measuredFour100ClassNames=measured,zeroCounterNames=no_counters,
        naturalBranchlessPositive=True,zeroCounterAndMissingApplicabilityNotPass=True,positiveVectors=4,invalidCounterVectors=rejected,
        prior75ScopeUnaffected=True,originalReportModified=False,rawCounterModified=False,productTestsExecuted=0,
        rawJacocoFour100=True,strictGeneratedInstructionCoverageQualified=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,originalCount=post['four100ExecutableClassCount'],correctedCount=len(measured),zeroCounterClasses=len(no_counters),
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
