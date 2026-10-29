"""Read original public manifests only. Counts are technical/source-local, never completion rate."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import snapshot_program_qualified_v2 as cfg

OUT = data.BASE/'PG13956-used35-periodic-original-manifest-audit-v1'
SOURCE = cfg.SOURCE
POSTS = [
    ('PG13844-snapshot-program-whole-post-v1','1765e226fef6761d6d975a535300e709c09f81e713e83974a567d309f671c113',23,3),
    ('PG13856-startup-proof-whole-eight-post-v1','fe04b2400b076efae9bf85b326be38bca7b15e215a7cae77c7e90c59d49c5e07',8,1),
    ('PG13865-broker-config-whole-four-post-v2','e377f82f0cbbb72499431a532d9538614f98f3fdd9b7f441d2e9308bdc3b0822',4,1),
    ('PG13874-release-approval-whole-eight-post-v1','b2c9af63478b1fab703c9e4db791b302da772b000807dceba4293437cec34ba0',8,1),
    ('PG13884-web-runtime-whole-two-post-v1','c07b6aaa6e9243ed10521070a9b371e2a8aa627b8477ab444ac63f10fa6e159a',2,1),
    ('PG13894-live-intent-fence-whole-six-post-v1','837db6b5e9152aa8d7a150646fe651b96d23f81293c20f43c214235210dc8037',6,2),
    ('PG13906-morning-data-envelopes-whole-twenty-post-v1','69271181be0bba1e4420e3e509bece74a7d2d0bbe520defc7b33b1911a1e1e7f',20,3),
    ('PG13914-morning-completion-boundaries-whole-thirteen-post-v1','9b93d9d78d143076d418c91413c2cec62d02ad6f3101a211839e206874991a68',13,3),
    ('PG13923-api-web-terminal-stop-whole-eleven-post-v2','cecea1c5dd6053fc0acd49d2b8888ebde308a7acefff40f9a690b8420544ad28',11,3),
    ('PG13930-root-bootstrap-cleanup-whole-sixteen-post-v1','fd67423447597324d351996ef0a28546cbcf758e49abf814e8a1b8fd3765c00e',16,3),
    ('PG13938-morning-backup-handoff-whole-eight-post-v1','25998c628fd9d51131c98f791b00165a892095fc476166bbd1896c1f3bf85b9c',8,2),
]
FULL_PROGRAMS = [
    (0,'dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot'),
    (1,'dev/codex/schubert/nk/bootstrap/StartupProofFrame'),
    (3,'dev/codex/schubert/nk/bootstrap/ReleaseApproval'),
    (6,'dev/codex/schubert/nk/batch/file/MorningPrestartEvidence'),
    (6,'dev/codex/schubert/nk/batch/file/MorningCompletionEvidence'),
    (8,'dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop'),
    (9,'dev/codex/schubert/nk/batch/file/CleanupPreflight'),
    (10,'dev/codex/schubert/nk/batch/file/MorningBackupPreparation'),
    (10,'dev/codex/schubert/nk/batch/file/MorningBackupCompletion'),
]

def quota_summary(before, after, threshold):
    if type(threshold) is not int or threshold != 35:
        raise ValueError('threshold is a trigger, not a quota observation')
    if any(type(v.get(k)) is not int for v in (before,after) for k in ('usedPercent','resetsAt')):
        raise ValueError('typed actual observation required')
    same = before['resetsAt'] == after['resetsAt']
    return dict(thresholdUsedPercent=threshold,before=before,after=after,sameWindow=same,
        observedSharedPp=after['usedPercent']-before['usedPercent'] if same else None,
        dedicatedPgptPp=None,pmoPp=None,N=None,T=None)

def main():
    invocation = capture(__file__);assert not OUT.exists()
    normal,normal_pin = cfg.normal();assert normal['source'] == SOURCE
    references = [];cases = set();current = []
    for directory,pin,tests,suites in POSTS:
        value = data.read_checked(data.BASE/directory/'manifest.json',pin)
        assert value['source'] == SOURCE and value['actualExit'] == value['failures'] == value['errors'] == value['skipped'] == 0
        assert value['tests'] == tests and value['suites'] == suites and value['singleSession'] is True
        assert value['whole451Accepted'] is value['formalUpdated'] is False and value['newAccepted'] == 0 and value['effortPercent'] is None
        actual = {(r['classname'],r['name']) for r in value['cases']}
        assert len(actual) == tests and not cases&actual;cases |= actual
        references.append(dict(path=str((data.BASE/directory/'manifest.json').relative_to(data.ROOT)),sha256=pin,source=SOURCE,methods=tests,suites=suites,coverageGateExit=value['coverageGateExit']))
        current.append(value)
    assert len(cases) == 119 and sum(v['suites'] for v in current) == 23
    new_cases = [c for c in cases if c[1]=='normalExitCodeIsLiteralOnlyAfterNormalMainCode'];assert len(new_cases) == 1
    old = data.read_checked(data.BASE/'PG13806-inspector-snapshot-whole-nine-post-v1/manifest.json','d0bbaf6462a0f1a3d277913436ef62f6922f15f6b43922a74eefc52673cb0591')
    assert old['source'] == '17ab52b253282ce45016f0586c0167a22029fd8c' and old['actualExit'] == 0 and old['tests'] == 9 and old['suites'] == 1
    assert len({(r['classname'],r['name']) for r in old['cases']}&cases) == 9
    programs = []
    for index,base in FULL_PROGRAMS:
        value = current[index]
        rows = {name:r for name,r in value['executable'].items() if name==base or name.startswith(base+'$')}
        assert rows and base in rows
        closure_key = 'completeSourceUnitClosure'
        closure = value[closure_key]
        declared = {name for name in closure if name==base or name.startswith(base+'$')}
        metadata = set(value['naturalZeroInterfaceMetadata'])
        assert set(rows)|{name for name in metadata if name in declared} == declared
        totals = {kind:dict(covered=sum(r['counters'][kind]['covered'] for r in rows.values()),missed=sum(r['counters'][kind]['missed'] for r in rows.values())) for kind in ['LINE','METHOD','CLASS','BRANCH']}
        assert all(v['missed']==0 and v['covered']>0 for v in totals.values())
        programs.append(dict(source=SOURCE,sourceUnit=base,postManifest=references[index],executablePhysical=len(rows),completeSourceClosure=sorted(declared),totalsFromOneOriginalExecOnly=totals))
    assert len(programs) == 9 and sum(r['executablePhysical'] for r in programs) == 12
    check = current[7]['executable']['dev/codex/schubert/nk/batch/file/MorningCompletionChecks']['counters']
    assert check == {'LINE':dict(covered=14,missed=0),'METHOD':dict(covered=5,missed=0),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=0,missed=0)}
    trace = data.read_checked(data.BASE/'PG13950-web-startup-resource-seven-trace-post-v1/manifest.json','c516af9f9df91e63da6a2e50e22fe06719ae08db52b80bb3e42758f66a30e195')
    assert trace['sourceDerivedRaw'] == 6247 and trace['joinedContextWarnings'] == 3401 and trace['currentWholeJoinPending'] == 2540 and trace['noCurrentReference'] == 2846
    events_path = data.ROOT.parent/'PMO/pgpt-execution-metrics/events.jsonl'
    lines = events_path.read_text().splitlines();events = [json.loads(line) for line in lines]
    baseline = next(v for v in events if v['eventId']=='PGPT-20261008-2900')
    start = next(v for v in events if v['eventId']=='PGPT-20261008-2929')
    correction = next(v for v in events if v['eventId']=='PGPT-20261008-2930')
    q = quota_summary(baseline['quotaAfter'],start['freshQuota']['primary'],35)
    assert q['observedSharedPp'] == 6 and q['after']['usedPercent'] == 36
    assert correction['correctionForEventId'] == start['eventId'] and correction['observedSharedPp'] == q['observedSharedPp']
    negatives = []
    for label,change in [('wrong-delta',lambda v:v.update(observedSharedPp=5)),('dedicated-zero',lambda v:v.update(dedicatedPgptPp=0)),('token-estimate',lambda v:v.update(N=1)),('threshold-as-actual',lambda v:v['after'].update(usedPercent=35)),('boolean-quota',lambda v:v['after'].update(usedPercent=True))]:
        bad = copy.deepcopy(q);change(bad)
        assert json.dumps(bad,sort_keys=True) != json.dumps(q,sort_keys=True);negatives.append(label)
    later = dict(start['freshQuota']['primary'],resetsAt=start['freshQuota']['primary']['resetsAt']+1)
    assert quota_summary(baseline['quotaAfter'],later,35)['observedSharedPp'] is None;negatives.append('different-window-no-delta')
    retained_events = {}
    for identifier in ['PGPT-20261008-2900','PGPT-20261008-2929','PGPT-20261008-2930']:
        line, = [line for line in lines if json.loads(line)['eventId']==identifier];retained_events[identifier] = data.sha(line.encode())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=normal_pin,
        postReferences=references,currentSourceQualifiedMethodsReferenced=119,currentSourceSuiteReferences=23,newFunctionalMethodIds=1,existingMethodsRequalified=118,
        historicalSourceMethodsReferencedSeparately=9,historicalSource=old['source'],crossSourceSameMethodIdentities=9,sourceDomainsMerged=False,
        fullSourceProgramMeasurements=programs,fullSourceProgramFour100=9,fullSourceExecutablePhysicalFour100=12,additionalCompleteChecksSourceNaturalZeroBranch=check,
        otherNestedClassMeasurementsOnly=['CompletionProgress','CompletionPhase','ApiTerminalCapture$Owner','WebTerminalCapture$Owner'],
        retainedGaps=['WebRuntimeExecution close/retention','BackupUnitStartClient partial and four unmeasured executable members','MorningStartupLaunchOwner unmeasured parent','ApiTerminalCapture native factory','WebTerminalCapture native factory','RootServiceAdmissionScope native overload','BootstrapAdminMain actual branches'],
        brokerConfigurationCoverage=None,brokerConfigurationApplicability='NON_EXECUTABLE_XML_NOT_JAVA_EXCLUSION',
        baselineEvent=baseline['eventId'],reviewStartEvent=start['eventId'],correctionEvent=correction['eventId'],quotaObservation=q,eventLineHashes=retained_events,quotaMetadataNegativeProfiles=negatives,
        staticRawBefore=6247,staticRawAfter=6247,priorCorrectionsBefore=3194,priorCorrectionsAfter=3194,currentReferenceBefore=3394,currentReferenceAfter=3401,unreferencedBefore=2853,unreferencedAfter=2846,
        mainSourceChangedFiles=0,testSourceChangedFiles=1,testChange='One new normal-exit boundary method and shared literal alias; initial candidate23582 PMD duplicate warning fixed in0061 before original PT.',
        productFailuresInReferencedRuns=0,toolBodyFailures=[dict(run='PG13922',entrySha256='5551ed6b5002457d9bb5396756697e50ac7669682db512bf9f9846b01162f30b',actualExit=1,repairedBy='PG13923',bug='BUG-2082')],
        otherPreservedRework=['BUG2080 initial candidate PMD duplicate','BUG2081 quota document erratum','BUG2083 start-description threshold/actual erratum','PG13820/13864 prebody lint','PG13894 draft replacement expansion','PG13906 draft parenthesis','Exact-save absolute-name guard and event-end display TypeError; no duplicate PT/events'],
        originalEstimatesRewritten=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedCriteria=17,totalCriteria=190,effortPercent=None,
        actualExternalPathDelta=0,wholeClosureStagnation=True,assessment='TECHNICAL_GAINS_PROVEN_NOT_ON_TRACK_FOR_WHOLE_CLOSURE_UNCALIBRATED_COST',
        nextPriority='Remaining15 Main resource contexts and their precise ownership/exit contracts; register actual PG defect before fix. Preflight-safe RootScope6/ParentGuard6 remain unexecuted; NoPrior helper chain unresolved. Do not replay successful tests or actual held operations.',
        productTestsExecutedByThisAudit=0,coverageExecReanalyzed=False,oldCoverageTransferred=False,globalCoverageUnion=False,actualVmActions=0,actualDatabaseActions=0,nativeQualification=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
    print(json.dumps(dict(currentSourceMethods=119,newMethodIds=1,fullSourcePrograms=9,fullSourcePhysical=12,sharedObservedPp=q['observedSharedPp'],dedicatedCost=None,newAccepted=0)))

if __name__ == '__main__':main()
