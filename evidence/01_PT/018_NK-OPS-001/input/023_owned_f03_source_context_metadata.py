"""Metadata-only binding of individually authored F03 source decisions; no Java execution."""
from pathlib import Path
import collections
import datetime
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
RAW = BASE / 'PG19744-current-six-main-static-repaired-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
load = lambda p: json.loads(Path(p).read_text())


def prior(config):
    spec = importlib.util.spec_from_file_location('normal', ROOT / 'evidence/01_PT/018_NK-OPS-001/input/014_owned_current_main_static_repaired.py')
    normal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(normal)
    normal.read_inputs()
    assert sha(RAW / 'manifest.json') == 'cef691f454c1324bf16bd01948dbc9f0ed5b2091acb7da5f5817b0a48e9f7d7b'
    rows = []
    for item in config['priorManifests']:
        p = ROOT / item['path']
        assert sha(p) == item['sha256']
        rows.extend(load(p.parent / 'review.json')['classified'])
    assert len(rows) == len({r['rawOrdinal'] for r in rows}) == config['priorCount']
    return rows


def source_inputs(config):
    contexts = []
    for item in config['sourceContexts']:
        p = ROOT / item['path']
        assert sha(p) == item['sha256']
        lines = p.read_text().splitlines()
        spans = []
        for first, last in item['ranges']:
            assert 1 <= first <= last <= len(lines)
            spans.append({'firstLine': first, 'lastLine': last, 'lines': lines[first - 1:last]})
        contexts.append(dict(item, spans=spans))
    refs = []
    for item in config['designReferences']:
        p = ROOT / item['path']
        data = subprocess.check_output(['git', 'show', 'origin/main:' + item['path']])
        assert sha(p) == hashlib.sha256(data).hexdigest() == item['sha256']
        refs.append(dict(item, text=data.decode().splitlines()[item['line'] - 1]))
    return contexts, refs


def scoped_partitions(config, previous, current, remaining, raw):
    """BUG2316: exact scoped raw IDs and rule counts, independent of prose totals."""
    old = {r['rawOrdinal'] for r in previous}
    selected = {r['rawOrdinal'] for r in current}
    rest = {r['rawOrdinal'] for r in remaining}
    results = []
    for item in config.get('requiredScopedPartitions', []):
        before = {i for i, f in enumerate(raw) if i not in old and f['path'] == item['path']}
        chosen = before & selected
        after = before & rest
        assert before == set(item['beforeOrdinals'])
        assert chosen == set(item['selectedOrdinals'])
        assert after == set(item['remainingOrdinals'])
        assert not chosen & after and chosen | after == before
        counts = dict(collections.Counter(raw[i]['rule'] for i in after))
        assert counts == item['remainingRuleCounts']
        results.append({'path': item['path'], 'beforeCount': len(before), 'selectedCount': len(chosen), 'remainingCount': len(after), 'remainingRuleCounts': counts, 'exactOrdinalsVerified': True})
    return results


def historical_bindings(rows):
    """Verify immutable old source-context facts, never transfer runtime qualification."""
    count = 0
    for row in rows:
        for fact in row.get('sourceAssertions', []):
            p = ROOT / fact['path']
            assert sha(p) == fact['sha256']
            assert p.read_text().splitlines()[fact['line'] - 1].strip() == fact['text']
        item = row.get('historicalStaticReview')
        if item is None:
            continue
        p, m = ROOT / item['path'], ROOT / item['manifestPath']
        assert sha(p) == item['sha256'] and sha(m) == item['manifestSha256']
        manifest = load(m)
        files = manifest.get('files')
        hash_key = item.get('manifestHashKey', 'reviewSha256')
        assert hash_key in ['reviewSha256', 'purposesSha256']
        assert manifest.get(hash_key) == sha(p) or (isinstance(files, dict) and files.get('review.json') == sha(p))
        old = load(p)
        for part in item['rowPointer']:
            old = old[part]
        finding = row['rawFinding']
        assert old['path'] == finding['path'] and old['rule'] == finding['rule']
        assert old['attributes'] == finding['attributes']
        assert old.get('sourceSha256', old.get('inputSha256')) == finding['sourceSha256']
        reason_key = item.get('historicalReasonKey', 'reason')
        assert reason_key in ['reason', 'manualPurpose']
        assert old[reason_key] == item['historicalReason']
        assert item['runtimeTransferred'] is False
        monitor = row.get('privateMonitorEvidence')
        if monitor is not None:
            lines = (ROOT / finding['path']).read_text().splitlines()
            assert lines[monitor['declarationLine'] - 1].strip() == monitor['declaration']
            assert re.search(r'private\s+final\s+Object\s+' + re.escape(monitor['identifier']) + r'\s*=\s*new Object\(\)', monitor['declaration'])
            assert re.search(r'synchronized\s*\(\s*' + re.escape(monitor['identifier']) + r'\s*\)', lines[int(finding['attributes']['beginline']) - 1])
        count += 1
    return count


