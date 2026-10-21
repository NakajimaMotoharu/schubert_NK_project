"""Nineteen current changed-source applicability spans; whole/native success remains pending."""
import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6384_web_fatal_callback_retry_qualification import original_source
from pg5958_private_lock_reason_review import fragment
from pg6292_standalone_interrupt_context import rule_premise
from static_disposition_overlay import load, apply_decisions

PLAN = BASE/'PG6392-current4052-static-plan-v1/manifest.json'
PLAN_SHA = 'aea6890d1e513c9669fc786456d4b1c58180edbb5c6a9b9aa6d8265a0608c1a3'
G = 'AvoidCatchingGenericException'
E = 'EmptyCatchBlock'
T = 'DoNotUseThreads'
SPEC = {
    'ServiceProcessResources': {
        (205, G): (2, 'IOException/Runtime/Error from the exact release port invoke the pre-acquired fixed retention observer. If a finite component observer returns, the original failure is rethrown, not marked closed; the native policy remains non-returning. Public and caller-owned policies are prepared before acquisition.'),
        (243, E): (1, 'The fixed constant diagnostic is best-effort only. Failure to print cannot release the original UNKNOWN or invoke downstream cleanup; caller-owned and fixed native loops retain the actual frame. An empty catch is intentional containment, not successful physical release.'),
        (243, G): (2, 'Both unchecked diagnostic failures remain contained before the caller holding loop. Raw provider text is never printed and no failing diagnostic is recursively retried.'),
        (251, G): (2, 'Both unchecked observation failures enter the fixed finite fallback. Neither normal tick return nor failed observation returns the owning infinite loop or certifies resource closure.'),
        (254, E): (1, 'A failed fallback is contained within a finite action and returns to the owner-held loop, never to the application cleanup chain. The component seam may throw a marker outside its own process for observation; native callers supply only prepared fixed policies.'),
        (254, G): (2, 'Both unchecked fallback failures are contained without changing the original release failure, retrying close or advancing another resource. Non-returning ownership is established in the caller, separately checked by JVM retention/fence review.'),
        (263, T): (1, 'Thread.interrupted clears the current observer flag before monotonic waiting, not a new thread or borrowed-container task. It cannot authorize shutdown/release or count as live native evidence.'),
        (268, T): (1, 'Clearing subsequent interruption inside the monotonic wait prevents a hot retry interval. No resource close or worker restart is performed; the standalone owner retains the UNKNOWN frame.'),
        (275, T): (1, 'The fixed sleep is one bounded observation interval in a plain Java standalone process, not a managed J2EE thread. Its return does not escape the original retention loop.'),
        (276, E): (1, 'InterruptedException consumes only the observation notification, not closure of any owner. The outer loop still retains all original references; interrupt is never a fabricated terminal or cleanup success.')},
    'WebLogApplicationRuntime': {
        (228, G): (1, 'The startup Runtime branch shares the checked lifecycle cleanup path after local owners are captured. The first unknown close enters the SS324 caller-owned holding loop; normal cleanup preserves the original startup failure. Factory-before-handoff and direct startup Error paths are separate residual domains, not certified by this catch.'),
        (256, 'AvoidSynchronizedStatement'): (1, 'The private stopLock serializes stoppedResources and the close transition. Failed close leaves stopping=true and the cursor at the same resource; another close cannot release a downstream resource as if the failed join succeeded. It is not evidence of a real native stop.'),
        (263, G): (1, 'The normal retryable component close maps checked failure to fixed unavailable after fatal preservation, with no cursor increment. Direct Error still propagates; native ownership must independently retain its outer frame. SS324 does not remove this distinct retryable component contract.'),
        (287, G): (2, 'Both Exception and Error from one startup resource close enter the same non-returning frame. Diagnostic and finite tick policies were initialized before acquisition; four reachability fences retain startup failure, close failure, resource and downstream inside the loop. No close retry, later owner release or post-acquisition array/callback allocation occurs.')}
}
TESTS = {
    'ServiceProcessResources': ['api.file.ServiceProcessResourcesTest', 'api.file.ServiceOwnedReleaseTest',
                              'api.file.ServiceNativeReleaseTest', 'api.file.ServiceResourceRetentionTest'],
    'WebLogApplicationRuntime': ['web.bootstrap.WebLogApplicationRuntimeTest', 'web.bootstrap.WebStartupRetentionTest']
}


