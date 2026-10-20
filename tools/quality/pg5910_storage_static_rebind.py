"""Reauthenticate exactly528 unchanged reasons; no old3973 PASS imported as current."""
import inspect
import copy
import json
from collections import defaultdict
import pg5784_current_static_rebind as previous
from static_disposition_overlay import load

SOURCE = '7a664ce0a99860bb75e1e1a3ae30354a9840528a'
OLD_SOURCE = '79098cfa553d38cb6032c28d8722394e59c39966'
SEMANTIC = ('sourcePath', 'sourceSha256', 'rule', 'beginline', 'endline', 'begincolumn',
            'endcolumn', 'priority', 'diagnosticTextSha256', 'identitySchema', 'legacyFindingId')


def ordered_pairs(old, current):
    """Pair full, equal source-local diagnostic sequences, not first equal candidates."""
    if any(len({r['findingId'] for r in rows}) != len(rows) for rows in (old, current)):
        raise ValueError('one actual diagnostic ID per raw occurrence')
    left, right = defaultdict(list), defaultdict(list)
    for row in old:
        left[row['sourcePath']].append(row)
    for row in current:
        right[row['sourcePath']].append(row)
    result = {}
    for path, values in right.items():
        before = left[path]
        if len(before) != len(values) or any(tuple(a[k] for k in SEMANTIC) != tuple(b[k] for k in SEMANTIC) for a, b in zip(before, values)):
            continue
        for rank, (a, b) in enumerate(zip(before, values), 1):
            result[b['findingId']] = (a, rank)
    return result


def binder(pairs):
    def bind(row, candidates, raw, before, current):
        pair = pairs.get(row['findingId'])
        matches = [] if pair is None else [r for r in candidates if r['findingId'] == pair[0]['findingId']]
        value, kind = previous.bind_one(row, matches, raw, before, current)
        if kind == 'REBOUND':
            value = copy.deepcopy(value)
            value.update(priorRawXmlOrdinal=pair[0]['rawXmlOrdinal'], sourceFileOccurrenceRank=pair[1],
                         diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE')
        return value, kind
    return bind


def reader_source():
    raw = inspect.getsource(previous.main)
    changes = {
        'PG5772-primary-capture27-v1/manifest.json': 'PG5902-current-static3973-v1/manifest.json',
        'b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487': '1bf8bfdf27d65ecf416ae76ca0b6b30dfc0158e5b1c7d28b148a788c02489521',
        'PG5754-current3932-cases/qualification.json': 'PG5886-current3973-cases/qualification.json',
        'ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18': '2045f1a9eb4eb60f2f470442bfbd3774f2925ce17cc88b5875d16f1163778d7f',
        'PG5776-jms-primary-static-v1/manifest.json': 'PG5906-storage30-static-v1/manifest.json',
        'aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f': 'a0c4d80e21a1a20a05928d26a35168be6802aa01e2bc8a682bb6e49959ca5365',
        '207c64bdb95dedd001056d79318acf1ff6c53ec00b7c17d55e3ba3bd9530c186': '25bca31961c97c84386e0764c005ac4a341ac66241f29a9425722b15a8b8ff40',
        'pg5776-jms-primary-static-v1/manifest.safe.json': 'pg5906-storage30-static-v1/manifest.safe.json',
        "if len(rows)!=1585 or len(used)!=472 or len(held)!=1 or not held[0]['sourcePath'].endswith('/ArtemisReplyConsumer.java')or held[0]['rule']!='CompareObjectsWithEquals':raise ValueError('only exact472 unchanged and one moved/changed owner scope held')": "if len(rows)!=1556 or len(used)!=528 or held:raise ValueError('all528 require exact entire source/coordinates/diagnostic identity/all owner bytes')",
        "len({r['findingId']for r in rows})!=1585": "len({r['findingId']for r in rows})!=1556",
        "'currentRawFindings':1585": "'currentRawFindings':1556"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one exact current storage528 binding: ' + old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<storage528 unchanged roots>', 'exec')
    return raw


def main():
    old = load(previous.BASE / 'PG5902-current-static3973-v1/manifest.json', '1bf8bfdf27d65ecf416ae76ca0b6b30dfc0158e5b1c7d28b148a788c02489521', OLD_SOURCE)
    path = previous.BASE / 'PG5906-storage30-static-v1/findings.json'
    if previous.sha(path) != '25bca31961c97c84386e0764c005ac4a341ac66241f29a9425722b15a8b8ff40':
        raise ValueError('immutable current raw diagnostics')
    pairs = ordered_pairs(old, json.loads(path.read_bytes()))
    scope = {**vars(previous), 'SOURCE': SOURCE, 'OLD_SOURCE': OLD_SOURCE, 'bind_one': binder(pairs),
             'OUT': previous.BASE / 'PG5910-storage-dispositions-v2'}
    exec(compile(reader_source(), '<storage528 unchanged roots>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
