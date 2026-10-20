"""Immutable private-lock PG plan/declared transformations; main() does not modify Production."""
import hashlib
import json
import os
import re
import subprocess
from collections import defaultdict
from pg5540_snapshot_scratch_selected import ROOT, TC, sha
from pg5918_api_static_rebind import SOURCE, W
from static_disposition_overlay import BASE, load

FQ = 'java.util.concurrent.locks.ReentrantLock'


def scalar_positions(text):
    result = {0: 0}; units = 0
    for i, char in enumerate(text):
        units += 2 if ord(char) > 0xffff else 1
        result[units] = i+1
    return result


def transform(text, fields, blocks):
    positions = scalar_positions(text); edits = []
    for field in fields:
        if not field['eligible'] or field['serializableOwner'] or field['superclass'] != 'java.lang.Object' or field['otherReads']:
            raise ValueError('exclusive nonserialized private field with Object parent only')
        for a, b in (('typeStart', 'typeEnd'), ('initStart', 'initEnd')):
            start, end = positions[field[a]], positions[field[b]]
            if text[start:end] not in ('Object', 'java.lang.Object'):
                raise ValueError('exact original Object type/constructor token')
            edits.append((start, end, FQ))
    by_field = {(f['owner'], f['name']): f for f in fields}
    for block in blocks:
        field = by_field.get((block['fieldOwner'], block['name']))
        if field is None or block['parentKind'] != 'BLOCK':
            raise ValueError('statement-list parent required; never split a conditional/labeled statement')
        start, end, body_start, body_end, expr_start, expr_end = (positions[block[k]] for k in ('start', 'end', 'bodyStart', 'bodyEnd', 'expressionStart', 'expressionEnd'))
        expression = text[expr_start:expr_end]
        if re.fullmatch(r'(?:this\.)?'+re.escape(field['name']), expression) is None or re.sub(r'\s', '', text[start:body_start]) != 'synchronized('+expression+')':
            raise ValueError('stable same-this field expression and original unmodified monitor header')
        indent = text[text.rfind('\n', 0, start)+1:start]
        if indent.strip() or text[body_start] != '{' or text[body_end-1] != '}' or body_end != end:
            raise ValueError('exact formatted statement/header/body bounds')
        edits.append((start, body_start, expression+'.lock();\n'+indent+'try '))
        edits.append((body_end, body_end, ' finally {\n'+indent+'  '+expression+'.unlock();\n'+indent+'}'))
    if len({(a, b) for a, b, _s in edits}) != len(edits):
        raise ValueError('one source edit at each declared span')
    previous_end = -1
    for start, end, _ in sorted(edits):
        if start < previous_end or end < start:
            raise ValueError('no overlapping token edits or deleted critical bodies')
        previous_end = end
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start]+replacement+text[end:]
    return text


