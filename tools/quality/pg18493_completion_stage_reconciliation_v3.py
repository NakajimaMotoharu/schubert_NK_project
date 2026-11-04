"""Read only pinned public planning metadata; emit drafts, not PT or acceptance results.

The caller persists stdout with apply_patch. No product loading, raw log access,
discovery, process enumeration, DB/server action or historical run replay.
"""
import collections
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT.parent / 'PMO/hourly-monitor/completion-execution-kit-20261102'
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
DESIGN = '7147c428bb9d619d88139947294bc3e8d95c4b62'
HELD = {'tools/quality/architecture/SnapshotKeyCloseWitness.java', 'tools/quality/pg9892_snapshot_key_close_witness.py'}


def digest(content):
    return hashlib.sha256(content).hexdigest()


def main():
    pins = []

    def read(path, pin=None):
        assert str(path.relative_to(ROOT)) not in HELD if path.is_relative_to(ROOT) else path.is_relative_to(KIT)
        content = path.read_bytes()
        actual = digest(content)
        if pin is not None:
            assert pin == actual, str(path)
        pins.append({'path': str(path), 'sha256': actual})
        return json.loads(content)

    seed = read(KIT / 'evidence/remaining-work-seed.json')
    assert seed['source'] == SOURCE
    wbs = read(ROOT / 'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json', seed['sourcesPinned'][0]['sha256'])
    costs = read(ROOT / 'documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json', seed['sourcesPinned'][1]['sha256'])
    inventory = read(ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json', seed['sourcesPinned'][2]['sha256'])
    assert len(inventory['artifacts']) == 941, 'original logical inventory unchanged'
    read(ROOT / 'documents/400_PGPT/470_PMO/486_WBS現行実績.json')
    read(ROOT / 'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json')
    descriptor = read(BASE / 'PG15918-g13-current-static-descriptor-v1/artifacts.json', 'af8f4674a9ac737153b5e38221ef3bc0c2a1d1bdaf0fd256440f1b83cebed79c')
    registry = read(BASE / 'PG18454-current3008-latest270-owner-correction-v1/manifest.json', '0662e8e2912f48ef1d5619199a22edd1bbef34dcb45c7ef69b278936b7a40d51')
    original = read(BASE / 'PG15950-g13-current-test-declaration-inventory-v1/manifest.json', '0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139')
    read(BASE / 'PG15952-g13-current-test-declaration-post-v1/manifest.json', 'ae9eba3351785a9c5cf15bd8231b9622b8fd6ffe99581e6aa23cc6f546e37945')
    declarations = read(BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', original['files']['exact-ordinary-bindings.json'])
    assert original['source'] == registry['source'] == SOURCE
    assert not subprocess.check_output(['git', 'diff', '--name-only', SOURCE, 'HEAD', '--', 'src', 'program/characterization'], cwd=ROOT)
    tasks = {t['id']: t for t in wbs['tasks']}
    tasks.update({t['id']: t for t in costs['sharedBudgets']})
    tasks.update({t['id']: t for t in costs['children']})
    artifacts = {r['path']: r for r in descriptor}
    case_keys = {(r['classname'], r['name']) for r in registry['cases']}
    assert len(case_keys) == 3008 and len(declarations) == 5786
    ordinary = []
    for d in declarations:
        key = (d['className'], d['method'])
        found = key in case_keys
        owner = registry['owners'].get(d['path'], {})
        ordinary.append({'id': '#'.join(key), 'path': d['path'], 'sha256': d['sourceSha256'], 'span': [d['sourceStartLine'], d['sourceEndLine']],
            'ownerCandidate': owner.get('canonicalOwner'), 'costOwnerCandidate': owner.get('canonicalCostOwner'),
            'decision': 'RETAIN_EXISTING_CURRENT_CASE_REFERENCE_NOT_NEW_PASS' if found else 'CURRENT_EXECUTION_REFERENCE_MISSING_RECONCILIATION_REQUIRED',
            'independentOracleReview': 'NOT_PERFORMED_BY_METADATA_JOIN', 'requiredNewExecutions': None,
            'refusalAssigned': False, 'newAcceptance': False})
    assert sum(r['decision'].startswith('RETAIN_') for r in ordinary) == 2806
    assert len({r['id'] for r in ordinary}) == 5786
    sources = []
    for r in seed['sourceEvidenceRows']:
        a = artifacts[r['path']]
        assert a['owner'] == r['owner'] and r['path'] not in HELD
        status = r['evidenceStatus']
        key = r['path'].split('/src/main/java/')[-1].removesuffix('.java')
        u = registry['fullSourceUnits'].get(key)
        if status != 'NOT_IN_CURRENT_MEASUREMENT_REGISTRY':
            assert u is not None
        if status == 'PARTIAL':
            decision = 'RETAIN_MEASURED_SUBSET_AND_PLAN_MISSED_CONTRACTS'
        elif status == 'NOT_IN_CURRENT_MEASUREMENT_REGISTRY':
            decision = 'SEPARATE_COMPARISON_MODULE_REQUALIFICATION_AND_QA051_SEMANTICS' if r['module'] == 'characterization' else 'NO_CURRENT_MEASUREMENT_ENTRY_RECONCILE_ORIGINAL_PROOF_BEFORE_NEW_TEST'
        else:
            decision = 'REUSE_COUNTER_SUBPROOF_ONLY_CONTRACT_ORACLE_AND_POSTCONDITIONS_STILL_REQUIRED'
        sources.append(dict(r, sha256=a['sha256'], decision=decision,
            qualifiedUnitProof=None if u is None else {k: u.get(k) for k in ['post','postSha256','sessionIdentity','execSha256','physical']},
            requiredNewExecutions=None, semanticContractSatisfied=None, newAcceptance=False))
    assert len(sources) == 932 and len({r['path'] for r in sources}) == 932
    def family(leaf):
        i, k = leaf['id'], leaf['kind']
        if k == 'RESERVE': return 'RESERVE'
        if k in ('VM_CONNECTION','CHR','FINAL_GATE','SHARED_COST','FOUNDATION','CONFIG'): return k
        if i.startswith(('WBS-P001','WBS-P002')): return 'PROTOCOL_CODEC_TRANSPORT'
        if i.startswith(('WBS-P003','WBS-P004')): return 'STORAGE_TRANSACTION_RESOURCE'
        if i.startswith(('WBS-P005','WBS-P006')): return 'JMS_INBOX_OUTBOX_AUDIT'
        if i.startswith(('WBS-P007','WBS-P010')): return 'AUTH_ADMIN_SQL'
        if i.startswith(('WBS-P008','WBS-P009')): return 'SCENARIO_MEDIA'
        if i.startswith(('WBS-P011','WBS-P012','WBS-P013','WBS-P014')): return 'QUESTION_JOB_NOTIFICATION'
        if i.startswith(('WBS-P015','WBS-P016')): return 'WEB_SESSION_FORMS_AND_VIEWS'
        if i.startswith('WBS-P017'): return 'BATCH_BACKUP_CLEANUP_BROKER'
        if i.startswith('WBS-P018'): return 'STARTUP_OWNERSHIP_NATIVE'
        if i.startswith('WBS-P019'): return 'MIGRATION_ROLLBACK'
        if i.startswith('WBS-P020'): return 'COMPARISON_ADAPTER_QA051'
        raise ValueError(i)
    packages = []
    holds = []
    for leaf in seed['remainingLeafRows']:
        t = tasks[leaf['id']]
        parent = tasks.get(leaf['parent'], {})
        evidence_plan = t.get('evidencePlan', parent.get('evidencePlan', {}))
        i = leaf['id']
        resolved = leaf['kind'] == 'RESERVE'
        needs_operating_state = leaf['kind'] in ('VM_CONNECTION','CHR')
        own = leaf['directCurrentArtifactEvidence']
        current_paths = [p for paths in own.values() for p in paths]
        direct = [r for r in sources if r['path'] in current_paths]
        status = 'RESERVE_NOT_EARNED_WORK' if resolved else ('START_PREREQUISITES_NOT_PROVEN' if needs_operating_state else 'PARTIAL_PROOF_REUSE_CONTRACT_REVIEW_OPEN')
        hold_ids = []
        if needs_operating_state or leaf['kind'] == 'FINAL_GATE':
            h = 'H-' + i.removeprefix('WBS-')
            hold_ids.append(h)
            holds.append({'id': h, 'operation': leaf['title'], 'target': current_paths or [i + ' original criteria/evidencePlan'], 'source': SOURCE,
                'types': ['OWNERSHIP_OR_CURRENT_STATE','TECHNICAL_OR_QUALITY'] if needs_operating_state else ['TECHNICAL_OR_QUALITY'],
                'basis': ['456/460 saved checkpoint: no current VM/DB/job observation', leaf['criteria']],
                'missingCondition': 'Bind exact target/fixture/current boot, source, run and owner to original terminal plus independent post; establish operation independence before any actual command' if needs_operating_state else 'Join all stated per-criterion proofs and preceding leaf exits; partial/static counters do not close this gate',
                'resolver': 'PGPT execution owner; platform/user only if concrete authority gap remains', 'resolutionDueJST': None,
                'dueRule': 'BEFORE_THIS_OPERATION_NOT_ASSUMED_WEEK', 'affectedCriteria': [c['id'] for c in leaf['criteria']],
                'independenceFromRefusedOperation': None, 'concreteRefusalAssigned': False, 'status': 'UNRESOLVED_NO_OPERATION_AUTHORIZATION'})
        steps = [{'id': i + '/reuse', 'input': {'ownedArtifactPaths': current_paths, 'candidateTestFiles': evidence_plan.get('candidateTestFiles', []), 'specDirectory': evidence_plan.get('specDirectory'), 'proofSubset': {k: len(v) for k,v in own.items()}},
            'expected': 'Trace these exact requirements and named contract to independent TestID/oracle/source proof; reuse only individually justified subset; do not repeat a success just to count it', 'status': 'OPEN_NOT_SEMANTICALLY_VERIFIED'}]
        steps.extend({'id': i + '/criterion/' + c['id'].split(':')[-1], 'expected': c['expected'], 'independentOracle': c['evidenceType'], 'evidenceRequired': ['same-source/byte proof','actual command and terminal','applicable independent expected values','postconditions and scope hash'], 'status': 'OPEN_NOT_INFERRED_FROM_PATH_OR_COUNTER'} for c in leaf['criteria'])
        packages.append({'packageId': i, 'family': family(leaf), 'title': leaf['title'], 'kind': leaf['kind'], 'parentReferenceOnly': leaf['parent'],
            'source': SOURCE, 'designCommit': DESIGN, 'requirements': t.get('requirementIds', parent.get('requirementIds', [])), 'ss': t.get('ss', parent.get('ss', [])),
            'designFiles': evidence_plan.get('designFiles', []), 'costOwner': i, 'commonImplementationCostOwner': sorted({r['owner'] for r in direct}),
            'sharedCostsChargedHere': False, 'existingProofCountsByState': {k: len(v) for k,v in own.items()},
            'remainingConcreteOperations': leaf['remainingActions'], 'definitionOfDone': steps, 'startDependencies': leaf['dependencies'], 'exitDependencies': leaf['externalDependencies'],
            'holdIds': hold_ids, 'capturedGroups': leaf['capturedGroupCount'], 'noCapturedGroupIsNotNoWork': leaf['capturedGroupCount'] == 0,
            'historicalAcceptanceCurrentlyTransferred': False, 'initialEstimatePpPreserved': leaf['initialEstimatePpPreserved'], 'oldV5ReferenceNotRepriced': leaf['oldV5ReferencePpNotCurrentEstimate'],
            'estimatedRemainingPp': {'low': None,'base': None,'high': None}, 'estimateBasis': 'NO_COMPARABLE_CLOSED_FULL_CYCLE_YET_NOT_ZERO', 'status': status, 'newAccepted': False})
    assert len(packages) == 252 and len({r['packageId'] for r in packages}) == 252
    kinds = collections.Counter(r['kind'] for r in packages)
    assert kinds['RESERVE'] == 1 and kinds['VM_CONNECTION'] == 29 and kinds['CHR'] == 24
    family_rows = []
    for f in sorted({p['family'] for p in packages}):
        group = [p for p in packages if p['family'] == f]
        owners = {p['packageId'] for p in group} | {p['parentReferenceOnly'] for p in group}
        owned_sources = [r for r in sources if r['owner'] in owners]
        family_rows.append({'id': f, 'leafIds': [p['packageId'] for p in group], 'quantity': len(group), 'unit': 'EXPLICIT_LEAF_CONTRACT_NOT_UNIFORM_COST_UNIT',
            'currentSourceCount': len(owned_sources), 'partialPaths': [r['path'] for r in owned_sources if r['evidenceStatus']=='PARTIAL'],
            'unmeasuredPaths': [r['path'] for r in owned_sources if r['evidenceStatus']=='NOT_IN_CURRENT_MEASUREMENT_REGISTRY'],
            'closure': 'All named leaf criteria/own expected values and required postconditions; retain parent exits and shared costs once',
            'estimatedPp': {'low': None,'base': None,'high': None}, 'reason': 'Need comparable full-cycle contract and permission/owner resolution; old ratios and source counts are not unit prices'})
    reuse_counts = collections.Counter(r['evidenceStatus'] for r in sources)
    reference = [t for t in wbs['tasks'] if t['id'] == 'WBS-P019-02']
    assert len(reference) == 1 and reference[0]['remainingCost']['countsInTotal'] is False
    outputs = {
        'remaining-work-packages.json': {'scope': '251_REAL_LEAVES_PLUS_RESERVE_NO_LEAF_ACCEPTANCE_ADDED','source': SOURCE,'designCommit': DESIGN,'packages': packages,'referenceOnlyExcludedFromCost': reference},
        'source-reuse-matrix.json': {'source': SOURCE,'counts': dict(reuse_counts),'rows': sources,'semanticReviewComplete': False,'allUnmeasuredAssumedUntested': False},
        'ordinary-reuse-matrix.json': {'source': SOURCE,'ordinaryDeclarations':5786,'retainedCaseReferences':2806,'missingCurrentCaseReferences':2980,'newOrdinaryPasses':0,'nonApplicableOrDuplicateOrdinaryMethodsRemoved':0,'nonordinaryAnnotationSeparate':1,'allMissingAssumedUnexecuted':False,'semanticReviewComplete':False,'rows':ordinary},
        'common-cause-groups.json': {'groups':family_rows,'causeUnificationRules':['Freeze baseline plus old9982 plus latest13846 candidate registries before owner correction, and retain quality domain separately; do not reOPEN2->24->270 by inspecting one obsolete source only','For actual failures bind source/run/own acquisition and reverse release over all callers before fix; new BUG/YKT before corrective code','Inspect all SQL and transaction consumers for the specific confirmed cause, not every repository simply because it uses SQL','No root/DB name blacklist, no inferred refusal target; execute only specific independent approved operation'], 'groupBudgetsAuthorized':False},
        'hold-register.json': {'holds':holds,'globalHolds':[{'id':'H-REFUSAL-UNKNOWN','type':'REFUSAL_SCOPE_UNRESOLVED','operation':None,'basis':'QA053 original notification no longer exists;1975 nine PT have static review only; last successful read is not a refusal target','releaseCondition':'Concrete scope/authority resolution from original platform evidence, not probing; establish independent operation before use','resolutionDueJST':None,'globalBanOnAllDbOrSecurityTests':False},{'id':'H-AKO','type':'EXTERNAL_DEPENDENCY','target':'192.168.1.133/ako','operation':'Any credential read/connect/transfer/server control','basis':'Latest direct user: stopped; no access','releaseCondition':'Further direct authority and current ownership authentication','resolutionDueJST':None}], 'qa051Decision':'APPROVED_MAIN7147_NOT_WAITING_FOR_USER; branch/oracle/runtime work open','qa053Inquiry':'ANSWERED_UNAVAILABLE_NO_REASK'},
        'provisional-estimate.json': {'status':'PLAN_NOT_VALIDATED','components':family_rows,'fullCycleHistoricalPoolUsedOnce':seed['reconstructedSharedCostEvidence']['reconstructedFullAcceptedEarlyBasket'],'savedObservationEvidence':seed['reconstructedSharedCostEvidence'],'sharedExamples':seed['measurementAudit']['sharedExamplesNotNewCosts'],'overlapHandling':'Do not sum1128 enclosing groups or479 interval keys; early0->8 pool is one mixed reusable-evidence basket, not a price for unresolved paths','futureRemainingPp':{'low':None,'base':None,'high':None},'unpricedCriticalFamilies':['STARTUP_OWNERSHIP_NATIVE','VM_CONNECTION','CHR','FINAL_GATE'],'withdrawn630PpDec23Used':False,'old58475Rescaled':False},
        'reconciliation-summary.json': {'source':SOURCE,'designCommit':DESIGN,'inputPins':pins,'realLeaves':251,'reserve':1,'sourceRows':932,'measuredRows':650,'partialRows':80,'unmeasuredRows':282,'missingOrdinaryReferences':2980,'ordinaryExisting':2806,'uncapturedRealLeaves':sum(p['capturedGroups']==0 and p['kind']!='RESERVE' for p in packages),'newAccepted':0,'semanticClassificationOfAllGapsCompleted':False,'phaseCompletionRate':None,'method':'PINNED_METADATA_RECONCILIATION_NOT_SEMANTIC_ACCEPTANCE_OR_PT','rawPrivateOrHeldFilesRead':False,'productTestsExecuted':False}
    }
    return outputs


if __name__ == '__main__':
    values = main()
    print(json.dumps({'outputSha256': {name: digest((json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()) for name, value in values.items()}, 'logicalInventoryInvariant': 941, 'productTestsExecuted': 0}, sort_keys=True))
