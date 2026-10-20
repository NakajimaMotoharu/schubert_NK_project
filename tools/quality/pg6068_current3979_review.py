"""Rebind606 strict reasons plus25 individually reviewed scopes to genuine current3979;no PT replay."""
import copy
import hashlib
import json
import os
import subprocess
import tarfile
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import SOURCE
from pg5910_storage_static_rebind import ordered_pairs
from pg5758_static_rebind import bind_one
from static_disposition_overlay import load
from pg6048_current_jdbc24_review import current_refs

QSHA = '4a411f7710e793e34204cc738d7882c69d500967b719c596c48687e195b84a5e'
CSHA = 'b4f4fb0d819b59fa971f8795793a9e5d061ef542c1a4d9c2cb3b4acfa6155c03'
OLD = '8c869d7cea21d587b859b3e72e3516d9d2deb5c8'


def selected_refs(prior, index):
    refs = []
    for ref in prior:
        values = [index.get((ref['className'], hashlib.sha256(n.encode()).hexdigest())) for n in (ref['method'], ref['method']+'()')]
        matches = [r for r in values if r is not None]
        if len(matches) != 1 or matches[0]['source'] != SOURCE or matches[0]['result'] != 'PASS_ORIGINAL_XML':
            raise ValueError('one actual current whole identity for each selected method')
        refs.append({k: matches[0][k] for k in ('testId', 'xmlSha256', 'class', 'caseNameSha256', 'source')})
    return refs


