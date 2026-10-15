"""Independent canonical Markdown -> Test fixture audit. No Production method/code oracle.

P00101/02/03, MQ014-018, UI233-236/SS323. Read-only to canonical designs and
fixtures; generated safe audit evidence is not a Production test or acceptance.
"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from pg1446_current_cold_stage import W
from pg3274_header_group_full_six import ROOT, SOURCE

MACROS = ('PAGED48', 'MEDIA1024', 'USRMUT24')
ID = r'(?<![A-Z0-9])([A-Z0-9]{8})(?![A-Z0-9])'
FIELD = re.compile(r'^\|\s*([^|]+?)\s*\|\s*([0-9,]+)\s*\|\s*([0-9,]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$')
FIXTURE = Path('src/schubert-nk-protocol/src/test/resources/protocol')


def require(value, message):
    if not value:
        raise ValueError(message)


def unique_file(directory, pattern):
    paths = list(directory.glob(pattern)); require(len(paths) == 1, 'one exact canonical document required')
    return paths[0]


def numeric(value):
    require(re.fullmatch('[0-9]+(?:,[0-9]{3})*', value) is not None, 'canonical nonnegative decimal required')
    return int(value.replace(',', ''))


def layouts(text):
    result = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.split('|')[1:-1]]
        match = re.fullmatch(r'([QSE]) `([A-Z0-9]{8})`', cells[1]) if len(cells) >= 7 else None
        if match:
            require(match[2] not in result, 'duplicate canonical layout forbidden')
            values = (match[1], cells[2], *(numeric(v) for v in cells[3:7]))
            require(values[1] in ('S', 'A', 'I') and 256 + values[2] + values[3] * values[4] == values[5], 'independent UI total length formula required')
            result[match[2]] = values
    return result


def field_areas(texts):
    sections = []
    for text in texts:
        parts = re.split(r'(?m)^(#{2,3} .*)$', text)
        for index in range(1, len(parts), 2):
            heading, body = parts[index:index + 2]
            rows = [m.groups() for line in body.splitlines() if (m := FIELD.fullmatch(line))]
            sections.append((heading, body, rows))
    templates = {}; aliases = {}
    for heading, body, rows in sections:
        for name in MACROS:
            if '`' + name + '`' in heading:
                require(name not in templates and rows, 'unique nonempty canonical template required')
                templates[name] = rows
                # ASCII boundaries, not Unicode word boundaries beside Japanese prose.
                aliases[name] = re.findall(ID, body.split('|', 1)[0])
    require(set(templates) == set(MACROS), 'all three explicit shared template definitions required')

    def typed(rows, offset=0):
        result = []
        for name, start, length, wire, presence, rule in rows:
            require(wire in ('X', 'N', 'B') and presence in ('M', 'C', 'O', 'F'), 'explicit canonical field type/presence required')
            result.append((name, numeric(start) + offset, numeric(length), wire, presence, rule))
        return result

    result = {}
    for name, ids in aliases.items():
        for id in ids:
            require((id, 'DATA') not in result, 'duplicate shared-template use declaration forbidden')
            result[(id, 'DATA')] = typed(templates[name])
    explicit = set()
    for heading, body, rows in sections:
        ids = re.findall(r'`([A-Z0-9]{8})`', heading); area = re.search(r'\b(data|record)\b', heading)
        if len(ids) != 1 or not area:
            continue
        key = (ids[0], area[1].upper()); require(key not in explicit, 'duplicate explicit layout area forbidden'); explicit.add(key)
        if not rows:
            references = {name for name in templates if name in body}
            if len(references) == 1:
                rows = templates[next(iter(references))]
        expanded = []
        for row in rows:
            if row[0] in templates:
                require(row[3] == '-' and row[4] == 'M'
                        and numeric(row[2]) == sum(numeric(r[2]) for r in templates[row[0]]),
                        'composite macro must have its explicit exact width/type/presence')
                expanded.extend(typed(templates[row[0]], numeric(row[1]) - 1))
            else:
                expanded.extend(typed([row]))
        result[key] = expanded
    return result


def named_types(text):
    result = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.split('|')[1:-1]]
        match = re.match(r'^`([A-Z0-9]{8})` [0-9,]+/', cells[0]) if len(cells) >= 2 else None
        if match:
            names = re.findall(r'`([A-Za-z][A-Za-z0-9]*)`', cells[1])
            require(len(names) in (1, 2) and match[1] not in result, 'unique explicit Java data/record mapping required')
            result[match[1]] = (names[0], names[1] if len(names) == 2 else '-')
    return result


def tsv(path):
    return [line.split('\t') for line in path.read_text().splitlines() if line and not line.startswith('#')]


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean canonical audit tool required')
    ui = ROOT / 'documents/200_UI/230_インターフェース'; ss = ROOT / 'documents/300_SS/320_メッセージング'
    paths = [*(unique_file(ui, str(n) + '_*.md') for n in [233, 234, 235, 236]), unique_file(ss, '323_*.md')]
    canonical = {}
    for path in paths:
        relative = str(path.relative_to(ROOT)); data = path.read_bytes()
        require(data == subprocess.check_output(['git', 'show', 'origin/main:' + relative], cwd=ROOT), 'working design must equal current origin/main canonical')
        canonical[relative] = hashlib.sha256(data).hexdigest()
    catalog = layouts(paths[0].read_text()); areas = field_areas([p.read_text() for p in paths[1:4]])
    names = named_types(paths[4].read_text())
    fixtures = [ROOT / FIXTURE / n for n in ['layouts-ui233.tsv', 'fields-ui234-236.tsv', 'named-types-ss323.tsv']]
    expected_layouts = {}
    for id, kind, interaction, *sizes in tsv(fixtures[0]):
        require(id not in expected_layouts, 'duplicate layout fixture forbidden')
        expected_layouts[id] = (kind, interaction, *map(int, sizes))
    expected_areas = {}
    for id, area, name, start, length, wire, presence, rule in tsv(fixtures[1]):
        expected_areas.setdefault((id, area), []).append((name, int(start), int(length), wire, presence, rule))
    expected_names = {}
    for id, data, record in tsv(fixtures[2]):
        require(id not in expected_names, 'duplicate type fixture forbidden')
        expected_names[id] = (data, record)
    require(catalog == expected_layouts and len(catalog) == 64, 'all64 independent canonical layout tuples must match')
    require({k: v for k, v in areas.items() if v} == expected_areas and sum(map(len, expected_areas.values())) == 389, 'all389 field literals must match canonical, not Production')
    for id, (_, _, data_len, record_len, _, _) in catalog.items():
        for area, size in [('DATA', data_len), ('RECORD', record_len)]:
            rows = areas.get((id, area), []); position = 1
            for row in rows:
                require(row[1] == position and row[2] > 0, 'independent canonical gaps/overlap forbidden'); position += row[2]
            require(position - 1 == size, 'canonical area length must match independent UI233 tuple')
    require(names == expected_names and set(names) == set(catalog), 'all64 independent SS323 Java mappings required')
    distinct = {name for pair in names.values() for name in pair if name != '-'}; require(len(distinct) == 69, 'all69 named type names required')
    value = {'actualExit': 0, 'productionSource': SOURCE, 'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'canonicalSource': 'origin/main', 'canonicalCommit': subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
             'layoutTuples': 64, 'fieldRows': 389, 'nonemptyAreas': len(expected_areas), 'namedMappings': 64, 'distinctNamedTypes': 69,
             'canonicalHashes': canonical, 'fixtureHashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fixtures},
             'toolSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'sourceQualified': True, 'expectedGeneratedFromProduction': False, 'productionPtCredit': 0, 'coverageCredit': 0,
             'mainOrTestChanges': 0, 'vmActions': 0, 'acceptedLeafDelta': 0, 'formalAccepted': False,
             'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    # v1 is an uncommitted-tool diagnostic preserved privately, not accepted proof.
    out = W / 'pg3284-protocol-canonical-fixtures-v2'; out.mkdir(mode=0o700)
    with (out / 'manifest.safe.json').open('x') as stream:
        json.dump(value, stream, sort_keys=True)
    print(json.dumps(value)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
