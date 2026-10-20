"""Mechanical current943 trace beside immutable historical941/17; no runtime or PT operation."""
import argparse
import copy
import json
import os
import subprocess
import wbs_progress_audit as audit
import wbs_candidate_trace as trace
from pg3282_wbs_current_source_apply import rewrite_root, replace_public, group_coverage
from pg4948_current_trace_public import owner_measurement
from pg6104_sourcefile_line_projection import projection
from pg6082_web_factory_qualification import SOURCE

ROOT = audit.ROOT
PMO = ROOT/'documents/400_PGPT/470_PMO'
BASE = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
W = ROOT.parent/'pgpt-runs/PG379'
OUT = W/'pg6102-current-support-trace-v1'
PUBLIC = BASE/'PG6102-current-host-measurement-v1'
NAMES = ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json')
QSHA = '76d222eef92096c6b9fb84c73fb978836a441ec52ced506f0bdc3ece3d4f183a'
CSHA = '0ce3390f37aeabad4ecfef5f45a0ab7af6d8fb2f77d34ab955156ae5eaac9c90'
require = trace.require
sha = trace.sha


def read_qualified():
    qp = BASE/'PG6088-current3985-cases/qualification.json'; cp = qp.with_name('cases.json')
    require(sha(qp.read_bytes()) == QSHA and sha(cp.read_bytes()) == CSHA, 'genuine original current3985 qualification/cases')
    q = json.loads(qp.read_bytes())
    require(q['actualExit'] == q['FESFlakyNotRun'] == q['staticSixModules'] == 0
            and q['productionSource'] == SOURCE and (q['tests'],q['suites'],q['mainClasses']) == (3985,595,1667)
            and q['currentOriginalXmlQualified'] is True, 'actual same-source host-only measurement')
    return qp, q


def measurement():
    qp, q = read_qualified()
    historical = audit.read_json(PMO/NAMES[2])['source']
    counters = {m:{k:q['modules'][m]['coverage'][k] for k in trace.COUNTERS} for m in sorted(q['modules'])}
    return dict(actualExit=0, productionSource=SOURCE, run='PG6088-six-v1', tests=3985, suites=595, mainClasses=1667,
        FES=0, oldSourceNativeImported=False, nativeQualified=False, acceptedLeafDelta=0,
        formalAccepted=False, effortPercent=None, F03Accepted=False,
        measurementKind='CURRENT_HOST_ONLY_ORIGINAL_WHOLE',
        canonicalAcceptance=dict(source=historical, automaticSourceRebinding=False, historicalAcceptedTasks=17,
                                 formalUnchanged='PT-WEB-20260925-24/1964PT/53scope'),
        originalQualification=dict(path=qp.relative_to(ROOT).as_posix(), sha256=QSHA, casesSha256=CSHA),
        coverageRoot=q['coverageRoot'], modules=[dict(module=m, coverageXmlSha256=q['modules'][m]['coverageXmlSha256']) for m in sorted(q['modules'])],
        moduleCounters=counters, remaining={k:sum(v[k]['missed'] for v in counters.values()) for k in trace.COUNTERS},
        runtimeVerifiedRows=[], startUTC=q['startUTC'], endUTC=q['endUTC'], os=q['os'],
        command=q['command'], vmActions=0, testsExecutedByTrace=0, historicalNativeNotReauthenticated=True)


def publish():
    value = measurement(); os.umask(0o077); PUBLIC.mkdir()
    with (PUBLIC/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifest=PUBLIC.relative_to(ROOT).as_posix()+'/manifest.json',
                         sha256=sha((PUBLIC/'manifest.json').read_bytes()), remaining=value['remaining'], nativeQualified=False)))


