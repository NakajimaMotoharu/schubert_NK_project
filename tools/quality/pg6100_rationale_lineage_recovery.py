"""Recover lost review text only through immutable exact diagnostic ancestry; never infer PT success."""
import json
import os
from collections import Counter
from pg5940_private_lock_compile import BASE, sha
from pg5910_storage_static_rebind import SEMANTIC
from static_disposition_overlay import load

OLD_SOURCE = 'c4d0242abe53fa7916451ac22caffcdfc13d82b6'
OLD_SHA = '2f123f32ded4e8072de3f137f0faf98aabf7ed39e5601e7514a9228caa2c8c2a'
OLD_ROWS_SHA = 'efcf04c868453946ce2fd3c625d30b0d4374e12a3edc4108193725007335112f'


def reason_of(row):
    return next((v for v in (row.get('reason'), row.get('priorReason')) if isinstance(v, str) and v.strip()), None)


def disposition(row):
    return row.get('priorDisposition') if row.get('status') == 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' else row.get('status')


def recover(row, fetch):
    original = row; current = row; hops = []; seen = set()
    for _ in range(64):
        why = reason_of(current)
        if why is not None:
            return why, hops
        digest, ident = current.get('priorReviewManifestSha256'), current.get('priorFindingId')
        if not isinstance(digest, str) or not isinstance(ident, str) or (digest, ident) in seen:
            raise ValueError('missing or cyclic declared rationale ancestry')
        seen.add((digest, ident)); parent, receipt = fetch(digest, ident)
        if any(parent.get(k) != original.get(k) for k in SEMANTIC):
            raise ValueError('ancestor source/diagnostic/span changed; fresh review required')
        if disposition(parent) != disposition(original) or disposition(parent) not in ('REQUIRED_CONTRACT', 'FALSE_POSITIVE', 'CONTEXT_NOT_APPLICABLE'):
            raise ValueError('ancestor classification not the same reviewed obligation')
        hops.append(dict(manifestSha256=digest, findingId=ident, **receipt))
        current = parent
    raise ValueError('rationale ancestry exceeds explicit64 limit')


class Inventory:
    def __init__(self):
        self.paths = {}; self.cache = {}
        for path in BASE.glob('PG*/manifest.json'):
            if path.is_symlink() or not path.is_file():
                continue
            self.paths.setdefault(sha(path), []).append(path)

    def fetch(self, digest, ident):
        if digest not in self.cache:
            choices = self.paths.get(digest, [])
            if len(choices) != 1:
                raise ValueError('one immutable declared parent manifest')
            path = choices[0]; value = json.loads(path.read_bytes())
            if value.get('actualExit') != 0 or sha(path) != digest:
                raise ValueError('genuine parent manifest with matching hash')
            key = 'inventorySha256' if value.get('inventoryFile') == 'findings.json' else 'findingsSha256'
            rows_path = path.with_name('findings.json')
            if key in value:
                if rows_path.is_symlink() or not rows_path.is_file() or sha(rows_path) != value[key]:
                    raise ValueError('parent complete inventory hash')
                rows = json.loads(rows_path.read_bytes())
            else:
                rows = load(path, digest, value['source'])
            if Counter(r['status'] for r in rows) != Counter(value['statusCounts']):
                raise ValueError('parent complete status inventory')
            index = {r['findingId']: r for r in rows}
            if len(index) != len(rows):
                raise ValueError('one row for each diagnostic occurrence')
            receipt = dict(manifestPath=path.relative_to(BASE).as_posix(), reviewSource=value['source'],
                           inventorySha256=value.get(key), parentClassificationOnly=True)
            self.cache[digest] = index, receipt
        index, receipt = self.cache[digest]
        if ident not in index:
            raise ValueError('explicit prior finding id absent; no matching-by-guess')
        return index[ident], receipt


def main():
    path = BASE/'PG6068-current-static3979-v1/manifest.json'; rows_path = path.with_name('findings.json')
    if sha(path) != OLD_SHA or sha(rows_path) != OLD_ROWS_SHA:
        raise ValueError('original published c4 review inventory retained exactly')
    original = json.loads(rows_path.read_bytes())
    missing = [r for r in original if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' and reason_of(r) is None]
    if len(missing) != 431:
        raise ValueError('exact observed431 missing reasons,not a new acceptance estimate')
    inventory = Inventory(); restored, unresolved = [], []
    for row in missing:
        try:
            why, hops = recover(row, inventory.fetch)
        except ValueError as failure:
            unresolved.append(dict(findingId=row['findingId'], sourcePath=row['sourcePath'], reason=str(failure),
                                   newStatus='NOT_REVIEWED_CURRENT_SOURCE'))
        else:
            if not hops:
                raise ValueError('missing current text requires actual parent evidence')
            restored.append(dict(findingId=row['findingId'], sourcePath=row['sourcePath'], sourceSha256=row['sourceSha256'],
                status=row['status'], reason=why, ancestry=hops, reviewSource=OLD_SOURCE,
                metadataRestorationOnly=True, currentSourceRebindPending=True, originalPublishedRowUnchanged=True))
    if len(restored)+len(unresolved) != 431:
        raise ValueError('each affected row restored or explicitly withdrawn,not silently counted')
    os.umask(0o077); out = BASE/'PG6100-rationale-lineage-v1'; out.mkdir()
    for filename, value in (('restorations.json', restored), ('unresolved.json', unresolved)):
        with (out/filename).open('x') as f:
            json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    result = dict(actualExit=0, originalReviewSource=OLD_SOURCE, originalManifestSha256=OLD_SHA,
        originalInventorySha256=OLD_ROWS_SHA, missingReasons=431, restored=len(restored), unresolved=len(unresolved),
        restorationsSha256=sha(out/'restorations.json'), unresolvedSha256=sha(out/'unresolved.json'),
        maximumAncestryHops=max((len(r['ancestry']) for r in restored), default=0),
        parentManifestCount=len(inventory.cache), metadataRestorationOnly=True, currentSourceRebindPending=True,
        testsExecuted=0, buildsIssued=0, newAcceptedLeaves=0, ptAlternativeCompleted=0,
        historicalPtImported=False, F03Accepted=False, formalAccepted=False, originalEvidenceOverwritten=False)
    with (out/'manifest.json').open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(result | dict(manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
