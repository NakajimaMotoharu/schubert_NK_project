"""Reevaluate actual J2EE-premise warnings on current standalone graph; no guest or suppression."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import run, copy
from pmd_contract_disposition import classify_contract
from pg3966_literal_invariant_full_six import ROOT, W, SOURCE, require


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    from pathlib import Path
    b = Path('/home/mini/schubert-nk-pgpt'); sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    prior_path = b / 'runs/PG3992-static-assessment-rebind-v1/manifest.safe.json'
    require(sha(prior_path) == data['priorManifestSha256'], 'actual narrow current220 authority')
    prior = json.loads(prior_path.read_bytes()); require(prior['productionSource'] == data['source'] and prior['rawFindings'] == 1653 and prior['technicalDispositions'] == 220, 'same current-source diagnostic')
    rows_path = prior_path.parent / 'all1653-dispositions.safe.json'; require(sha(rows_path) == prior['allDispositionsSha256'], 'all actual raw1653 retained')
    rows = json.loads(rows_path.read_bytes()); require(len(rows) == 1653, 'no raw warning removed')
    current = b / 'source-full-PG3966'; context = data['context']
    require(context['source'] == data['source'] and len(context['sourceSha256']) == 849 and context['sourceSha256'] == {str(p.relative_to(current)): sha(p) for p in current.glob('src/*/src/main/java/**/*.java')}, 'all actual frozen849 source bound to standalone proof')
    vendor_path = b / 'runs/PG3706-pmd-inventory-v1/vendor-rules.private.json'; require(sha(vendor_path) == data['vendorRulesSha256'], 'primary pinned vendor premise')
    vendor = json.loads(vendor_path.read_bytes()); context['vendorExplicitJ2ee'] = {rule: 'J2EE' in vendor[rule]['description'] for rule in ['DoNotUseThreads', 'UseProperClassLoader']}
    require(all(context['vendorExplicitJ2ee'].values()), 'both actual rule descriptions expressly require J2EE premise')
    q = b / 'runs/PG3968-literal-invariant-whole-qualified-v1/manifest.safe.json'; require(sha(q) == data['qualificationSha256'], 'genuine current3717/1643 qualification')
    original = json.loads(q.read_bytes()); require(original['actualExit'] == 0 and original['productionSource'] == data['source'] and original['tests'] == 3717, 'exact current qualified source')
    checked = []; added = []
    for row in rows:
        if row['rule'] not in context['vendorExplicitJ2ee']: continue
        require(row['disposition'] in {'UNCLASSIFIED', 'CONTEXT_NOT_APPLICABLE_J2EE_RULE'}, 'only same actual context rule decisions may be refreshed')
        decision = classify_contract(row, context, {})
        require(decision and decision['disposition'] == 'CONTEXT_NOT_APPLICABLE_J2EE_RULE' and decision['qualityGatePass'] is False, 'actual approved standalone context, never blanket generic-catch exclusion')
        if row['disposition'] == 'UNCLASSIFIED': added.append(row['id'])
        row.update(decision, currentStandaloneProof={'source': data['source'], 'qualificationSha256': data['qualificationSha256'], 'vendorRulesSha256': data['vendorRulesSha256'], 'architectureSha256': data['contextSha256']})
        checked.append(row['id'])
    require(len(checked) == 239 and len(added) == 67, 'actual238 thread plus1 classloader premise; 172 previous matched scopes rechecked and67 ambiguous textual mappings resolved by actual architecture')
    out = b / 'runs/PG4030-current-standalone-static-v1'; out.mkdir()
    (out / 'all1653-dispositions.safe.json').write_text(json.dumps(rows, sort_keys=True))
    (out / 'architecture.safe.json').write_text(json.dumps(context, sort_keys=True))
    counts = dict(Counter(row['disposition'] for row in rows))
    result = {'actualExit': 0, 'productionSource': data['source'], 'rawFindings': 1653, 'technicalDispositions': 287, 'unclassified': 1366,
              'applicableViolationCount': None, 'currentContextDecisionsRechecked': 239, 'newSourceRequalifiedFromTextuallyHeld': 67, 'historicalNarrowScopesStillHeld': 17,
              'dispositions': counts, 'allDispositionsSha256': sha(out / 'all1653-dispositions.safe.json'), 'architectureSha256': sha(out / 'architecture.safe.json'),
              'priorManifestSha256': data['priorManifestSha256'], 'qualificationSha256': data['qualificationSha256'], 'vendorRulesSha256': data['vendorRulesSha256'],
              'F03Accepted': False, 'formalAccepted': False, 'ruleChanged': False, 'suppressionAdded': False, 'pmdReissued': False, 'guestActions': 0,
              'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    require(counts['UNCLASSIFIED'] == 1366 and sum(counts.values()) == 1653, 'all exact current decisions retained')
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True)); result['serverManifestSha256'] = sha(out / 'manifest.safe.json'); print(json.dumps(result))


def main():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    old = json.loads((W / 'pg3744-pmd-contract-classification-v1/architecture.safe.json').read_bytes())
    docs = old['approvedDocumentSha256']
    for path, expected in docs.items():
        require(sha(ROOT / path) == expected == hashlib.sha256(subprocess.check_output(['git', 'show', 'origin/main:' + path], cwd=ROOT)).hexdigest(), 'unchanged exact approved direct-Java architecture')
    require(not subprocess.check_output(['git', 'diff', '7fffab57a567914956b66452e5e54388642efdec', 'HEAD', '--', 'src/deployment', 'pom.xml', ':(glob)src/*/pom.xml'], cwd=ROOT), 'no container/dependency/deployment change')
    context = {**old, 'source': SOURCE, 'sourceSha256': {str(p.relative_to(ROOT)): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    context['architectureEvidence'] = [{'path': p, 'originMainSha256': h} for p, h in docs.items()]
    q = json.loads((W / 'pg3968-literal-invariant-whole-qualified-v1/manifest.safe.json').read_bytes())
    prior = json.loads((W / 'pg3992-static-assessment-rebind-v1/manifest.safe.json').read_bytes())
    vendor = json.loads((W / 'pg3706-pmd-applicability-inventory-v1/manifest.safe.json').read_bytes())
    data = {'source': SOURCE, 'context': context, 'contextSha256': hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest(),
            'qualificationSha256': q['result']['qualificationManifestSha256'], 'priorManifestSha256': prior['result']['serverManifestSha256'], 'vendorRulesSha256': vendor['result']['vendorRulesSha256']}
    os.umask(0o077); out = W / 'pg4030-current-standalone-static-v1'; out.mkdir()
    script = out / 'review.private.py'; script.write_text('\n'.join(inspect.getsource(fn) for fn in [require, classify_contract, server]) + '\nserver(' + repr(data) + ')\n')
    compile(script.read_text(), '<current standalone exact primary premise>', 'exec')
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG4030-current-standalone-static-v1'
    status, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG4030-current-standalone-static-v1 && mkdir -m700 ' + destination, timeout=30); require(status == 0, 'new-only host assessment')
    status, _ = copy(script, destination + '/', timeout=60); require(status == 0, 'complete assessment source transferred')
    status, output = run('python3 -B ' + destination + '/review.private.py', timeout=120); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'productionSource': SOURCE, 'payloadSha256': sha(script), 'F03Accepted': False}
    if status == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return status


if __name__ == '__main__': raise SystemExit(main())