def candidates(texts, before_head):
    inventory, snapshot = [json.loads(texts[n],object_pairs_hook=audit.unique_object) for n in NAMES[2:]]
    qpath, _ = read_qualified(); require(qpath.exists(), 'original proof retained')
    measured_path = PUBLIC/'manifest.json'; measured = measurement()
    require(json.loads(measured_path.read_bytes()) == measured, 'unchanged explicit original host-only measurement')
    old = inventory['artifacts']; previous = inventory['currentPhysicalCandidate']
    require(previous['version'] == 1 and len(old) == len(previous['artifacts']) == 941, 'one initial941-to943 update,not overwriting newer trace')
    prior_blob = trace.git_artifacts(before_head,['documents/400_PGPT/470_PMO/'+NAMES[2]])['documents/400_PGPT/470_PMO/'+NAMES[2]]
    require(prior_blob == texts[NAMES[2]].encode(), 'previous current candidate preserved by immutable metadata Git source')
    paths = [trace.MOVES.get(a['path'],a['path']) for a in old]+sorted(trace.SUPPORT)
    current = trace.git_artifacts(SOURCE,paths); artifacts = []
    for prior in old:
        path = trace.MOVES.get(prior['path'],prior['path'])
        value = {k:prior[k] for k in ('kind','owner','costOwner')}
        value.update(path=path,historicalPath=prior['path'],sha256=sha(current[path]),acceptance='UNASSESSED')
        if value['kind'] == 'JAVA':
            value.update(module=path.split('/')[1].removeprefix('schubert-nk-'), **{'class':path.split('/src/main/java/')[1][:-5]})
        artifacts.append(value)
    for path,(owner,origin) in sorted(trace.SUPPORT.items()):
        artifacts.append(dict(path=path,historicalPath=None,kind='JAVA',owner=owner,costOwner=owner,
            sha256=sha(current[path]),acceptance='UNASSESSED',module='protocol',
            **{'class':path.split('/src/main/java/')[1][:-5]},supportingExistingLeaf=owner,
            originCommit=origin,implementationSupportOnly=True,additionalBudgetPp=0))
    candidate = dict(version=2,source=SOURCE,historicalSource=inventory['source'],
        historicalDescriptorSha256=trace.descriptor_digest(old),relocations=trace.MOVES,
        design=previous['design'],measurement=dict(path=measured_path.relative_to(ROOT).as_posix(),sha256=sha(measured_path.read_bytes())),
        artifacts=artifacts,acceptedLeafDelta=0,scopeChanged=False,logicalScopeChanged=False,
        physicalScopeDelta=dict(addedSupport=sorted(trace.SUPPORT),removed=[]),effortPercent=None)
    proposal = copy.deepcopy(inventory); proposal['currentPhysicalCandidate'] = candidate
    observed = trace.verify_candidate(proposal)
    history = list(inventory.get('currentPhysicalCandidateHistory',[]))
    history.append(dict(source=previous['source'],metadataSource=before_head,
        inventoryPath='documents/400_PGPT/470_PMO/'+NAMES[2],inventorySha256=sha(texts[NAMES[2]].encode()),
        candidateSha256=trace.descriptor_digest(previous),measurement=previous['measurement'],preservedNotImported=True))
    first = rewrite_root(texts[NAMES[2]],dict(currentPhysicalCandidate=candidate,currentPhysicalCandidateHistory=history,
        currentCandidateAssessmentHead=before_head,
        artifactHashMeaning='Historical941/source/17acceptance are immutable. Current943 source870 host-only original3985 binds all current bytes and two explicit P005-03 implementation supports at zero additional budget. Old native/candidate success is not imported; counters do not grant runtime,acceptance or effort authority.'))
    second = rewrite_root(texts[NAMES[3]],dict(inventorySha256=sha(first.encode()),currentPhysicalCandidateMeasurement=observed,
        candidateInventoryMeaning='Historical941 descriptors/measurements/17acceptances unchanged;current943 source870 uses only actual original3985 host coverage. Physical support additions2,logical scope/fees unchanged. Native/global100/F03/formal pending;effortnull.'))
    # Root rewrite must not touch historical rows/counts/acceptance/cost.
    require(json.loads(first)['artifacts'] == inventory['artifacts'], 'historical artifact descriptor list unchanged')
    new_snapshot = json.loads(second)
    require(all(new_snapshot[k] == snapshot[k] for k in ('rows','counts','source','measurementRun','formal','wholeEffortCompletionRate')),
            'historical individual/measurement/formal fields unchanged')
    return {**texts,NAMES[2]:first,NAMES[3]:second}, observed


def stage():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT), 'clean committed trace operator/proof first')
    require(not subprocess.check_output(['git','diff',SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT), 'canonical Main/Test fixed')
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    texts = {n:(PMO/n).read_text() for n in NAMES}; proposed, observed = candidates(texts,head)
    os.umask(0o077); OUT.mkdir(mode=0o700)
    for n in NAMES:
        for prefix,value in (('before-',texts[n]),('candidate-',proposed[n])):
            with (OUT/(prefix+n)).open('x') as f:f.write(value)
    verified = audit.verify(master_path=OUT/('candidate-'+NAMES[0]),budget_path=OUT/('candidate-'+NAMES[1]),
                            inventory_path=OUT/('candidate-'+NAMES[2]),snapshot_path=OUT/('candidate-'+NAMES[3]))
    require(verified['acceptedTasks'] == 17 and verified['currentPhysicalCandidate'] == observed, 'actual candidate audit with historical17')
    result = dict(actualExit=0,source=SOURCE,before={n:sha(texts[n].encode()) for n in NAMES},
        after={n:sha(proposed[n].encode()) for n in NAMES},audit=verified,measurementSha256=sha((PUBLIC/'manifest.json').read_bytes()),
        acceptedLeafDelta=0,masterAndBudgetUnchanged=texts[NAMES[0]]==proposed[NAMES[0]] and texts[NAMES[1]]==proposed[NAMES[1]])
    with (OUT/'stage.safe.json').open('x') as f:json.dump(result,f,ensure_ascii=False,sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,staged=True,physicalArtifacts=observed['physicalArtifacts'],acceptedLeafDelta=0,stageSha256=sha((OUT/'stage.safe.json').read_bytes()))))


