"""Independent explicit producer-schema negatives; original38/analysis never rerun."""
import copy
import datetime as dt
import json
from pathlib import Path
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from selected_post_contract import clean

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
RAW=BASE/'PG9032-api-service-post-v1/manifest.json'
OUT=BASE/'PG9036-selected-post-guards-v1'
SOURCE='73d94fc525c6ea8828ca82d906ec583146fee7bf'
CLASSES={'dev/codex/schubert/nk/api/monitoring/ApiServiceMetricBinding','dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandler'}


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    assert sha(RAW.read_bytes())=='4585f25047cd5f657152facf8486a44a69fe73c67d17345b864cd61e3965a358'
    record=json.loads(RAW.read_bytes())
    expected={'LINE':dict(missed=0,covered=60),'METHOD':dict(missed=0,covered=10),'CLASS':dict(missed=0,covered=2),'BRANCH':dict(missed=0,covered=8)}
    assert clean(record,SOURCE,38,2,CLASSES)==expected
    cases=[]
    def changed(name,mutate):
        value=copy.deepcopy(record);mutate(value);cases.append((name,value))
    changed('wrong-source',lambda value:value.update(source='0'*40))
    changed('wrong-test-count',lambda value:value.update(tests=37))
    changed('failed-post',lambda value:value.update(actualExit=1))
    changed('boolean-exit',lambda value:value.update(actualExit=False))
    changed('missing-unclassified',lambda value:value.pop('unclassified'))
    changed('null-unclassified',lambda value:value.update(unclassified=None))
    changed('unknown-class',lambda value:value['executableClasses'].update({'unknown':next(iter(value['executableClasses'].values()))}))
    changed('missed-branch',lambda value:next(iter(value['executableClasses'].values()))['counters']['BRANCH'].update(missed=1))
    changed('vacuous-branch',lambda value:next(iter(value['executableClasses'].values()))['counters']['BRANCH'].update(covered=0))
    changed('boolean-aggregate',lambda value:value['counters']['LINE'].update(missed=False))
    changed('wrong-aggregate',lambda value:value['counters']['LINE'].update(covered=61))
    changed('crc-mismatch',lambda value:value.update(actualCrcMismatch=1))
    changed('two-sessions',lambda value:value.update(actualSessions=2))
    changed('union',lambda value:value.update(coverageUnion=True))
    changed('excluded',lambda value:value.update(customExclusionsAdded=True))
    changed('suppressed',lambda value:value.update(suppressionsAdded=True))
    changed('whole-gate-inferred',lambda value:value.update(whole451Accepted=True))
    changed('raw-pmd-warning',lambda value:value['staticRaw']['pmd'].update(findings=1))
    changed('processing-error',lambda value:value['staticRaw']['spotbugs'].update(processingErrors=1))
    changed('missing-static-kind',lambda value:value['staticRaw'].pop('checkstyle'))
    changed('failed-analysis',lambda value:value['staticRaw']['pmd'].update(actualExit=4))
    changed('timedout-analysis',lambda value:value['staticRaw']['pmd'].update(timedOut=True))
    rejected=[]
    for name,value in cases:
        try:clean(value,SOURCE,38,2,CLASSES)
        except (ValueError,KeyError):rejected.append(name)
        else:raise AssertionError('bad producer proof accepted')
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,source=SOURCE,
         producerManifestSha256=sha(RAW.read_bytes()),actualProducerSchemaUsed=True,independentGoldenCounters=expected,
         metadataCounterexamples=rejected,productTestsExecuted=0,analysisJobsRerun=0,
         missingOrUnknownNotDefaultedToZero=True,bug='BUG-1730',ykt='YKT-1481',formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,metadataCounterexamples=len(rejected),productTestsExecuted=0)))


if __name__=='__main__':main()
