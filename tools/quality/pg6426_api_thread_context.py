"""Resolve exactly two prior missing semantic bindings by independently checked rule premise."""
import copy
import hashlib
import json
import os
import re
import subprocess
import zipfile
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6414_web_frame_pending_qualification import original_source
from pg6292_standalone_interrupt_context import rule_premise
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load, validate_rationales
from pg6186_native_ownership_order import methods, one_call

INPUT = BASE/'PG6422-web-frame-static-review-v1/manifest.json'
INPUT_SHA = '98f22c7c7045c9a6c7674b6329d87448098e8a7ec3aeb8b9ffd3b79844c7539e'
PATH = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java'
CLS = 'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain'
KEY = 'api:'+CLS.replace('.', '/')+'.class'
REASONS = {
    87: 'Pinned DoNotUseThreads restricts J2EE-managed webapp threading. SS311 defines this API as a standalone Java service; the ordinary entry installs only its own current-thread uncaught handler before startup. The actual JVM target is java.lang.Thread.currentThread/setUncaughtExceptionHandler. This architecture premise needs no invented dynamic Test case and does not prove actual API startup, native ownership or readiness.',
    289: 'The Thread parameter is required by the JVM uncaught-handler signature; the fatal method ignores that thread and the Throwable and prints only fixed API process failed. It does not create/control a foreign thread or run under a J2EE container. Source/JVM/pom/rule hashes prove only this pinned rule non-applicability, not native success or provider cleanup.'
}


def calculate():
    source = original_source(); rows = load(INPUT, INPUT_SHA, source); rule = rule_premise()
    qp = BASE/'PG6414-web-frame-pending-qualification-v1/manifest.json'; q = json.loads(qp.read_bytes())
    private = W/'pg6414-web-frame-pending-qualification-v1/manifest.safe.json'
    if sha(qp) != 'f214986209f003c92248644f55e617042af273ab6b652a2e753dffceda30498f' or sha(private) != q['privateManifestSha256']:
        raise ValueError('exact current all8511667 qualification first')
    proof = json.loads(private.read_bytes()); snapshot = W/'pg6412-web-frame-pending-selected-v1/source'
    pom = ROOT/'src/schubert-nk-api/pom.xml'; ss = ROOT/'documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md'
    if sha(pom) != sha(snapshot/'src/schubert-nk-api/pom.xml') or any(v in pom.read_text() for v in ('<packaging>war', '<packaging>ear', 'jakarta.ejb')):
        raise ValueError('same standalone API jar context, not a changed container deployment')
    text = (ROOT/PATH).read_text()
    if sha(ROOT/PATH) != proof['allSourceHashes'][PATH] or not re.search(r'public void main\(String\[\] arguments\) throws IOException\s*\{\s*Thread.currentThread\(\).setUncaughtExceptionHandler\(ApiProcessMain::fatal\);', text):
        raise ValueError('exact owned current-thread entry before startup')
    jar = snapshot/'src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    with zipfile.ZipFile(jar) as z:
        actual = {'api:'+n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
    if actual != {k: v for k, v in proof['allPhysicalMainSha256'].items() if k.startswith('api:')}:
        raise ValueError('every original API Jar class still qualified')
    raw = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jar), CLS], text=True)
    blocks = methods(raw); main = next(v for k, v in blocks.items() if ' void main(' in k)
    one_call({'main': main}, 'Thread.currentThread:'); one_call({'main': main}, 'Thread.setUncaughtExceptionHandler:')
    fatal = next(v for k, v in blocks.items() if ' void fatal(java.lang.Thread, java.lang.Throwable)' in k)
    one_call({'fatal': fatal}, 'PrintStream.println:')
    if fatal.count('String API process failed') != 1 or any(op in fatal for op in ('aload_0', 'aload_1')):
        raise ValueError('fatal ignores both values, only fixed diagnostic')
    result = copy.deepcopy(rows); resolutions = []; found = set()
    for index, row in enumerate(rows):
        if row['sourcePath'] != PATH or row['rule'] != 'DoNotUseThreads' or int(row['beginline']) not in REASONS:
            continue
        line = int(row['beginline'])
        if line in found or row['status'] != 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' or row.get('priorDisposition') != 'CONTEXT_NOT_APPLICABLE' or row.get('wholeSourceQualifiedCaseBindingStillPending') is not True or row['sourceSha256'] != sha(ROOT/PATH):
            raise ValueError('exact two previously unresolved context-only sites, no broad pending promotion')
        found.add(line); previous = copy.deepcopy(row)
        result[index].update(status='CONTEXT_NOT_APPLICABLE', reason=REASONS[line],
            staticContextPremiseOnly=True, rawWarningRetained=True, currentWholeCaseRefs=[], currentWholeJoinPending=True,
            wholeSourceQualifiedCaseBindingStillPending=False, noDynamicCaseRequiredForThisRulePremise=True,
            explicitCurrentSourceContextRereview=True, unresolvedReason=None,
            resolvedPriorPending=dict(status=previous['status'], missingSemanticBinding=True,
                priorReason=previous.get('reason'), historicalUnresolvedReason=previous.get('unresolvedReason'),
                resolution='FRESH_PINNED_RULE_JAR_POM_SOURCE_JVM_CONTEXT_ONLY'),
            diagnosticFragment=fragment(text, row), pinnedRule=rule, apiPomSha256=sha(pom), relatedSS311Sha256=sha(ss),
            owningClassSha256=actual[KEY], originalSourceClassProofSha256=sha(private),
            actualRuntimeProven=False, formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0)
        resolutions.append(result[index])
    if found != set(REASONS) or len(resolutions) != 2:
        raise ValueError('both exact API thread-context sites required')
    if [r['findingId'] for r in result] != [r['findingId'] for r in rows] or len(result) != 1358:
        raise ValueError('all raw diagnostic identities and order retained')
    validate_rationales(result)
    return result, resolutions, dict(actualExit=0, source=source, rawFindings=1358, inventoryFile='findings.json',
        inputManifestPath=INPUT.relative_to(ROOT).as_posix(), inputManifestSha256=INPUT_SHA,
        statusCounts=dict(Counter(r['status'] for r in result)), currentWholeJoinPending=True,
        explicitRulePremiseResolutions=2, remainingMissingSemanticBindings=12,
        testsExecuted=0, additionalBuildsIssued=0, productionClassesExecuted=0, liveProcessThreadActions=0,
        formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0, newAcceptedLeaves=0, effortPercent=None,
        residual=['WebNative12 unresolved semantic sites remain pending','134 other source reviews and current4054 join still required',
                  'architecture premise is not current API/native/Root safety proof'])


def main():
    rows, resolutions, value = calculate(); os.umask(0o077); out = BASE/'PG6426-api-thread-context-v1'; out.mkdir()
    for name, item in (('findings.json', rows), ('resolutions.json', resolutions), ('manifest.json', value)):
        if name == 'manifest.json':
            value['inventorySha256'] = sha(out/'findings.json'); value['resolutionsSha256'] = sha(out/'resolutions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, contextResolved=2, statusCounts=value['statusCounts'],
        semanticUnresolved=12, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