def calculate():
    source = original_source(); rows = load(PLAN, PLAN_SHA, source)
    qp = BASE/'PG6384-web-fatal-callback-retry-qualification-v1/manifest.json'
    q = json.loads(qp.read_bytes()); private = W/'pg6384-web-fatal-callback-retry-qualification-v1/manifest.safe.json'
    if sha(qp) != '7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7' or sha(private) != q['privateManifestSha256']:
        raise ValueError('genuine current22/static/all physical proof')
    proof = json.loads(private.read_bytes()); rule = rule_premise(); found = Counter(); decisions = []
    poms = {}
    for module in ('bootstrap', 'web'):
        p = ROOT/('src/schubert-nk-'+module+'/pom.xml')
        if any(v in p.read_text() for v in ('<packaging>war', '<packaging>ear', 'jakarta.ejb')):
            raise ValueError('standalone execution context must be re-reviewed')
        poms[module] = sha(p)
    for row in rows:
        name = Path(row['sourcePath']).stem; key = (int(row['beginline']), row['rule'])
        if name not in SPEC or key not in SPEC[name]:
            continue
        count, reason = SPEC[name][key]; found[(name, key)] += 1; path = ROOT/row['sourcePath']
        if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or sha(path) != row['sourceSha256'] or sha(path) != proof['allSourceHashes'][row['sourcePath']]:
            raise ValueError('one exact unreviewed current span')
        module = row['sourcePath'].split('/')[1].removeprefix('schubert-nk-')
        prefix = module+':'+row['sourcePath'].split('/src/main/java/')[1][:-5]
        family = {k: v for k, v in proof['allPhysicalMainSha256'].items() if k == prefix+'.class' or k.startswith(prefix+'$')}
        if not family:
            raise ValueError('actual current owner family')
        context = row['rule'] == T; declarations = []
        if not context:
            for suffix in TESTS[name]:
                cls = 'dev.codex.schubert.nk.'+suffix
                rel = Path('src/schubert-nk-'+module+'/src/test/java')/(cls.replace('.', '/')+'.java')
                committed = subprocess.check_output(['git', 'show', source+':'+rel.as_posix()], cwd=ROOT)
                if (ROOT/rel).read_bytes() != committed:
                    raise ValueError('current declared semantic Test source fixed')
                declarations.append(dict(className=cls, sourceSha256=sha(ROOT/rel)))
        decisions.append(dict(row, source=source, status='CONTEXT_NOT_APPLICABLE' if context else 'REQUIRED_CONTRACT',
            reason=reason, diagnosticFragment=fragment(path.read_text(), row), rawWarningRetained=True,
            owningPhysicalClassHashes=family, plannedCurrentWholeCaseClasses=declarations,
            currentWholeCaseRefs=[], currentWholeJoinPending=True, staticContextPremiseOnly=context,
            standalonePomSha256=poms, threadRulePremise=rule if context else None,
            actualRuntimeProven=False, formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0))
    if len(decisions) != 19 or found != Counter({(name, key): item[0] for name, sites in SPEC.items() for key, item in sites.items()}):
        raise ValueError('all19 individually read source span multiplicities')
    updated = apply_decisions(rows, decisions)
    return decisions, dict(actualExit=0, source=source, rawFindings=1355, reviewed=19,
        baseManifestPath=PLAN.relative_to(ROOT).as_posix(), baseManifestSha256=PLAN_SHA,
        statusCounts=dict(Counter(r['status'] for r in updated)), currentWholeJoinPending=True,
        testsExecuted=0, additionalBuildsIssued=0, pmdRawRemoved=0, F03Accepted=False, formalAccepted=False,
        ptAlternativeCompleted=0, effortPercent=None,
        unresolved=['161 other current source spans', '14 prior missing semantic bindings',
                    'current4052 whole/native/rollout and real safety still not proven'])


def main():
    rows, value = calculate(); os.umask(0o077); out = BASE/'PG6394-startup-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=19, statusCounts=value['statusCounts'], manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