def formatted(text):
    result = subprocess.run([str(TC/'jdk-25.0.4/bin/java'), '-jar', str(TC/'google-java-format-1.36.1-all-deps.jar'), '--skip-reflowing-long-strings', '-'], input=text, text=True, capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError('pinned source-only formatter must succeed before any Production edit')
    return result.stdout


def select_fields(facts, baseline):
    index = {(r['module'], r['class']): r for r in baseline['targets']}
    chosen, deferred = [], []
    for field in facts['fields']:
        if not field['eligible']:
            continue
        blocks = [b for b in facts['blocks'] if (b['path'], b['fieldOwner'], b['name']) == (field['path'], field['owner'], field['name'])]
        module = field['path'].split('/')[1].removeprefix('schubert-nk-')
        owners = {field['owner']} | {r['blockOwner'] for r in blocks}
        keys = [(module, name.replace('.', '/')) for name in sorted(owners)]
        reason = None
        if field['serializableOwner'] or field['superclass'] != 'java.lang.Object' or field['otherReads']:
            reason = 'SERIALIZATION_PARENT_OR_ALIAS_REQUIRES_SEPARATE_REVIEW'
        elif any(b['parentKind'] != 'BLOCK' for b in blocks):
            reason = 'NON_STATEMENT_LIST_PARENT'
        elif any(k not in index or index[k]['baselineFour100'] is not True for k in keys):
            reason = 'BASELINE_NOT_EXPLICIT_FOUR100; no counter supplementation or exclusion acceptance'
        value = dict(field=field, blocks=blocks, requiredClassKeys=[m+':'+n+'.class' for m, n in keys])
        (deferred if reason else chosen).append(dict(value, reason=reason) if reason else value)
    return chosen, deferred


def main():
    mp = W/'pg5932-private-monitor-facts-v3/manifest.safe.json'; bp = BASE/'PG5936-private-monitor-baseline-v2/manifest.json'
    qp = BASE/'PG5926-current3973-cases/qualification.json'; casesp = qp.with_name('cases.json')
    expected = {mp: '9441602b57a9fdc8416d66655ceff9b2cc42f39edd4d296c544531a716b47143',
                bp: '45a26ebaf0a916f5eb27ab0f4d765b40f630db67347e65f4940ec42c2c6363e0',
                qp: '89bdeed7bf69067bb0a20c766c8e59cbb780d0fd83dffa7e71c9e1255b1115cf',
                casesp: '706d48d8a43c7e80876ecf9fedd6cddf935bb88bba207dc04998015b6bbc0904'}
    if any(sha(p) != value for p, value in expected.items()):
        raise ValueError('immutable current type/all3973/class/coverage inputs')
    meta, baseline, q = (json.loads(p.read_bytes()) for p in (mp, bp, qp))
    if not (meta['source'] == baseline['source'] == q['productionSource'] == SOURCE and meta['actualExit'] == baseline['actualExit'] == 0 and meta['identity']['physicalMainSha256'] == q['allPhysicalMainSha256']):
        raise ValueError('one current source and actual physical Main maps')
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != meta['identity']['sourceHashes']:
        raise ValueError('current original851 Main source fixed before PG')
    overlay = BASE/'PG5934-current-static3973-v1/manifest.json'
    rows = load(overlay, '7b18bc543eaf7be827dd22c78aea321f1bf0bb996dbeedd92b83395b675bcbfb', SOURCE)
    chosen, deferred = select_fields(meta['facts'], baseline)
    if len(chosen) != 33 or len({r['field']['path'] for r in chosen}) != 33 or sum(len(r['blocks']) for r in chosen) != 93:
        raise ValueError('exact planned33 source/field,93 statement-list blocks')
    grouped = defaultdict(list)
    for row in chosen:
        grouped[row['field']['path']].append(row)
    cases = json.loads(casesp.read_bytes()); source_plans = []; ids = set(); targets = set()
    for path, values in sorted(grouped.items()):
        text = (ROOT/path).read_text(); fields = [r['field'] for r in values]; blocks = [b for r in values for b in r['blocks']]
        positions = scalar_positions(text); source_ids = []
        for block in blocks:
            start = positions[block['start']]
            found = []
            for row in rows:
                if row['sourcePath'] != path or row['rule'] != 'AvoidSynchronizedStatement':
                    continue
                offset = sum(map(len, text.splitlines(keepends=True)[:int(row['beginline'])-1]))+int(row['begincolumn'])-1
                if offset == start:
                    found.append(row)
            if len(found) != 1 or found[0]['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or found[0]['sourceSha256'] != sha(ROOT/path) or found[0]['findingId'] in ids:
                raise ValueError('one genuinely unreviewed current PMD span per selected block')
            ids.add(found[0]['findingId']); source_ids.append(found[0]['findingId'])
        module = path.split('/')[1].removeprefix('schubert-nk-'); simple = path.rsplit('/', 1)[1][:-5]
        references = []
        for test in sorted((ROOT/('src/schubert-nk-'+module+'/src/test/java')).rglob('*.java')):
            test_text = test.read_text()
            if re.search(r'\b'+re.escape(simple)+r'\b', test_text) is None:
                continue
            cls = test.relative_to(ROOT/('src/schubert-nk-'+module+'/src/test/java')).as_posix()[:-5].replace('/', '.')
            own_cases = [c for c in cases if c['class'] == cls]
            if own_cases:
                references.append(dict(testSourcePath=test.relative_to(ROOT).as_posix(), testSourceSha256=sha(test), testClass=cls,
                                       baselineCaseIds=[c['testId'] for c in own_cases], sourceReferenceOnlyNotPerTestCoverageAttribution=True))
        required = sorted({k for value in values for k in value['requiredClassKeys']}); targets.update(required)
        predicted = formatted(transform(text, fields, blocks))
        source_plans.append(dict(path=path, module=module, beforeSha256=sha(ROOT/path), predictedAfterSha256=hashlib.sha256(predicted.encode()).hexdigest(),
                                 fields=fields, blocks=blocks, findingIds=source_ids, requiredClassKeys=required,
                                 sourceTraceMarkers=sorted(set(re.findall(r'\b(?:NK-[A-Z]{2,4}-[0-9]{3}|SS[0-9]{3}|UI[0-9]{3}|PT-[A-Z0-9-]+)\b', text))),
                                 existingTestSourceReferences=references, directTestSourceReferenceMissing=not references))
    if len(ids) != 93 or len(targets) != 34:
        raise ValueError('all93 exact warnings and34 actual executable target classes')
    out = BASE/'PG5938-private-lock93-plan-v1'; os.umask(0o077); out.mkdir()
    value = dict(actualExit=0, source=SOURCE, typeFactsSha256=sha(mp), baselineManifestSha256=sha(bp), currentWholeQualificationSha256=sha(qp),
                 sourcePlans=source_plans, selectedSourceFiles=33, selectedPrivateFields=33, selectedMonitorBlocks=93,
                 requiredClassKeys=sorted(targets), deferredEligibleFields=deferred, deferredEligibleMonitorBlocks=sum(len(r['blocks']) for r in deferred),
                 otherUnreviewedMonitorBlocks=25, totalUnreviewedMonitorBlocks=154, formatterSha256=sha(TC/'google-java-format-1.36.1-all-deps.jar'),
                 newProductionCodeApplied=False, ptCasesAdded=0, oldBaselineIsNotNewSourcePt=True, ptAlternativeCompleted=0, formalAccepted=False, F03Accepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, selectedSourceFiles=33, selectedPrivateFields=33, selectedMonitorBlocks=93,
                         targets=34, deferredEligibleMonitorBlocks=value['deferredEligibleMonitorBlocks'],
                         missingDirectTestSourceReference=[r['path'] for r in source_plans if r['directTestSourceReferenceMissing']],
                         manifestSha256=sha(out/'manifest.json'), productionCodeChanged=False)))


if __name__ == '__main__':
    main()
