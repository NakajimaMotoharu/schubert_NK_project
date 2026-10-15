"""Independently reconstruct 64 golden vector rows from canonical field tables.

Only UI Markdown/committed test TSV are read; no Production code or Java call.
Generic codec boundary vectors are not business-valid semantic request fixtures.
"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

from pg3284_protocol_canonical_fixtures import ROOT, SOURCE, FIXTURE, field_areas, layouts, require, tsv, unique_file


def area_bytes(fields, maximum=False, error=False):
    result = bytearray()
    for name, start, length, wire, presence, rule in fields:
        require(start == len(result) + 1 and length > 0, 'independent contiguous positive area required')
        require(wire in ('X', 'N', 'B') and presence in ('M', 'C', 'O', 'F'), 'explicit canonical type/presence required')
        if presence == 'F':
            fixed = re.fullmatch(r'固定`([A-Z]+)`', rule)
            if fixed:
                require(wire == 'X', 'fixed literal X required'); value = fixed[1].encode('ascii')
            else:
                require(rule in ('全space', 'Space') and wire == 'X', 'only explicit reserved space allowed'); value = b''
            require(len(value) <= length, 'fixed literal fits canonical width')
            value = value.ljust(length, b' ')
        elif error:
            value = (b'0' if wire == 'N' else b' ') * length
        elif not maximum and presence != 'M':
            value = b' ' * length
        elif wire == 'X':
            value = b'Z' * length if maximum else b'A'.ljust(length, b' ')
        elif wire == 'N':
            value = (b'9' if maximum else b'0') * length
        else:
            require(length == 1, 'boolean is exactly one byte'); value = b'1' if maximum else b'0'
        require(len(value) == length, 'exact field byte width'); result.extend(value)
    return bytes(result)


def vector_row(id, catalog, areas):
    data = areas.get((id, 'DATA'), []); record = areas.get((id, 'RECORD'), [])
    sha = lambda value: hashlib.sha256(value).hexdigest()
    return [id, sha(area_bytes(data)), sha(area_bytes(data, maximum=True)),
            sha(area_bytes(record)), sha(area_bytes(record, maximum=True)),
            sha(area_bytes(data, error=True)) if catalog[id][0] == 'S' else '-']


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean independent golden tool required')
    ui = ROOT / 'documents/200_UI/230_インターフェース'
    paths = [unique_file(ui, str(n) + '_*.md') for n in (233, 234, 235, 236)]
    for path in paths:
        require(path.read_bytes() == subprocess.check_output(['git', 'show', 'origin/main:' + str(path.relative_to(ROOT))], cwd=ROOT), 'current canonical origin/main byte required')
    catalog = layouts(paths[0].read_text()); areas = field_areas([p.read_text() for p in paths[1:]])
    golden_path = ROOT / FIXTURE / 'payload-golden-ui234-236.tsv'; golden = tsv(golden_path)
    require(len(golden) == len(catalog) == 64 and len({row[0] for row in golden}) == 64, 'exact64 unique golden rows')
    independent = [vector_row(row[0], catalog, areas) for row in golden]
    require(independent == golden and sum(row[-1] != '-' for row in independent) == 31, 'all287 independently computed digests and33 not-applicable cells must match')
    require(('fields-ui234-236.tsv-sha256=' + hashlib.sha256((ROOT / FIXTURE / 'fields-ui234-236.tsv').read_bytes()).hexdigest()) in golden_path.read_text(), 'golden-to-field independent fixture provenance required')
    value = {'actualExit': 0, 'productionSource': SOURCE, 'run': 'PG3292-canonical-golden-v1',
             'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'canonicalCommit': subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
             'canonicalHashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
             'goldenFixtureSha256': hashlib.sha256(golden_path.read_bytes()).hexdigest(),
             'layouts': 64, 'responseErrors': 31, 'digestChecks': 287, 'notApplicableErrorCells': 33,
             'expectedGeneratedFromProduction': False, 'businessSemanticValidityClaimed': False,
             'newPtCredit': 0, 'coverageCredit': 0, 'vmActions': 0, 'formalUpdated': False,
             'toolSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    out = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG3292-canonical-golden'
    out.mkdir(parents=True, exist_ok=False)
    with (out / 'manifest.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps(value)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
