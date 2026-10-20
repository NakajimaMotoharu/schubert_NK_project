"""Current3988 original XML join: strict685,explicit34 source rereviews,new10; no test replay."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tarfile
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6114_http_owner_qualification import SOURCE
from pg5910_storage_static_rebind import ordered_pairs
from pg5758_static_rebind import bind_one, rationale_text
from static_disposition_overlay import load, validate_rationales
from pg6048_current_jdbc24_review import current_refs
from pg6092_current3985_static_join import source_case_candidates
from pg6120_original3988_artifacts import new_case_identities, OLD
from pg6112_http_owner_selected import PATHS
from pg5958_private_lock_reason_review import fragment
from pg5966_api_sql_selected import source_test_names

PRIOR = BASE/'PG6092-current-static3985-v1/manifest.json'
PRIOR_SHA = '10b6cfcfa6a05960f9cf421b4b07dd943a958993e045a3105320fa680c468226'
ART = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java'
HTTP = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java'


def inputs():
    oldrows = load(PRIOR, PRIOR_SHA, OLD)
    oldq = BASE/'PG6088-current3985-cases/qualification.json'
    if sha(oldq) != '76d222eef92096c6b9fb84c73fb978836a441ec52ced506f0bdc3ece3d4f183a':
        raise ValueError('immutable prior source870 whole map')
    oldphysical = json.loads(oldq.read_bytes())['allPhysicalMainSha256']
    pub = BASE/'PG6114-http-owner-qualification-v1/manifest.json'; private = W/'pg6114-http-owner-qualification-v1/manifest.safe.json'
    if sha(pub) != '504e9754e0c815e97a70870d576988c9a7bde3aeabec6427a71bd15657ae1103':
        raise ValueError('actual same-source1939 source/class/static qualification')
    public = json.loads(pub.read_bytes())
    if sha(private) != public['privateManifestSha256'] or sha(private.with_name('findings.safe.json')) != public['findingsSha256']:
        raise ValueError('all original static input/output bytes')
    static = json.loads(private.read_bytes()); raw = json.loads(private.with_name('findings.safe.json').read_bytes())
    if static['source'] != SOURCE or static['actualExit'] != 0 or static['pmdRawFindings'] != 1311 or static['pmdProcessingErrors'] or static['checkstyleFindings'] or static['originalSixSpotBugs']:
        raise ValueError('one source and complete unfiltered1311/CS0/processing0/six0')
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != static['allSourceHashes']:
        raise ValueError('all851 current Main remain fixed')
    return oldrows, oldphysical, raw, static


def strict_pending(oldrows, before, raw, current):
    pairs = ordered_pairs(oldrows, raw)
    decided = {r['findingId']: r for r in oldrows if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}
    result = []; priors = {}
    for row in raw:
        pair = pairs.get(row['findingId']); prior = decided.get(pair[0]['findingId']) if pair else None
        value, kind = bind_one(row, [prior] if prior else [], (ROOT/row['sourcePath']).read_bytes(), before, current)
        if kind == 'REBOUND':
            priors[row['findingId']] = prior
        result.append(value)
    return result, priors


def changed_reviews(oldrows, raw, before, current):
    bytep = BASE/'PG6110-locked-flag-byte-v1/manifest.json'
    if sha(bytep) != 'f1412018fb6aff74b77d92359b4f13137979d2019720b5f7204618d4b6ad09b1':
        raise ValueError('actual one-field old/current byte equivalence proof')
    byte = json.loads(bytep.read_bytes()); key = 'web:'+ART.split('/src/main/java/')[1][:-5]+'.class'
    if byte['oldClassSha256'] != before[key] or byte['newClassSha256'] != current[key] or not byte['allMethodInstructionsAndExceptionsUnchanged']:
        raise ValueError('actual870->599 bit-only proof also matches currentacb class byte')
    prior_text = subprocess.check_output(['git', 'show', OLD+':'+ART], cwd=ROOT, text=True)
    if prior_text.count('private volatile boolean closed;') != 1 or (ROOT/ART).read_text() != prior_text.replace('private volatile boolean closed;', 'private boolean closed;', 1):
        raise ValueError('exact one modifier source edit,all operations unchanged')
    semantic = lambda r: tuple(r[k] for k in ('rule', 'beginline', 'endline', 'begincolumn', 'endcolumn', 'priority', 'diagnosticTextSha256'))
    prior_art = [r for r in oldrows if r['sourcePath'] == ART and r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE']
    current_art = [r for r in raw if r['sourcePath'] == ART]
    if len(prior_art) != 18 or len(current_art) != 18 or list(map(semantic, prior_art)) != list(map(semantic, current_art)):
        raise ValueError('entire eighteen-site operation/diagnostic sequence,not first matching rule')
    pairs = list(zip(prior_art, current_art))
    old_http = [r for r in oldrows if r['sourcePath'] == HTTP and r['rule'] == 'UseProperClassLoader']
    new_http = [r for r in raw if r['sourcePath'] == HTTP and r['rule'] == 'UseProperClassLoader']
    if len(old_http) != 1 or len(new_http) != 1 or old_http[0]['status'] != 'CONTEXT_NOT_APPLICABLE':
        raise ValueError('one explicit standalone classloader context premise')
    old_http_text = subprocess.check_output(['git', 'show', OLD+':'+HTTP], cwd=ROOT, text=True)
    if fragment(old_http_text, old_http[0]) != fragment((ROOT/HTTP).read_text(), new_http[0]) or 'context.setParentClassLoader(WebHttpServer.class.getClassLoader());' not in (ROOT/HTTP).read_text():
        raise ValueError('exact standalone release classloader expression retained')
    if subprocess.check_output(['git', 'diff', OLD, SOURCE, '--', 'pom.xml', '.mvn', 'mvnw', 'src/deployment', 'program/characterization', ':(glob)src/*/pom.xml'], cwd=ROOT):
        raise ValueError('no automatic loader/context review across environment/build/deployment change')
    pairs.append((old_http[0], new_http[0])); reviews = []
    old_identity = [r for r in oldrows if r['sourcePath'] == HTTP and r['rule'] == 'CompareObjectsWithEquals']
    new_identity = [r for r in raw if r['sourcePath'] == HTTP and r['rule'] == 'CompareObjectsWithEquals']
    if len(old_identity) != 1 or len(new_identity) != 1 or old_identity[0]['status'] != 'REQUIRED_CONTRACT':
        raise ValueError('one explicit Throwable identity guard observation')
    catch_start = '} catch (LifecycleException | RuntimeException | Error failure) {'
    next_method = '  static WebHttpServer startWithFactory('
    def catch_suffix(text):
        if text.count(catch_start) != 1:
            raise ValueError('one exact typed startup failure scope')
        return text.split(catch_start, 1)[1].split(next_method, 1)[0]
    if catch_suffix(old_http_text) != catch_suffix((ROOT/HTTP).read_text()) or 'if (failure != cleanup) failure.addSuppressed(cleanup);' not in catch_suffix(old_http_text):
        raise ValueError('same typed Throwable catch/suppression suffix,not arbitrary object equality')
    orderp = BASE/'PG6116-http-owner-order-v1/manifest.json'
    if sha(orderp) != '6bb8792c6b4f68fd72599f77faffac9176677f85cb1361deb6ff26ba475d8476':
        raise ValueError('actual allthree HTTP constructor/lifecycle/private lambda proof')
    pairs.append((old_identity[0], new_identity[0]))
    for prior, row in pairs:
        path = ROOT/row['sourcePath']
        old_text = prior_text if row['sourcePath'] == ART else old_http_text
        if fragment(old_text, prior) != fragment(path.read_text(), row):
            raise ValueError('each actual diagnostic fragment is independently unchanged')
        cls = row['sourcePath'].split('/src/main/java/')[1][:-5].replace('/', '.')+'Test'
        test = ROOT/'src/schubert-nk-web/src/test/java'/(cls.replace('.', '/')+'.java')
        why = rationale_text(prior)
        if why is None:
            raise ValueError('prior rationale is required,never inferred')
        reviews.append(dict(row, source=SOURCE, status=prior['status'], reason='1292 current-source rereview (not new classification): '+why,
            priorReason=why, priorFindingId=prior['findingId'], priorReviewManifestSha256=PRIOR_SHA,
            diagnosticFragment=fragment(path.read_text(), row), rawWarningRetained=True,
            sourceReauthenticationMethod='ONE_FIELD_BIT_AND_IDENTICAL_OPERATIONS' if row['sourcePath'] == ART else 'EXPLICIT_STANDALONE_LOADER_CONTEXT_UNCHANGED' if row['rule'] == 'UseProperClassLoader' else 'IDENTITY_GUARD_SAME_TYPED_CATCH_AND_SUPPRESSION_SUFFIX',
            declaredIndependentTests=[dict(className=cls, module='web', sourceSha256=sha(test), methods=sorted(source_test_names(test)))],
            currentWholeCaseRefs=[], currentWholeJoinPending=True, staticContextPremiseOnly=False, formalAccepted=False))
    for name, parameter_line in [('ApiManagementServer', 83), ('WebManagementServer', 121)]:
        paths = {r['sourcePath'] for r in oldrows if r['sourcePath'].endswith('/'+name+'.java')}
        if len(paths) != 1:
            raise ValueError('one declared management owner')
        path = paths.pop(); text = (ROOT/path).read_text()
        old_text = subprocess.check_output(['git', 'show', OLD+':'+path], cwd=ROOT, text=True)
        old_threads = [r for r in oldrows if r['sourcePath'] == path and r['rule'] == 'DoNotUseThreads']
        removed = [r for r in old_threads if int(r['beginline']) == parameter_line]
        if len(removed) != 1 or 'HttpServer server, ThreadPoolExecutor executor' not in old_text.splitlines()[parameter_line-1]:
            raise ValueError('only removed old private-constructor executor parameter warning')
        old_threads = [r for r in old_threads if r not in removed]
        new_threads = [r for r in raw if r['sourcePath'] == path and r['rule'] == 'DoNotUseThreads']
        if len(new_threads) != (6 if name == 'ApiManagementServer' else 8) or len(old_threads) != len(new_threads):
            raise ValueError('six API/eight Web explicit existing thread-context sites')
        for prior, row in zip(old_threads, new_threads):
            if prior['status'] != 'CONTEXT_NOT_APPLICABLE' or prior.get('staticContextPremiseOnly') is not True or fragment(old_text, prior) != fragment(text, row) or prior['diagnosticTextSha256'] != row['diagnosticTextSha256']:
                raise ValueError('entire source-local thread operation sequence,not an arbitrary first match')
            reviews.append(dict(row, source=SOURCE, status='CONTEXT_NOT_APPLICABLE',
                reason='1292 individual source-context rereview: '+rationale_text(prior)+'. Current SS311/342/343 remains standalone dedicated JVM,not a J2EE/WAR/EAR container. Actual6116 confirms daemon-thread lambda and existing lifecycle methods unchanged;this rule-context premise proves neither worker termination nor runtime health.',
                priorReason=rationale_text(prior), priorFindingId=prior['findingId'], priorReviewManifestSha256=PRIOR_SHA,
                diagnosticFragment=fragment(text, row), rawWarningRetained=True,
                sourceReauthenticationMethod='EXPLICIT_STANDALONE_MANAGEMENT_CONTEXT_SEQUENCE',
                declaredIndependentTests=[], currentWholeCaseRefs=[], currentWholeJoinPending=True,
                staticContextPremiseOnly=True, formalAccepted=False))
    if len(reviews) != 34:
        raise ValueError('eighteen modifier reasons/two HTTP sites/fourteen context premises only')
    return reviews


def reviewed_result(qsha, csha):
    if any(re.fullmatch('[0-9a-f]{64}', x) is None for x in (qsha, csha)):
        raise ValueError('explicit genuine qualification and cases hashes first')
    qp = BASE/'PG6118-current3988-cases/qualification.json'; cp = qp.with_name('cases.json')
    if (sha(qp), sha(cp)) != (qsha, csha):
        raise ValueError('immutable current3988 original qualification/cases')
    q, cases = [json.loads(p.read_bytes()) for p in (qp, cp)]
    if q['productionSource'] != SOURCE or (q['tests'], q['suites'], q['mainClasses'], q['FESFlakyNotRun']) != (3988, 595, 1667, 0) or not q['currentOriginalXmlQualified'] or q['staticSixModules']:
        raise ValueError('genuine current3988 source/run/XML qualification')
    oldrows, before, raw, static = inputs()
    if static['allSourceHashes'] != q['allSourceHashes'] or static['allPhysicalMainSha256'] != q['allPhysicalMainSha256']:
        raise ValueError('all851/1667 original selected static == current whole inputs')
    receipt_path = W/'pg6120-original3988-artifacts-v1/manifest.safe.json'
    receipt = json.loads(receipt_path.read_bytes()); ip = receipt_path.with_name('input.safe.json')
    if receipt['actualExit'] != 0 or receipt['source'] != SOURCE or receipt['publicQualificationSha256'] != qsha or receipt['publicCasesSha256'] != csha or receipt['inputSha256'] != sha(ip):
        raise ValueError('original reader receipt and full input bytes')
    whole_inputs = json.loads(ip.read_bytes())['allSourceInputs']; selected_inputs = {}
    with tarfile.open(W/'pg6112-http-owner-selected-v1/source.tar') as tar:
        for member in tar:
            if member.isfile():
                selected_inputs[member.name] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    rules = {'tools/quality/static/'+name for name in ('README.md', 'checkstyle.xml', 'pmd.xml', 'pmd-record-1298.patch',
        'canaries/DynamicKeyRuleCanary.java', 'canaries/GateField.java', 'canaries/GateNegative.java', 'canaries/GatePositive.java',
        'canaries/GateRecord.java', 'canaries/OutboxCauseGraphCanary.java', 'canaries/UnsafeKeyRuleCanary.java')}
    if len(whole_inputs) != 1888 or set(selected_inputs)-set(whole_inputs) != rules or any(selected_inputs.get(p) != h for p, h in whole_inputs.items()):
        raise ValueError('every1888 original Main/Test/CHR/build input equal,only11 explicit static extras')
    if any(hashlib.sha256(subprocess.check_output(['git', 'show', SOURCE+':'+p], cwd=ROOT)).hexdigest() != selected_inputs[p] for p in rules):
        raise ValueError('all static extras canonical and unchanged')
    new_case_identities()  # All three changed Test files retain every old byte outside new leading case.
    index = {(r['class'], r['caseNameSha256']): r for r in cases}
    if len(index) != 3988 or any(r['xmlSha256'] != q['modules'][r['module']]['xmlHashes'][r['sourceXml']] for r in cases):
        raise ValueError('every3988 unique current original XML case')
    modules = {r['class']: r['module'] for r in cases}; verified = {}
    changed_tests = {p for p in PATHS if '/src/test/java/' in p}
    def verify_test(name):
        path = 'src/schubert-nk-'+modules[name]+'/src/test/java/'+name.replace('.', '/')+'.java'
        if path not in verified:
            old = subprocess.check_output(['git', 'show', OLD+':'+path], cwd=ROOT)
            if hashlib.sha256(old).hexdigest() != sha(ROOT/path) and path not in changed_tests:
                raise ValueError('unchanged independent Test text or exact proven new leading case only')
            verified[path] = sha(ROOT/path)
    result, priors = strict_pending(oldrows, before, raw, q['allPhysicalMainSha256'])
    if len(priors) != 685:
        raise ValueError('only actual685 strict source/byte-identical reasons may rebind')
    for row in result:
        prior = priors.get(row['findingId'])
        if prior:
            context = prior.get('staticContextPremiseOnly') is True
            refs = current_refs(prior['currentWholeCaseRefs'], index, context, source=SOURCE)
            for ref in refs:
                verify_test(ref['class'])
            row.update(status=prior['status'], reason=rationale_text(prior), priorReason=rationale_text(prior),
                priorReviewSource=OLD, priorReviewManifestSha256=PRIOR_SHA, currentWholeCaseRefs=refs,
                currentWholeJoinPending=False, currentQualificationSha256=qsha, currentCasesSha256=csha,
                historicalPtImportedAsCurrent=False, staticContextPremiseOnly=context)
    reviews = changed_reviews(oldrows, raw, before, q['allPhysicalMainSha256'])
    reviewp = BASE/'PG6122-web-lifecycle-review-v1/reviews.json'
    if sha(reviewp) != '88e2c6c4f1480082143231fc01e6244f07817df9d0279f7e91f905b2bbd21151':
        raise ValueError('actual new ten individual review results')
    reviews += json.loads(reviewp.read_bytes()); positions = {r['findingId']: i for i, r in enumerate(result)}
    for reviewed in reviews:
        i = positions[reviewed['findingId']]
        if result[i]['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or any(result[i][k] != reviewed[k] for k in ('sourcePath', 'sourceSha256', 'rule', 'beginline', 'endline', 'begincolumn', 'endcolumn', 'diagnosticTextSha256')):
            raise ValueError('each rereview/newreview targets exact unresolved raw occurrence')
        refs = []
        for declared in reviewed['declaredIndependentTests']:
            name = declared['className']; path = ROOT/('src/schubert-nk-'+declared['module']+'/src/test/java')/(name.replace('.', '/')+'.java')
            if sha(path) != declared['sourceSha256']:
                raise ValueError('exact reviewed independent Test text')
            verify_test(name)
            for method in declared['methods']:
                matches = [index[(name, hashlib.sha256(n.encode()).hexdigest())] for n in source_case_candidates(path.read_text(), method) if (name, hashlib.sha256(n.encode()).hexdigest()) in index]
                if len(matches) != 1 or matches[0]['source'] != SOURCE or matches[0]['result'] != 'PASS_ORIGINAL_XML':
                    raise ValueError('one genuine current3988 original result per declared method')
                refs.append({k: matches[0][k] for k in ('testId', 'xmlSha256', 'class', 'caseNameSha256', 'source')})
        if not refs and reviewed.get('staticContextPremiseOnly') is not True:
            raise ValueError('every changed/new review has actual current independent PT')
        result[i] = dict(reviewed, currentWholeCaseRefs=refs, currentWholeJoinPending=False,
                         currentQualificationSha256=qsha, currentCasesSha256=csha, historicalPtImportedAsCurrent=False)
    validate_rationales(result); counts = dict(Counter(r['status'] for r in result))
    if counts != {'REQUIRED_CONTRACT': 457, 'CONTEXT_NOT_APPLICABLE': 235, 'FALSE_POSITIVE': 37, 'NOT_REVIEWED_CURRENT_SOURCE': 582}:
        raise ValueError('all1311 retained;strict685/rereview34/new10 only')
    value = dict(actualExit=0, source=SOURCE, tests=3988, suites=595, sourceFiles=851, physicalMain=1667,
        currentRawFindings=1311, statusCounts=counts, sourceAndWholeJoinedDispositions=729,
        strictReauthenticated=685, changedSourceReasonsRereviewed=34, netNewDispositions=10,
        staticContextOnlyPremises=sum(r.get('staticContextPremiseOnly') is True for r in result), independentTestFilesVerified=len(verified),
        currentWholeQualificationSha256=qsha, currentWholeCasesSha256=csha,
        currentRawStaticSha256=sha(W/'pg6114-http-owner-qualification-v1/findings.safe.json'),
        currentWholeStaticPhysicalInputsComplete=True, inventoryFile='findings.json',
        formalAccepted=False, F03Accepted=False, globalFour100=q['global100'], nativeQualified=False,
        chrFinalQualified=False, effortPercent=None, newAcceptedLeaves=0, ptAlternativeCompleted=0,
        testsExecuted=0, additionalBuildsIssued=0, pgptAllComplete=False)
    return result, value


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--qualification-sha256', required=True); parser.add_argument('--cases-sha256', required=True)
    args = parser.parse_args(); rows, value = reviewed_result(args.qualification_sha256, args.cases_sha256)
    os.umask(0o077); out = BASE/'PG6124-current-static3988-v1'; out.mkdir()
    with (out/'findings.json').open('x') as stream:
        json.dump(rows, stream, ensure_ascii=False, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    value['inventorySha256'] = sha(out/'findings.json')
    with (out/'manifest.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps(value | dict(manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