def reviewed_result():
    qp = BASE/'PG6060-current3979-cases/qualification.json'; cp = qp.with_name('cases.json')
    if (sha(qp), sha(cp)) != (QSHA, CSHA):
        raise ValueError('genuine current3979/594 qualification/cases')
    q = json.loads(qp.read_bytes()); cases = json.loads(cp.read_bytes())
    if q['productionSource'] != SOURCE or (q['tests'], q['suites'], q['mainClasses'], q['FESFlakyNotRun']) != (3979, 594, 1667, 0):
        raise ValueError('exact same current original run')
    sp = BASE/'PG6054-expiry-read-qualification-v1/manifest.json'; pp = W/'pg6054-expiry-read-qualification-v1/manifest.safe.json'
    if (sha(sp), sha(pp)) != ('9f1269de6b66c0be2467aab5de164e82553f03d33dc79f5212e410ff4f1daee9', '14128e3496c796aca15bb9bd8bc46d87a2662a34e8f412125d1b667ff029c885'):
        raise ValueError('original current all8511667/static1305 inputs')
    static = json.loads(pp.read_bytes()); raw = json.loads(pp.with_name('findings.safe.json').read_bytes())
    if (static['source'] != SOURCE or static['allSourceHashes'] != q['allSourceHashes'] or static['allPhysicalMainSha256'] != q['allPhysicalMainSha256']
            or static['pmdRawFindings'] != 1305 or static['pmdProcessingErrors'] != 0 or static['checkstyleFindings'] != 0):
        raise ValueError('actual whole and selected static source/class byte maps must equal')
    if static['pmdProcessingErrors'] or static['checkstyleFindings'] or static['originalSixSpotBugs']:
        raise ValueError('actual static conditions,no normalized nonzero')
    whole_input = W/'pg6066-original3979-artifacts-v1/input.safe.json'
    if sha(whole_input) != '5e5e939e0998dee105b7b9ecfad17a7719e9dffd5d4482d61374200a598428f7':
        raise ValueError('actual original whole input receipt')
    selected_inputs = {}
    with tarfile.open(W/'pg6052-expiry-combined-green-v1/source.tar') as tar:
        for member in tar:
            if member.isfile():
                selected_inputs[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    whole_inputs = json.loads(whole_input.read_bytes())['allSourceInputs']
    rule_files = {'tools/quality/static/'+name for name in ('README.md', 'checkstyle.xml', 'pmd.xml', 'pmd-record-1298.patch',
        'canaries/DynamicKeyRuleCanary.java', 'canaries/GateField.java', 'canaries/GateNegative.java',
        'canaries/GatePositive.java', 'canaries/GateRecord.java', 'canaries/OutboxCauseGraphCanary.java', 'canaries/UnsafeKeyRuleCanary.java')}
    if (len(whole_inputs) != 1887 or set(selected_inputs)-set(whole_inputs) != rule_files
            or any(selected_inputs.get(p) != h for p, h in whole_inputs.items())):
        raise ValueError('all1887 original build/Test/CHR inputs equal;only11 explicit static rules/materials are extra in selected archive')
    for path in rule_files:
        if hashlib.sha256(subprocess.check_output(['git', 'show', SOURCE+':'+path], cwd=ROOT)).hexdigest() != selected_inputs[path]:
            raise ValueError('each additional static rule/canary input equals canonical same source,not an omitted build input')
    index = {(r['class'], r['caseNameSha256']): r for r in cases}
    if len(index) != 3979 or any(r['xmlSha256'] != q['modules'][r['module']]['xmlHashes'][r['sourceXml']] for r in cases):
        raise ValueError('all actual unique source/run/XML identities')
    oldsha = '087cc73138dcb3f91f082510c9c2b6dc6a8f390e569a4cbaba1f6d75fccf3c4a'
    oldrows = load(BASE/'PG6048-current-jdbc24-v2/manifest.json', oldsha, OLD)
    oldq = BASE/'PG6040-current3976-cases/qualification.json'
    if sha(oldq) != '0d11101550922d207fec3ba3f1d2fa9bbb3b35a5b5fabfc83cdb35a6ea950788':
        raise ValueError('actual prior8c physical map')
    before = json.loads(oldq.read_bytes())['allPhysicalMainSha256']; pairs = ordered_pairs(oldrows, raw)
    decided = {r['findingId']: r for r in oldrows if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}
    result, used, test_sources, context_count = [], set(), {}, 0
    module_for_class = {r['class']: r['module'] for r in cases}
    for row in raw:
        pair = pairs.get(row['findingId']); prior = copy.deepcopy(decided.get(pair[0]['findingId'])) if pair else None
        if prior:
            prior['reason'] = prior.get('reason') or prior.get('priorReason')
        value, kind = bind_one(row, [prior] if prior else [], (ROOT/row['sourcePath']).read_bytes(), before, q['allPhysicalMainSha256'])
        if kind == 'REBOUND':
            used.add(prior['findingId']); context = prior.get('staticContextPremiseOnly') is True
            refs = current_refs(prior['currentWholeCaseRefs'], index, context, source=SOURCE)
            for ref in refs:
                name = ref['class']
                if name not in test_sources:
                    path = 'src/schubert-nk-'+module_for_class[name]+'/src/test/java/'+name.replace('.', '/')+'.java'
                    historical = subprocess.check_output(['git', 'show', OLD+':'+path], cwd=ROOT)
                    if hashlib.sha256(historical).hexdigest() != sha(ROOT/path):
                        raise ValueError('reused review expected Test bodies must remain identical;changed oracle needs fresh review')
                    test_sources[name] = sha(ROOT/path)
            context_count += not bool(refs)
            value.update(status=prior['status'], reason=prior['reason'], priorReviewSource=OLD, priorReviewManifestSha256=oldsha,
                currentWholeCaseRefs=refs, currentWholeJoinPending=False, currentQualificationSha256=QSHA, currentCasesSha256=CSHA,
                currentWholePhysicalProofSha256=QSHA, historicalPtImportedAsCurrent=False, staticContextPremiseOnly=context,
                diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE')
        result.append(value)
    if len(used) != 606 or context_count != 211:
        raise ValueError('only observed606 strict source/byte-identical reasons,211 static-context premises')
    newp = BASE/'PG6064-local-map11-expiry14-v1/manifest.json'; reviews = newp.with_name('reviews.json')
    if (sha(newp), sha(reviews)) != ('9d515fa81dfb201241bd1658eaee37627c203324a6eedd23f50560e33cabf45f', '7364fa45a39822f554cdc8f5cc2b01825617a5e06547b6fac779c5e4d89a1818'):
        raise ValueError('individual current25 source reviews immutable')
    by_id = {r['findingId']: i for i, r in enumerate(result)}
    for reviewed in json.loads(reviews.read_bytes()):
        i = by_id[reviewed['findingId']]; original = result[i]
        if original['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or any(original[k] != reviewed[k] for k in ('sourcePath', 'sourceSha256', 'rule', 'beginline', 'endline', 'begincolumn', 'endcolumn', 'diagnosticTextSha256')):
            raise ValueError('exact currently unreviewed diagnostic,no overwriting another reason')
        context = reviewed['staticContextPremiseOnly']; refs = selected_refs(reviewed['currentSelectedCaseRefs'], index)
        if (context and (reviewed['status'] != 'CONTEXT_NOT_APPLICABLE' or refs)) or (not context and len(refs) != 35):
            raise ValueError('explicit static-only premises versus all35 actual new whole references')
        result[i] = dict(reviewed, currentWholeCaseRefs=refs, currentWholeJoinPending=False,
            currentQualificationSha256=QSHA, currentCasesSha256=CSHA, currentWholePhysicalProofSha256=QSHA,
            historicalPtImportedAsCurrent=False, currentWholePhysicalAndStaticInputsVerified=True)
    counts = dict(Counter(r['status'] for r in result))
    if counts != {'REQUIRED_CONTRACT': 364, 'CONTEXT_NOT_APPLICABLE': 237, 'FALSE_POSITIVE': 30, 'NOT_REVIEWED_CURRENT_SOURCE': 674}:
        raise ValueError('all1305 retained;606 strict plus25 individual,not arithmetic-only acceptance')
    value = dict(actualExit=0, source=SOURCE, tests=3979, suites=594, inputSourceFiles=851, physicalMain=1667,
        pmdRawFindings=1305, pmdProcessingErrors=0, checkstyleFindings=0, statusCounts=counts,
        sourceAndWholeJoinedDispositions=631, currentWholeQualificationSha256=QSHA, currentWholeCasesSha256=CSHA,
        rawFindingsSha256=sha(pp.with_name('findings.safe.json')), findingsSha256=hashlib.sha256((json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode()).hexdigest(),
        previousReviewSource=OLD, strictReauthenticated=606, newIndividual=25, staticOnlyPremises=222,
        unchangedTestBodiesVerified=len(test_sources), currentWholeStaticPhysicalInputsComplete=True,
        formalAccepted=False, globalFour100=q['global100'], nativeQualified=False, chrFinalQualified=False,
        effortPercent=None, newAcceptedLeaves=0, ptAlternativeCompleted=0, testsExecuted=0, additionalBuildsIssued=0,
        pgptAllComplete=False, openFollowup='BUG1537/YKT1297 and all existing unresolved scopes')
    return result, value


def main():
    result, value = reviewed_result()
    os.umask(0o077); out = BASE/'PG6068-current-static3979-v1'; out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    if sha(out/'findings.json') != value['findingsSha256']:
        raise ValueError('exact published reviewed rows')
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(value | dict(manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