def apply():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT), 'clean committed metadata before applying exact staged pair')
    record = json.loads((OUT/'stage.safe.json').read_bytes())
    require(record['actualExit'] == 0 and record['source'] == SOURCE and record['masterAndBudgetUnchanged']
            and not (OUT/'apply-intent.safe.json').exists(), 'one staged metadata application only')
    require(sha((PUBLIC/'manifest.json').read_bytes()) == record['measurementSha256'], 'same committed measurement before metadata update')
    for n in NAMES:
        require(sha((PMO/n).read_bytes()) == record['before'][n]
                and sha((OUT/('candidate-'+n)).read_bytes()) == record['after'][n], 'before/candidate bytes unchanged')
    with (OUT/'apply-intent.safe.json').open('x') as f:
        json.dump(record,f,ensure_ascii=False,sort_keys=True); f.flush(); os.fsync(f.fileno())
    for n in NAMES[2:]:replace_public(PMO/n,(OUT/('candidate-'+n)).read_bytes())
    verified = audit.verify()
    require(verified['acceptedTasks'] == 17, 'historical17 retained after update')
    require(all(sha((PMO/n).read_bytes()) == record['before'][n] for n in NAMES[:2]), 'master/acceptance/cost untouched')
    with (OUT/'apply.safe.json').open('x') as f:
        json.dump(dict(actualExit=0,source=SOURCE,audit=verified,acceptedLeafDelta=0),f,ensure_ascii=False,sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,applied=True,currentArtifacts=verified['currentPhysicalCandidate']['physicalArtifacts'],acceptedLeafDelta=0)))


def report():
    staged = json.loads((OUT/'stage.safe.json').read_bytes()); applied = json.loads((OUT/'apply.safe.json').read_bytes())
    require(staged['actualExit'] == applied['actualExit'] == 0 and all(sha((PMO/n).read_bytes()) == staged['after'][n] for n in NAMES),
            'genuine stage/apply and all current metadata unchanged')
    inventory = audit.read_json(PMO/NAMES[2]); observed = trace.verify_candidate(inventory)
    require(observed == applied['audit']['currentPhysicalCandidate'], 'same actual applied current candidate observation')
    measured = json.loads((PUBLIC/'manifest.json').read_bytes())
    owners = owner_measurement(inventory['currentPhysicalCandidate']['artifacts'],group_coverage(measured))
    lines = projection(measured,inventory['currentPhysicalCandidate']['artifacts'],ROOT)
    require(all(owners['remaining'][k] == observed['remaining'][k] for k in ('METHOD','CLASS','BRANCH'))
            and lines['sourcefileLineTotals']['missed'] == observed['remaining']['LINE']
            and lines['classFamilyLineTotals']['missed'] == owners['remaining']['LINE'],
            'each counter compared in its actual domain;all missed class lines retained')
    owners['lineCounterDomain'] = 'SUM_OF_OWNED_CLASS_FAMILY_LINE_COUNTERS_NOT_MODULE_SOURCEFILE_LINES'
    value = dict(actualExit=0,productionSource=SOURCE,kind='CURRENT943_HOST_ONLY_TRACE_NOT_ACCEPTANCE',
        historicalArtifacts=941,currentArtifacts=943,physicalSupportAdditions=2,logicalScopeChanged=False,
        historicalAcceptedTasks=17,acceptedLeafDelta=0,formalAccepted=False,effortPercent=None,
        currentMeasurement=observed,currentJavaOwnerCounters=owners,sourcefileLineReconciliation=lines,
        measurementManifestSha256=sha((PUBLIC/'manifest.json').read_bytes()),
        beforeFileHashes=staged['before'],afterFileHashes=staged['after'],
        stageReceiptSha256=sha((OUT/'stage.safe.json').read_bytes()),applyReceiptSha256=sha((OUT/'apply.safe.json').read_bytes()),
        oldSourceNativeImported=False,nativeQualified=False,sourceChanges=0,testsExecuted=0,vmActions=0)
    public = BASE/'PG6102-current943-trace-v1'; public.mkdir()
    with (public/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha((public/'manifest.json').read_bytes()),javaOwners=owners['javaOwners'],
                         currentCounterCounts=owners['counts'],remaining=owners['remaining'],acceptedLeafDelta=0)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action',choices=['publish','stage','apply','report'])
    args = parser.parse_args(); {'publish':publish,'stage':stage,'apply':apply,'report':report}[args.action]()
