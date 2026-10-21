"""Twelve explicit current Web applicability decisions; component PT/JVM, not native or whole PASS."""
import json
import os
import re
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6470_web_owned_component_selected import MAIN, TEST
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load, apply_decisions

PLAN_SHA = '63f05846011cc46260492c3ec07be19945a762a73f591dc5991671359c57c36c'
QSHA = '67be969bc999b8cc5cd020faea6f1604bf8c32ebf8673f6db4a13910a8e90722'
ORDER_SHA = 'd92b841cbbbbbe64680fd01609c8c21ee84de21d43732d7ffe8df02fedf0864a'
SITES = {
    'replies': ('The five volatile handles are independently published snapshots, not an atomic aggregate. replies is captured before consumer start, read once by healthy, and closed only through the private-lock stop sequence. Actual field flags and the unchanged health/close instructions complement the owned running-consumer/close tests; latch visibility alone is not used as a JMM proof.', ('001','004','006')),
    'replay': ('replay is retained immediately after its owned worker start and published for an unlocked health snapshot. The private monitor serializes start and close; the volatile read does not authorize release. Actual worker readiness and post-close false state are checked with a dedicated empty production-schema DB, while descriptor/JVM lifetime checks preserve the outer owner.', ('001','004','006')),
    'retry': ('retry is an independently published owned worker, captured before other startup work and inspected once for health. The same private lock and ordered stop retain its dependencies until worker close. Actual self-owned DB/JMS startup and stopping/publication negatives test the intended component contract; neither synthetic Ready nor this flag proves real Root authorization.', ('001','004','006')),
    'http': ('http is captured by the existing native assembly owner callback before HTTP initialization can fail. The volatile handle supports the unlocked health snapshot; all mutation and ordered stop retain the private lock. Actual HTTP assembly/start, Ready failure and concurrent-close serialization are exercised; the original capture lambda and close opcodes/bootstrap targets are independently unchanged.', ('001','003','004')),
    'management': ('management is stored immediately after bind and before start/promote. ready snapshots the same volatile manager, whose own stopping/promoted state controls publication. A synthetic release IOException cannot promote, and normal/duplicate close makes ready false. This does not replace real generation/peer or admission authentication.', ('001','003','006')),
    'start': ('The private final ownerLock protects the compound startAttempted/stopping check, acquisition/capture order and final promotion. It is neither the exposed runtime object nor a managed-container monitor. A bounded separate close thread is actually BLOCKED at the private monitor during the first owned verification gate; startup proceeds before the known owners can be closed. Source/JVM prove the same monitor on all exits.', ('001','004')),
    'close': ('The same private final ownerLock serializes admission refusal, the existing ten-phase stop cursor and concurrent start/close. No successful cursor step is repeated on duplicate close. Actual owned FD zero, public false states and concurrent close completion are checked; UNKNOWN retry/retention and real native ownership remain separate dependencies, not inferred from this monitor.', ('001','003','004','006')),
    'currentBroker': ('currentBroker is a borrowed alias of the immediately captured broker field, not a second owned factory/context. It must remain open across readiness, consumer/dispatcher assembly and all workers. JVM proves immediate field capture and no close in start; actual own TCP broker/start/healthy and reverse close test the component path. The field is released in the existing final stop phase only.', ('001','003','004','006')),
    'keys': ('keys aliases the already retained WebNativeCodecs owner; wrapping this local in TWR would prematurely invalidate codec dependencies of the HTTP/worker graph. The field capture, no startup alias close and unchanged ordered codec release are independently proven. Synthetic five-key outer credentials remain borrowed and readable after normal and failed startup close; real credentials/native authorization are not claimed.', ('001','002','003','006')),
    'transferRoot': ('transferRoot aliases the field captured immediately after descriptor-based open, before fixed identity verification. On the first proof IO/RTE/Error/null/false failure, one own FD remains known until normal close; successful startup retains both roots and close consumes them once. Interface FD spying and inode-backed own paths are independent of private fields. No deployed transfer root is touched.', ('001','002','004')),
    'assetRoot': ('assetRoot is a borrowed alias of the second immediately captured owned root. First-root-success/second-proof-null-or-false cases retain two known FDs until ordinary close; successful startup and concurrent close keep the same bounded ownership. The real native metadata helper is separately tested on an own inode, without treating synthetic component role assertions as OS authorization.', ('001','002','004','007')),
    'control': ('control aliases the immediately stored management owner, so local TWR would terminate the endpoint after startup. Actual bind/start/promote and release-failure cases keep the field and never falsely publish ready; ordered close clears readiness without re-promoting or repeating FD closure. JVM proves the capture-before-start and unchanged close/bootstrap semantics, not external Root completion.', ('001','003','006')),
}


