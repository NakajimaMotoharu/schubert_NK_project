"""Record a source-only review; native/callback uncertainty is never a PMD waiver."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

r = Path.cwd()
b = r / 'evidence/01_PT/018_NK-OPS-001'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ref = lambda p: dict(path=str(p.relative_to(r)), sha256=sha(p))
before = load(b / 'evidence/PG37084-f03-specific-lifetime83-applicability-v1/remaining-unmatched.json')
facts_path = r.parent / 'pgpt-runs/PG379/pg37074-sync54-structural-facts.json'
facts = {x['rawFindingIndex']: x for x in load(facts_path)}
selected = [x for x in before if x['raw']['rule'] == 'AvoidSynchronizedStatement']
assert len(selected) == 39 and len({x['rawFindingIndex'] for x in selected}) == 39
ordinary = {'BatchMetricRecorder', 'MonitoringObservationClock', 'MonitoringPoller'}
rows = []
for original in selected:
    f = facts[original['rawFindingIndex']]
    p = r / original['raw']['path']
    text = p.read_text()
    assert sha(p) == original['sourceSha256'] == f['sourceSha256']
    assert f['fullBody'] in text
    stem = p.stem
    declaration = 'private final Object ' + f['monitor']
    assert declaration in text
    if stem in {'BackupUnitStartClient', 'MaintenanceUnitStopClient'}:
        assert 'Object stateLock = new Object();' in text
        owner = 'factory-local new Object passed into private handle state; not a caller-provided monitor'
    else:
        assert re.search(r'private final Object\s+' + f['monitor'] + r'\s*=\s*new Object\(\)', text)
        owner = 'private final instance-created Object; no caller-visible this/class monitor'
    planned = stem in ordinary
    rows.append(dict(rawFindingIndex=original['rawFindingIndex'], raw=original['raw'],
                     sourceSha256=sha(p), method=f['method'], monitor=f['monitor'],
                     fullBody=f['fullBody'], bodySha256=hashlib.sha256(f['fullBody'].encode()).hexdigest(),
                     owner=owner,
                     disposition='APPLICABLE_ORDINARY_LOCK_CHANGE_PLANNED' if planned else 'UNRESOLVED_NATIVE_OR_CALLBACK_CONTRACT',
                     reason=('Injected clock/action/registry work can run within the private monitor. '
                             'Preserve atomicity and borrowed ownership with a private final ReentrantLock, '
                             'then qualify original whole ordinary tests plus exceptional unlock/concurrency postconditions.'
                             if planned else
                             'Compound publication/readback/retirement or held resource/client/capture lifetime requires exclusion. '
                             'Private ownership alone does not prove native-frame pinning absent or justify a blanket Java25 waiver. '
                             'Do not alter held paths or claim runtime/source admission from this source review.')))
assert sum(x['disposition'].startswith('APPLICABLE_') for x in rows) == 4
assert sum(x['disposition'].startswith('UNRESOLVED_') for x in rows) == 35
thread_paths = [r / 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform' / x
                for x in ['ConfigurationGroupResolver.java', 'InspectorUnitProbe.java']]
thread_facts = []
for p in thread_paths:
    lines = p.read_text().splitlines()
    sites = [dict(line=i + 1, text=s.strip()) for i, s in enumerate(lines)
             if 'newVirtualThreadPerTaskExecutor(' in s or 'startVirtualThread(' in s]
    assert len(sites) == 1
    thread_facts.append(dict(**ref(p), sites=sites,
                             limitation='The visible task drains a bounded stream. This is not a whole-program no-virtual-caller proof.'))
ss = Path('documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md')
canonical = subprocess.check_output(['git', 'show', 'origin/main:' + str(ss)])
assert canonical == (r / ss).read_bytes()
out = b / 'evidence/PG37206-f03-sync39-source-review-v1'
assert not out.exists()
out.mkdir()
rp = out / 'site-decisions.json'
rp.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
manifest = dict(actualExit=0, terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                sourceCore='fefac4b6c8d14df495deacef39eaade275f1348a',
                sourceHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                rawOriginal=ref(b / 'evidence/PG36960-f03-root-pmd-v1/pmd.xml') if (b / 'evidence/PG36960-f03-root-pmd-v1/pmd.xml').exists() else None,
                selectedOriginal=ref(b / 'evidence/PG37084-f03-specific-lifetime83-applicability-v1/remaining-unmatched.json'),
                independentRows=ref(rp), structuralFactsSha256=sha(facts_path),
                reviewedSites=39, reviewedClasses=12, applicableOrdinarySites=4,
                unresolvedNativeCallbackSites=35, newNotApplicableDispositions=0,
                prior922NotApplicableUnchanged=True, original49NotYetClosed=True,
                canonicalMainSs343Sha256=hashlib.sha256(canonical).hexdigest(),
                codingStandard=ref(r / 'documents/400_PGPT/410_工程標準/411_コーディング規約.md'),
                threadSourceFacts=thread_facts,
                officialRule='https://docs.pmd-code.org/pmd-doc-7.28.0/pmd_rules_java_multithreading.html#avoidsynchronizedstatement',
                changedProductionSources=0, executedProductTests=0, nativeOperations=0,
                changedRulesOrSuppressions=0, newAcceptance=0, formalUpdated=False,
                retainedHolds=['BUG3152 recovery ten catches', 'QA056 four classfiles', 'Root/native/recovery/VM/DB/permit/intent operations'],
                nextProof='Four ordinary synchronization sites: original whole monitoring tests, finite two-thread exclusion and exception-release postconditions, fresh Main compile/static/ABI/raw CRC. Keep35 native/callback sites and recovery10 unresolved.')
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: manifest[k] for k in ['actualExit', 'reviewedSites', 'applicableOrdinarySites', 'unresolvedNativeCallbackSites', 'newAcceptance']}))
