"""Trace the approved 64 UI layouts to the current DDL and Java inventories."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess


DATA = Path('evidence/01_PT/004_NK-DAT-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
MIGRATIONS = Path('src/schubert-nk-api/src/main/resources/db/migration')
DB_TEST = Path('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database')
PROTOCOL = Path('src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout')
RD = Path('documents/100_RD/140_データ要件/141_データ・移行対象要件.md')


def git(*args):
    return subprocess.check_output(['git', *args])


def sha(content):
    return hashlib.sha256(content).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def read(source, path):
    return git('show', f'{source}:{path}').decode('utf-8')


def ui_dimensions(document):
    table = {}
    direction = {}
    for line_no, line in enumerate(document.splitlines(), 1):
        if not line.startswith('|'):
            continue
        cells = [field.strip() for field in line.strip('|').split('|')]
        match = re.fullmatch(r'([QSE]) `([A-Z0-9]{8})`', cells[1]) if len(cells) == 9 else None
        if match:
            kind, layout = match.groups()
            assert layout not in table
            table[layout] = tuple(int(field.replace(',', '')) for field in cells[3:7])
            direction[layout] = (kind, line_no)
    assert Counter(value[0] for value in direction.values()) == {'Q': 31, 'S': 31, 'E': 2}
    return table, direction


def ss_rows(text):
    result = {}
    for line_no, line in enumerate(text.splitlines(), 1):
        if not re.match(r'^\| `[A-Z0-9]{8}`\s+[0-9]', line):
            continue
        cells = [field.strip() for field in line.strip('|').split('|')]
        assert len(cells) == 5
        layout, dimension_text = cells[0][1:].split('`', 1)
        assert layout not in result
        dimensions = tuple(int(field.replace(',', '')) for field in dimension_text.strip().split('/'))
        result[layout] = (dimensions, cells[1], cells[2], cells[3], line_no)
    return result


def db_inventory(core, old, recent):
    files = sorted(git('ls-tree', '-r', '--name-only', core, '--', str(MIGRATIONS)).decode().splitlines())
    versions = [re.fullmatch(r'V([0-9]{3})__[a-z0-9_]+\.sql', Path(path).name).group(1) for path in files]
    assert versions == [f'{version:03}' for version in range(1, 31)]
    testing = read(core, DB_TEST/'MigrationInventory.java')
    start = testing.index('List.of(')
    assert re.findall(r'"([0-9]{3})"', testing[start:testing.index(');', start)]) == versions
    archived = old['oldApplied29SqlHashes']
    assert set(archived) == set(files[:29])
    qualified = recent['currentDdlArtifacts']
    assert files[-1] in qualified and len(qualified) == 2
    program = {}
    declared = {}
    for name in files:
        source = read(core, name)
        digest = sha(source.encode('utf-8'))
        assert b'\r' not in source.encode('utf-8') and '\0' not in source
        assert digest == (archived[name] if name in archived else qualified[name]['sha256'])
        program[name] = digest
        for table in re.findall(r'^CREATE TABLE ([a-z_]+\.[a-z_]+)\b', source, re.M):
            assert table not in declared
            declared[table] = name
    for path, ref in qualified.items():
        assert sha(git('show', f'{core}:{path}')) == ref['sha256']
    test_text = read(core, DB_TEST/'DatabaseMigrationTest.java')
    start = test_text.index('private static Set<String> expectedTables()')
    table_oracle = set(re.findall(r'"([a-z_]+\.[a-z_]+)"', test_text[start:test_text.index(');', start)]))
    assert set(declared) == table_oracle and len(declared) == 24
    return program, declared


def main():
    start_file = next(PLAN.glob('1042_P004*'))
    start = json.loads(start_file.read_bytes())['values']
    refs = start['oracleReferences']
    assert all(pin(Path(ref['path'])) == ref for ref in refs)
    old, recent, protocol = (json.loads(Path(ref['path']).read_bytes()) for ref in refs[1:4])
    core, design = start['productionCoreMain'], start['canonicalDesignSource']
    ui_path, ss_path, ddl_path = (Path(ref['path']) for ref in refs[-3:])
    requirements = re.findall(r'^\| (DAT-[0-9]{3}) \|', read(design, RD), re.M)
    assert requirements == [f'DAT-{i:03}' for i in range(1, 12)]
    ddl_spec = read(design, ddl_path)
    assert 'DAT-001～DAT-011' in ddl_spec and '## 11. Migration DDLの順序・検査' in ddl_spec

    ui, direction = ui_dimensions(read(design, ui_path))
    ss = ss_rows(read(design, ss_path))
    registry = read(core, PROTOCOL/'LayoutRegistry.java')
    rows = re.findall(r'd\(\s*"([A-Z0-9]{8})",\s*MessageKind\.(\w+),\s*InteractionKind\.(\w+),\s*'
                      r'([0-9_]+),\s*([0-9_]+),\s*([0-9_]+),\s*([0-9_]+)\)', registry)
    actual = {layout: (kind, group, tuple(int(value.replace('_', '')) for value in dims))
              for layout, kind, group, *dims in rows}
    types_source = read(core, PROTOCOL/'PayloadTypeCatalog.java')
    bindings = re.findall(r'Map\.entry\(\s*"([A-Z0-9]{8})",\s*mapping\(\s*(\w+)\.class', types_source)
    java_types = dict(bindings)
    assert len(rows) == len(bindings) == len(java_types) == len(ui) == 64
    assert set(ui) == set(ss) == set(actual) == set(java_types)
    assert protocol['productionCore'] == core and protocol['actualExit'] == 0
    migration_hashes, tables = db_inventory(core, old, recent)

    layouts = []
    for name, shape in ui.items():
        data, record, maximum, total = shape
        kind, ui_line = direction[name]
        ss_dims, java_text, handler, db_text, ss_line = ss[name]
        java_kind, interaction, java_dims = actual[name]
        assert java_dims == ss_dims == shape and total == 256 + data + record * maximum
        assert java_kind == {'Q': 'REQUEST', 'S': 'RESPONSE', 'E': 'EVENT'}[kind]
        assert java_types[name] in re.findall(r'`(\w+)`', java_text)
        assert db_text
        # Preserve the design's descriptions, including derived values and aliases.
        named_tables = [table for table in tables if re.search(
            r'(?<!\w)'+re.escape(table.split('.')[-1])+r'(?!\w)', db_text)]
        layouts.append(dict(layout=name, uiLine=ui_line, designLine=ss_line, dataBytes=data,
                            recordBytes=record, maximumRecords=maximum, maximumWireBytes=total,
                            interaction=interaction, javaType=java_types[name], designHandler=handler,
                            designDbDescription=db_text, explicitlyNamedTables=sorted(named_tables)))
    assert {row['layout'] for row in layouts if row['designDbDescription'] == '—'} == {
        'GAMREQ01', 'ANMREQ01', 'MCTREQ01'}
    out = DATA / start['run']
    out.mkdir()
    catalog, inventory = out/'layout-db-catalog.json', out/'ddl-inventory.json'
    write(catalog, layouts)
    write(inventory, dict(versions=sorted(migration_hashes), migrationSha256=migration_hashes,
                          tableDeclarations=tables))
    proof = out/'manifest.json'
    write(proof, dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                      source=start['source'], productionCore=core, designSource=design,
                      groupStart=pin(start_file), designRequirements=requirements,
                      wireLayouts=64, originalAppliedSqlBytesMatching=29, currentMigrations=30,
                      currentSqlDeclarations=24, currentSqlLayoutProof=pin(catalog),
                      declaredObjectsOnly=pin(inventory), sourceTraceProofs=refs[1:], actualDbTests=0,
                      actualRuntimeLayoutDbTrace=0, codeFourCoverage=None, whole451=False,
                      formalDelta=0))
    print(pin(proof))


if __name__ == '__main__':
    main()