def run(config, slot, public):
    assert not slot.exists() and not public.exists()
    previous = prior(config)
    contexts, refs = source_inputs(config)
    raw = load(RAW / 'findings.json')
    rows = []
    old = {r['rawOrdinal'] for r in previous}
    paths = {c['path']: c['sha256'] for c in contexts}
    for decision in config['decisions']:
        i = decision['rawOrdinal']
        f = raw[i]
        assert i not in old and f['rule'] == decision['rule']
        assert paths[f['path']] == f['sourceSha256'] == decision['sourceSha256']
        if 'attributeValues' in decision:
            assert decision['attributeValues']
            assert all(f['attributes'][k] == v for k, v in decision['attributeValues'].items())
        else:
            assert f['attributes']['variable'] == decision['variable']
        assert int(f['attributes']['beginline']) == decision['line']
        assert decision['reason'] and decision['requiredDynamicPostconditions']
        rows.append(dict(decision, id=f'{i:06d}:' + hashlib.sha256(canon(f)).hexdigest(), rawFinding=f, classification='CONTEXTUAL_NONAPPLICABLE', actualViolation=False, runtimeProven=False, ptExempt=False, newWbsAcceptance=False))
    assert len(rows) == len({r['rawOrdinal'] for r in rows}) == config['newCount']
    historical_bindings(rows)
    selected = old | {r['rawOrdinal'] for r in rows}
    remaining = [{'rawOrdinal': i, 'id': f'{i:06d}:' + hashlib.sha256(canon(f)).hexdigest(), 'rawFinding': f, 'applicability': 'UNCLASSIFIED', 'actualViolation': None} for i, f in enumerate(raw) if i not in selected]
    assert len(remaining) == 1491 - config['priorCount'] - config['newCount']
    partitions = scoped_partitions(config, previous, rows, remaining, raw)
    result = {'source': config['mainSource'], 'classified': rows, 'remaining': remaining, 'sourceContexts': contexts, 'canonicalDesignReferences': refs, 'deferred': config['deferred'], 'scopedPartitions': partitions, 'productExecuted': False, 'coverageMeasured': False, 'rawGateUnchanged': 1, 'actualApplicableViolations': None, 'wholeF03Accepted': False, 'whole451Accepted': False}
    slot.mkdir()
    (slot / 'review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    manifest = {'actualExit': 0, 'source': config['mainSource'], 'atJST': datetime.datetime.now().astimezone().isoformat(), 'driverSha256': sha(__file__), 'configSha256': sha(sys.argv[2]), 'reviewSha256': sha(slot / 'review.json'), 'orchestrationHead': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'newContext': len(rows), 'combinedReviewed': len(selected), 'remaining': len(remaining), 'productExecuted': False, 'newAcceptance': 0}
    (slot / 'manifest.safe.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'new': len(rows), 'remaining': len(remaining)}))


def post(config, slot, public):
    manifest = load(slot / 'manifest.safe.json')
    value = load(slot / 'review.json')
    assert manifest['actualExit'] == 0 and manifest['driverSha256'] == sha(__file__)
    assert manifest['configSha256'] == sha(sys.argv[2]) and manifest['reviewSha256'] == sha(slot / 'review.json')
    previous = prior(config)
    contexts, refs = source_inputs(config)
    assert value['sourceContexts'] == contexts and value['canonicalDesignReferences'] == refs
    rows = value['classified']
    expected = {r['rawOrdinal']: r for r in config['decisions']}
    assert len(rows) == len(expected) == config['newCount']
    for row in rows:
        decision = expected[row['rawOrdinal']]
        assert all(row[k] == v for k, v in decision.items())
        assert not row['ptExempt'] and not row['runtimeProven']
    historical_bindings(rows)
    allrows = previous + rows + value['remaining']
    raw = load(RAW / 'findings.json')
    indexed = {r['rawOrdinal']: r for r in allrows}
    assert len(allrows) == len(indexed) == len({r['id'] for r in allrows}) == len(raw) == 1491
    assert set(indexed) == set(range(1491))
    for i, finding in enumerate(raw):
        assert indexed[i]['rawFinding'] == finding
        assert indexed[i]['id'] == f'{i:06d}:' + hashlib.sha256(canon(finding)).hexdigest()
    assert value['scopedPartitions'] == scoped_partitions(config, previous, rows, value['remaining'], raw)
    counts = collections.Counter(canon(f) for f in raw)
    assert len(counts) == 1439 and sum(c == 2 for c in counts.values()) == 52 and max(counts.values()) == 2
    assert {r['rawOrdinal'] for r in config['deferred']} <= {r['rawOrdinal'] for r in value['remaining']}
    assert not public.exists()
    public.mkdir(parents=True)
    for p in slot.iterdir():
        if p.is_file():
            shutil.copyfile(p, public / p.name)
    output = dict(manifest, independentPostReconstruction=True, allOriginalOrdinalsExact=True, disjointPartition1491=True, duplicateGroupsPreserved=52, files={p.name: sha(p) for p in public.iterdir() if p.is_file()})
    (public / 'manifest.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'new': len(rows), 'combined': config['priorCount'] + len(rows), 'remaining': len(value['remaining']), 'manifestSha256': sha(public / 'manifest.json')}))


def requalify(config):
    """Rebind exact immutable per-site source facts to a fresh changed-source report."""
    spec = importlib.util.spec_from_file_location('normal_current', ROOT / 'evidence/01_PT/018_NK-OPS-001/input/014_owned_current_main_static_repaired.py')
    normal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(normal)
    normal.configure('evidence/01_PT/018_NK-OPS-001/input/050_current_d8_main_static.json')
    normal.read_inputs()
    def pinned(item):
        p = ROOT / item['path']
        assert sha(p) == item['sha256']
        return p, load(p)
    fresh_path, fresh = pinned(config['freshManifest'])
    old_path, old = pinned(config['historicalManifest'])
    assert fresh['normalSource'] == config['mainSource'] and fresh['analysisComplete'] and fresh['allMainSpotbugsClassSetsExact']
    assert fresh['productTestsExecuted'] == 0 and fresh['testSourceCount'] == 0 and not fresh['processingErrors']
    for name, digest in fresh['files'].items():
        assert sha(fresh_path.parent / name) == digest
    for name, digest in old['files'].items():
        assert sha(old_path.parent / name) == digest
    raw = load(fresh_path.parent / 'findings.json')
    prior_raw = load(old_path.parent / 'findings.json')
    log = config['changedMainPath']
    changed = [p for p, h in old['sourceInputHashes'].items() if fresh['sourceInputHashes'].get(p) != h]
    assert changed == [log] and len(fresh['sourceInputHashes']) == len(old['sourceInputHashes']) == 966
    assert collections.Counter(canon(f) for f in raw if f['path'] != log) == collections.Counter(canon(f) for f in prior_raw if f['path'] != log)
    by_fact = collections.defaultdict(collections.deque)
    for i, f in enumerate(raw):
        if f['path'] != log:
            by_fact[canon(f)].append(i)
    rows, old_ordinals, designs = [], set(), {}
    def span(lines, item):
        assert lines[item['firstLine'] - 1:item['lastLine']] == item['lines']
    for item in config['historicalReviews']:
        mp, manifest = pinned(item)
        review_path = mp.parent / 'review.json'
        review = load(review_path)
        assert manifest.get('reviewSha256') == sha(review_path) or manifest.get('files', {}).get('review.json') == sha(review_path)
        for context in review.get('sourceContexts', []):
            if context['path'] == log:
                continue
            assert sha(ROOT / context['path']) == context['sha256']
            lines = (ROOT / context['path']).read_text().splitlines()
            for section in context.get('spans', []):
                span(lines, section)
        for ref in review.get('canonicalDesignReferences', []):
            current = subprocess.check_output(['git', 'show', 'origin/main:' + ref['path']])
            assert sha(ROOT / ref['path']) == hashlib.sha256(current).hexdigest()
            previous = subprocess.check_output(['git', 'show', config['historicalSource'] + ':' + ref['path']])
            assert hashlib.sha256(previous).hexdigest() == ref['sha256']
            assert current == previous or (ref['path'] == config['appendedDesignPath'] and current.startswith(previous))
            line = current.decode().splitlines()[ref['line'] - 1]
            assert line == ref['text']
            designs[(ref['path'], ref['line'])] = dict(path=ref['path'], line=ref['line'], text=line, currentSha256=hashlib.sha256(current).hexdigest(), historicalSha256=ref['sha256'], exactOrAppendOnly=True)
        for row in review['classified']:
            ordinal = row['rawOrdinal']
            assert ordinal not in old_ordinals and row['rawFinding'] == prior_raw[ordinal]
            old_ordinals.add(ordinal)
            assert row['id'] == f'{ordinal:06d}:' + hashlib.sha256(canon(row['rawFinding'])).hexdigest()
            if row['rawFinding']['path'] == log:
                continue
            f = row['rawFinding']
            assert row['classification'] == 'CONTEXTUAL_NONAPPLICABLE' and row['actualViolation'] is False and row['ptExempt'] is False and row['runtimeProven'] is False and row['reason']
            assert sha(ROOT / f['path']) == f['sourceSha256']
            lines = (ROOT / f['path']).read_text().splitlines()
            if 'sourceContext' in row:
                span(lines, row['sourceContext'])
            for declaration in row.get('ownerDeclarations', []):
                assert lines[declaration['line'] - 1] == declaration['text']
            historical_bindings([row])
            index = by_fact[canon(f)].popleft()
            rows.append(dict(rawOrdinal=index, id=f'{index:06d}:' + hashlib.sha256(canon(f)).hexdigest(), rawFinding=f, classification='CONTEXTUAL_NONAPPLICABLE', actualViolation=False, reason=row['reason'], historicalRow=dict(manifestPath=item['path'], manifestSha256=item['sha256'], reviewSha256=sha(review_path), rawOrdinal=ordinal, id=row['id']), exactCurrentSourceVerified=True, runtimeTransferred=False, ptExempt=False))
    assert len(old_ordinals) == 1490 and len(rows) == 1464 and not any(by_fact.values())
    lp, lm = pinned(config['logReviewManifest'])
    log_review = load(lp.parent / 'review.json')
    assert sha(lp.parent / 'review.json') == lm['reviewSha256']
    remaining_log = collections.defaultdict(collections.deque)
    for item in log_review:
        if item['path'] == log:
            remaining_log[canon(item['finding'])].append(item)
    for index, f in enumerate(raw):
        if f['path'] != log:
            continue
        finding = dict(f['attributes'], message=f['message'])
        item = remaining_log[canon(finding)].popleft()
        assert item['sourceSha256'] == f['sourceSha256'] == sha(ROOT / log)
        assert (ROOT / log).read_text().splitlines()[int(f['attributes']['beginline']) - 1].strip() == item['lineText'].strip()
        assert item['reason'] and item['classification'] == 'CONTEXTUAL_NONAPPLICABLE'
        rows.append(dict(rawOrdinal=index, id=f'{index:06d}:' + hashlib.sha256(canon(f)).hexdigest(), rawFinding=f, classification='CONTEXTUAL_NONAPPLICABLE', actualViolation=False, reason=item['reason'], currentLogReview=dict(manifestPath=config['logReviewManifest']['path'], sha256=config['logReviewManifest']['sha256'], ordinal=item['ordinal']), runtimeTransferred=False, ptExempt=False))
    assert not any(remaining_log.values()) and len(rows) == len(raw) == 1494
    assert {x['rawOrdinal'] for x in rows} == set(range(len(raw)))
    unit_path, unit = pinned(config['logUnitManifest'])
    assert unit['actualExit'] == 0 and unit['productionCoreMain'] == config['mainSource'] and unit['tests'] == 19 and all(unit[k] == 0 for k in ['failures', 'errors', 'skipped', 'aborted'])
    assert unit['inputHashes'][log] == fresh['sourceInputHashes'][log]
    multiplicity = collections.Counter(canon(f) for f in raw)
    return dict(source=config['mainSource'], rawCount=len(raw), currentReviewed=len(rows), unchangedOtherMainReviewed=1464, changedLogReviewed=30, canonicalUnique=len(multiplicity), duplicateGroups=sum(n > 1 for n in multiplicity.values()), rawMultiplicityPreserved=True, classified=sorted(rows, key=lambda x:x['rawOrdinal']), canonicalDesignReferences=list(designs.values()), sourceSetOnlyChanged=[log], rawGateUnchanged=fresh['rawGateExit'], styleApplicableViolations=0, individualReviewOnly=True, suppressed=0, productExecuted=False, coverageMeasured=False, runtimeTransferred=False, wholeF03Accepted=False, whole451Accepted=False, formalUpdated=False, newAccepted=0, safetyHoldsUnchanged=True)


def requal_run(config, slot, public):
    assert not slot.exists() and not public.exists()
    value = requalify(config)
    slot.mkdir()
    (slot / 'review.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    manifest = dict(actualExit=0, source=config['mainSource'], atJST=datetime.datetime.now().astimezone().isoformat(), driverSha256=sha(__file__), configSha256=sha(sys.argv[2]), reviewSha256=sha(slot / 'review.json'), raw=1494, reviewed=1494, remaining=0, newAccepted=0, wholeF03Accepted=False, whole451Accepted=False, productExecuted=False, coverageMeasured=False)
    (slot / 'manifest.safe.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, reviewed=1494, remaining=0)))


def requal_post(config, slot, public):
    m = load(slot / 'manifest.safe.json')
    assert m['actualExit'] == 0 and m['driverSha256'] == sha(__file__) and m['configSha256'] == sha(sys.argv[2]) and m['reviewSha256'] == sha(slot / 'review.json')
    assert load(slot / 'review.json') == requalify(config)
    assert not public.exists()
    public.mkdir()
    for p in slot.iterdir():
        shutil.copyfile(p, public / p.name)
    m = dict(m, independentPostReconstruction=True, files={p.name:sha(p) for p in public.iterdir()})
    (public / 'manifest.json').write_text(json.dumps(m, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, reviewed=1494, remaining=0, manifestSha256=sha(public / 'manifest.json'))))


if __name__ == '__main__' and len(sys.argv)==3 and sys.argv[1] in ['requal-run','requal-post']:
    assert sys.argv[2]=='evidence/01_PT/018_NK-OPS-001/input/051_current_d8_source_requalification.json'
    config=load(sys.argv[2]);assert config['mainSource']=='d8ff9efb16a7da1b073bdf9770487e3e6415b636'
    assert config['slot']=='pg20154-current-d8-context-requalification-v1' and config['publicName']=='PG20154-current-d8-context-requalification-v1'
    slot=ROOT.parent/'pgpt-runs/PG379'/config['slot'];public=BASE/config['publicName']
    (requal_run if sys.argv[1]=='requal-run' else requal_post)(config,slot,public)
    raise SystemExit(0)

if __name__ == '__main__':
    assert len(sys.argv) == 3 and sys.argv[1] in ['run', 'post']
    config = load(sys.argv[2])
    assert config['mainSource'] == '28af318d0198fe7432ca6fcd234d3fabbfd10173'
    slot = ROOT.parent / 'pgpt-runs/PG379' / config['slot']
    public = BASE / config['publicName']
    (run if sys.argv[1] == 'run' else post)(config, slot, public)
