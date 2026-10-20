"""Source/byte/Test-qualified old reasons plus98 fresh JMS reviews joined to original3985 XML."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tarfile
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6082_web_factory_qualification import SOURCE
from pg5910_storage_static_rebind import ordered_pairs
from pg5758_static_rebind import bind_one, rationale_text
from static_disposition_overlay import validate_rationales
from pg6048_current_jdbc24_review import current_refs
from pg6090_original3985_artifacts import OLD, TESTS, new_case_identities


def source_case_candidates(text, method):
    prefix = r'(?m)^\s*(?:public\s+)?void\s+'+re.escape(method)+r'\s*'
    zero = re.findall(prefix+r'\(\s*\)', text)
    path = re.findall(prefix+r'\(\s*@TempDir\s+Path\s+[A-Za-z_$][A-Za-z0-9_$]*\s*\)', text)
    if len(zero) == 1 and not path:
        return method, method+'()'
    if len(path) == 1 and not zero and 'import java.nio.file.Path;' in text and 'import org.junit.jupiter.api.io.TempDir;' in text:
        return (method+'(Path)',)
    raise ValueError('only one explicit zero-argument or imported TempDir Path Test signature;no guessed display alias')


def reviewed_result(qsha, csha):
    if any(re.fullmatch('[0-9a-f]{64}', x) is None for x in (qsha, csha)):
        raise ValueError('explicit genuine current qualification/cases SHA256')
    qp = BASE/'PG6088-current3985-cases/qualification.json'; cp = qp.with_name('cases.json')
    if (sha(qp), sha(cp)) != (qsha, csha):
        raise ValueError('immutable independent3985 qualification/cases first')
    q, cases = [json.loads(p.read_bytes()) for p in (qp, cp)]
    if (q['productionSource'] != SOURCE or (q['tests'], q['suites'], q['mainClasses'], q['FESFlakyNotRun']) != (3985, 595, 1667, 0)
            or not q['currentOriginalXmlQualified'] or q['staticSixModules']):
        raise ValueError('genuine current3985 original XML/physical qualification')
    sp = BASE/'PG6082-web-factory-qualification-v1/manifest.json'; pp = W/'pg6082-web-factory-qualification-v1/manifest.safe.json'
    if sha(sp) != '134e8181764a40b725fd0fa9365f5d18fa714b66221e4f46b992d3f84cd7e735':
        raise ValueError('actual original source870 static report')
    pub = json.loads(sp.read_bytes())
    if sha(pp) != pub['privateManifestSha256']:
        raise ValueError('all851/1667 original static input map')
    static = json.loads(pp.read_bytes()); raw_path = pp.with_name('findings.safe.json')
    if sha(raw_path) != pub['findingsSha256']:
        raise ValueError('all unfiltered1315 diagnostic rows')
    raw = json.loads(raw_path.read_bytes())
    if (static['source'] != SOURCE or static['allSourceHashes'] != q['allSourceHashes'] or static['allPhysicalMainSha256'] != q['allPhysicalMainSha256']
            or static['pmdRawFindings'] != 1315 or static['pmdProcessingErrors'] or static['checkstyleFindings'] or static['originalSixSpotBugs']):
        raise ValueError('actual same-source selected static and original whole source/class maps exactly equal')
    original_receipt = W/'pg6090-original3985-artifacts-v1/manifest.safe.json'
    receipt = json.loads(original_receipt.read_bytes()); ip = original_receipt.with_name('input.safe.json')
    if (receipt['actualExit'] != 0 or receipt['source'] != SOURCE or receipt['publicQualificationSha256'] != qsha
            or receipt['publicCasesSha256'] != csha or receipt['inputSha256'] != sha(ip)):
        raise ValueError('original reader receipt and complete immutable input')
    whole_inputs = json.loads(ip.read_bytes())['allSourceInputs']; selected_inputs = {}
    with tarfile.open(W/'pg6086-web-factory-selected-v2/source.tar') as tar:
        for member in tar:
            if member.isfile():
                selected_inputs[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    rules = {'tools/quality/static/'+name for name in ('README.md', 'checkstyle.xml', 'pmd.xml', 'pmd-record-1298.patch',
        'canaries/DynamicKeyRuleCanary.java', 'canaries/GateField.java', 'canaries/GateNegative.java',
        'canaries/GatePositive.java', 'canaries/GateRecord.java', 'canaries/OutboxCauseGraphCanary.java', 'canaries/UnsafeKeyRuleCanary.java')}
    if (len(whole_inputs) != 1888 or set(selected_inputs)-set(whole_inputs) != rules
            or any(selected_inputs.get(p) != h for p, h in whole_inputs.items())):
        raise ValueError('all1888 Main/Test/CHR/build original inputs equal;only11 explicit static extras')
    if any(hashlib.sha256(subprocess.check_output(['git', 'show', SOURCE+':'+p], cwd=ROOT)).hexdigest() != selected_inputs[p] for p in rules):
        raise ValueError('all static extras equal canonical source')
    oldp = BASE/'PG6068-current-static3979-v1/manifest.json'; oldraw = oldp.with_name('findings.json')
    if sha(oldp) != '2f123f32ded4e8072de3f137f0faf98aabf7ed39e5601e7514a9228caa2c8c2a' or sha(oldraw) != 'efcf04c868453946ce2fd3c625d30b0d4374e12a3edc4108193725007335112f':
        raise ValueError('all original c4 rows unchanged including BUG1540 missing text')
    oldrows = json.loads(oldraw.read_bytes()); restoration = BASE/'PG6100-rationale-lineage-v1/manifest.json'
    if sha(restoration) != '77f7b881be30d4c4bf6250dc236237adf2524ded3ac6df7fb630cdccaf3799d2':
        raise ValueError('independent hash/source/diagnostic ancestry restoration first')
    rp = restoration.with_name('restorations.json'); restored = json.loads(rp.read_bytes())
    if sha(rp) != json.loads(restoration.read_bytes())['restorationsSha256'] or len(restored) != 431:
        raise ValueError('each missing reason restored through explicit immutable ancestry')
    restores = {r['findingId']: r for r in restored}
    for row in oldrows:
        if row['findingId'] in restores:
            why = restores[row['findingId']]
            if rationale_text(row) is not None or any(row[k] != why[k] for k in ('sourcePath', 'sourceSha256', 'status')):
                raise ValueError('restore only original missing text,not change classification/source')
            row['reason'] = row['priorReason'] = why['reason']
    validate_rationales(oldrows)
    oldq = BASE/'PG6060-current3979-cases/qualification.json'
    if sha(oldq) != '4a411f7710e793e34204cc738d7882c69d500967b719c596c48687e195b84a5e':
        raise ValueError('prior physical whole map immutable')
    before = json.loads(oldq.read_bytes())['allPhysicalMainSha256']
    pairs = ordered_pairs(oldrows, raw); decided = {r['findingId']: r for r in oldrows if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}
    index = {(r['class'], r['caseNameSha256']): r for r in cases}
    if len(index) != 3985 or any(r['xmlSha256'] != q['modules'][r['module']]['xmlHashes'][r['sourceXml']] for r in cases):
        raise ValueError('all3985 unique actual source/run/XML identities')
    new_case_identities()  # Proves the only three changed old Test files retain every original body.
    modules = {r['class']: r['module'] for r in cases}; result, used, verified_tests = [], set(), {}
    for row in raw:
        pair = pairs.get(row['findingId']); prior = decided.get(pair[0]['findingId']) if pair else None
        value, kind = bind_one(row, [prior] if prior else [], (ROOT/row['sourcePath']).read_bytes(), before, q['allPhysicalMainSha256'])
        if kind == 'REBOUND':
            used.add(prior['findingId']); context = prior.get('staticContextPremiseOnly') is True
            refs = current_refs(prior['currentWholeCaseRefs'], index, context, source=SOURCE)
            for ref in refs:
                name = ref['class']; path = 'src/schubert-nk-'+modules[name]+'/src/test/java/'+name.replace('.', '/')+'.java'
                if path not in verified_tests:
                    historical = subprocess.check_output(['git', 'show', OLD+':'+path], cwd=ROOT)
                    if hashlib.sha256(historical).hexdigest() != sha(ROOT/path) and path not in TESTS:
                        raise ValueError('unchanged independent Test text or explicit suffix-preserved new leading case only')
                    verified_tests[path] = sha(ROOT/path)
            value.update(status=prior['status'], reason=rationale_text(prior), priorReason=rationale_text(prior),
                priorReviewSource=OLD, priorReviewManifestSha256=sha(oldp), currentWholeCaseRefs=refs,
                currentWholeJoinPending=False, currentQualificationSha256=qsha, currentCasesSha256=csha,
                historicalPtImportedAsCurrent=False, staticContextPremiseOnly=context,
                diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE',
                rationaleRestorationSha256=sha(restoration) if prior['findingId'] in restores else None)
        result.append(value)
    if len(used) != 623:
        raise ValueError('only observed623 source/fullowner-byte identical dispositions;changed eight need new review')
    reviews_path = BASE/'PG6098-jms-individual-review-v1/reviews.json'
    if sha(reviews_path) != '15148a80d960824601364d4914838f0ba94e22172fa9afb73cd29fb8aff3656b':
        raise ValueError('all fresh98 per-site reviews,one volatile remains unresolved')
    positions = {r['findingId']: i for i, r in enumerate(result)}
    for reviewed in json.loads(reviews_path.read_bytes()):
        i = positions[reviewed['findingId']]
        if result[i]['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or any(result[i][k] != reviewed[k] for k in ('sourcePath','sourceSha256','rule','beginline','endline','begincolumn','endcolumn','diagnosticTextSha256')):
            raise ValueError('fresh review targets exact unresolved current diagnostic only')
        refs = []
        for declared in reviewed['declaredIndependentTests']:
            name = declared['className']; path = ROOT/('src/schubert-nk-'+declared['module']+'/src/test/java')/(name.replace('.', '/')+'.java')
            if sha(path) != declared['sourceSha256']:
                raise ValueError('independent reviewed Test source stays exact')
            for method in declared['methods']:
                candidates = source_case_candidates(path.read_text(), method)
                matches = [index[(name, hashlib.sha256(n.encode()).hexdigest())] for n in candidates if (name, hashlib.sha256(n.encode()).hexdigest()) in index]
                if len(matches) != 1 or matches[0]['source'] != SOURCE or matches[0]['result'] != 'PASS_ORIGINAL_XML':
                    raise ValueError('each named review Test has exactly one genuine current whole PASS')
                refs.append({k: matches[0][k] for k in ('testId','xmlSha256','class','caseNameSha256','source')})
        if not refs:
            raise ValueError('every fresh behavior review has actual current independent PT')
        result[i] = dict(reviewed, currentWholeCaseRefs=refs, currentWholeJoinPending=False,
            currentQualificationSha256=qsha, currentCasesSha256=csha, historicalPtImportedAsCurrent=False)
    validate_rationales(result)
    counts = dict(Counter(r['status'] for r in result))
    if counts != {'REQUIRED_CONTRACT':447,'CONTEXT_NOT_APPLICABLE':237,'FALSE_POSITIVE':37,'NOT_REVIEWED_CURRENT_SOURCE':594}:
        raise ValueError('all1315 retained;623 strict plus98 fresh,not arithmetic-only acceptance')
    value = dict(actualExit=0, source=SOURCE, tests=3985, suites=595, sourceFiles=851, physicalMain=1667,
        currentRawFindings=1315, statusCounts=counts, sourceAndWholeJoinedDispositions=721,
        strictReauthenticated=623, freshIndividualReviews=98, changedOldReasonsRereviewed=8, netNewDispositions=90,
        restoredHistoricalMissingReasons=431, rationaleRestorationSha256=sha(restoration),
        staticContextOnlyPremises=222, independentTestFilesVerified=len(verified_tests),
        currentWholeQualificationSha256=qsha, currentWholeCasesSha256=csha, currentRawStaticSha256=sha(raw_path),
        currentWholeStaticPhysicalInputsComplete=True, inventoryFile='findings.json',
        formalAccepted=False, F03Accepted=False, globalFour100=q['global100'], nativeQualified=False,
        chrFinalQualified=False, effortPercent=None, newAcceptedLeaves=0, ptAlternativeCompleted=0,
        testsExecuted=0, additionalBuildsIssued=0, pgptAllComplete=False)
    return result, value


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--qualification-sha256', required=True); parser.add_argument('--cases-sha256', required=True)
    args = parser.parse_args(); rows, value = reviewed_result(args.qualification_sha256, args.cases_sha256)
    os.umask(0o077); out = BASE/'PG6092-current-static3985-v1'; out.mkdir()
    with (out/'findings.json').open('x') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value['inventorySha256'] = sha(out/'findings.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(value | dict(manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
