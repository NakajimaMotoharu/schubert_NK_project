"""Current Root limited completion record, no VM operations or token inference."""
from pg998_metrics import append

if __name__ == '__main__':
    print(append('V3_PUBLISHED_769_ROOT_NATIVE', 'ATTEMPT_END', {
        'source': '769ddb15cd735c25fef581b5f9850ef9d0053c0f',
        'wbsLeafIds': ['WBS-N15.02'],
        'referenceLeafIds': ['WBS-N05', 'WBS-N06', 'WBS-N07', 'WBS-N08',
                             'WBS-N09', 'WBS-N10', 'WBS-N15.06'],
        'run': 'PG1318-1342',
        'estimateAtGroupStartPp': {'low': .4, 'base': .8, 'high': 1.5},
        'estimateFrozenAt': '0380 allocation corrected by0381; not recharged',
        'attemptResult': 'LIMITED_PASS', 'workCategory': 'NATIVE_CONNECTION',
        'technicalStagesGross': 5, 'technicalStagesReopen': 0,
        'technicalStagesNet': 5, 'formalRunDelta': 0, 'wholeLeafDelta': 0,
        'failureIds': ['BUG1077', 'BUG1078', 'BUG1079', 'BUG1080'],
        'retryCause': 'physical schema14vs17; old composed stage release; bare helper name; uppercase public run',
        'actualPaths': ['genuineRoot1477.543157s', 'fullcurrent capture',
                        'ownedreverse stop34.447439s', 'independent fullpost',
                        'current eightnative byte-qualified'],
        'sourceEvidenceRefs': ['evidence/01_PT/018_NK-OPS-001/646_PG1318_1342_当source真正Root停止native仕様結果.md'],
        'remainingCounters': {'line': 924, 'method': 178, 'class': 12, 'branch': 724},
        'unaccepted': ['default export/closing/Inspector', 'business faults/replay',
                       'CHR QA051 final', 'global451 four100 trace handoff'],
        'quotaAfter': {'usedPercent': 28, 'remainingPercent': 72,
                       'resetsAt': 1792229056, 'windowDurationMins': 10080,
                       'secondary': None, 'fetchedAtJST': '2026-10-11T09:19:47+09:00'},
        'tokenMeasurementIds': ['f9f02e2233a2347000b60a61e555b1afc472eb97dceeb061be51d096bc65d07b'],
        'tokenTotals': {'N': None, 'T': None},
        'nextCommand': 'Inspect BootstrapAdminMain/pg986/WBS criteria; freeze estimate and currentguard before new-only action',
    }))