def site(row, text):
    line = text.splitlines()[int(row['beginline'])-1]
    if row['rule'] == 'AvoidUsingVolatile':
        found = re.search(r'private volatile @Nullable \w+ (replies|replay|retry|http|management);', line)
        if found: return found.group(1)
    elif row['rule'] == 'CloseResource':
        found = re.search(r'var (currentBroker|keys|transferRoot|assetRoot|control) = Objects.requireNonNull\(', line)
        if found: return found.group(1)
    elif row['rule'] == 'AvoidSynchronizedStatement' and line.strip() == 'synchronized (ownerLock) {':
        start = text.index('  void start()'); close = text.index('  public void close()')
        offset = sum(len(v) for v in text.splitlines(keepends=True)[:int(row['beginline'])-1])
        if start < offset < text.index('  static Path nativePath('): return 'start'
        if close < offset < text.index('  static Duration replyTimeout('): return 'close'
    raise ValueError('unrecognized exact current Web warning span; never generic approval')


def calculate():
    qp = BASE/'PG6500-web-owned-component-qualification-v5/manifest.json'
    op = BASE/'PG6484-web-owned-runtime-order-v1/manifest.json'
    if sha(qp) != QSHA or sha(op) != ORDER_SHA:
        raise ValueError('exact original27 and actual complete JVM/default binding evidence')
    q, order = [json.loads(p.read_bytes()) for p in (qp, op)]; source = q['source']
    pp = W/'pg6500-web-owned-component-qualification-v5/manifest.safe.json'; cp = pp.with_name('cases.safe.json')
    if sha(pp) != q['privateManifestSha256'] or sha(cp) != q['casesSha256']:
        raise ValueError('immutable original all source/class/XML receipt')
    proof, cases = [json.loads(p.read_bytes()) for p in (pp, cp)]
    if not (q['actualExit'] == order['actualExit'] == 0 and order['source'] == source
            and (q['tests'], q['suites'], q['physicalMain']) == (27,11,1667)
            and order['qualificationSha256'] == QSHA and order['bootstrapHandlesAndAllArgumentsResolved']
            and proof['allPhysicalMainSha256']['web:'+MAIN.split('/src/main/java/')[1][:-5]+'.class'] == order['classSha256']):
        raise ValueError('same original source/component and full physical owner/JVM identity')
    text = (ROOT/MAIN).read_text()
    if sha(ROOT/MAIN) != proof['allSourceHashes'][MAIN] or sha(ROOT/TEST) != sha(W/'pg6498-web-owned-component-v5/source'/TEST):
        raise ValueError('current Main and independent Test bytes fixed')
    rows = load(BASE/'PG6502-current4064-static-plan-v1/manifest.json', PLAN_SHA, source)
    decisions = []; seen = Counter()
    for row in rows:
        if row['sourcePath'] != MAIN: continue
        if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or row['sourceSha256'] != sha(ROOT/MAIN):
            raise ValueError('fresh changed-source warning only')
        key = site(row, text); reason, methods = SITES[key]; seen[key] += 1
        refs = [r for r in cases if r['className'] == 'dev.codex.schubert.nk.web.bootstrap.WebNativeRuntimeOwnedComponentTest'
                and any(r['method'].startswith('webown327'+number) for number in methods)]
        if len(refs) != len(methods) or any(r['source'] != source or r['result'] != 'PASS_ORIGINAL_XML' for r in refs):
            raise ValueError('explicit current actual method/XML references per warning')
        decisions.append(dict(row, source=source, status='REQUIRED_CONTRACT', reason=reason,
            diagnosticFragment=fragment(text, row), rawWarningRetained=True,
            owningPhysicalClassHashes={'web:'+MAIN.split('/src/main/java/')[1][:-5]+'.class':order['classSha256']},
            originalSelectedQualificationSha256=QSHA, originalSelectedCaseRefs=refs,
            independentTestSourceSha256=sha(ROOT/TEST), jvmOwnershipProofSha256=ORDER_SHA,
            staticContextPremiseOnly=False, currentWholeCaseRefs=[], currentWholeJoinPending=True,
            selectedComponentOnly=True, actualRuntimeProven=False, nativeRootOrAuthorizationProven=False,
            formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0))
    if seen != Counter({k:1 for k in SITES}) or len(decisions) != 12:
        raise ValueError('all five volatile/two private locks/five borrowed aliases individually reviewed')
    updated = apply_decisions(rows, decisions)
    return decisions, dict(actualExit=0, source=source, rawFindings=1361, reviewed=12,
        baseManifestPath='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG6502-current4064-static-plan-v1/manifest.json',
        baseManifestSha256=PLAN_SHA, statusCounts=dict(Counter(r['status'] for r in updated)),
        original27QualificationSha256=QSHA, jvmProofSha256=ORDER_SHA,
        currentWholeJoinPending=True, heldOtherUnreviewed=11, testsExecuted=0, buildsIssued=0,
        pmdRawRemoved=0, newAcceptedLeaves=0, formalAccepted=False, F03Accepted=False,
        ptAlternativeCompleted=0, effortPercent=None)


def main():
    decisions, value = calculate(); os.umask(0o077)
    out = BASE/'PG6504-web-owned-semantic-review-v1'; out.mkdir()
    with (out/'decisions.json').open('x') as f:
        json.dump(decisions, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value['decisionsSha256'] = sha(out/'decisions.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=12, statusCounts=value['statusCounts'], manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__': main()
