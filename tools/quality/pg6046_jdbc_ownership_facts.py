"""Parse-only six JDBC source owners; factual ownership proof,not PT or a disposition waiver."""
import base64
import json
import os
import re
import subprocess
from pathlib import Path
from pg5940_private_lock_compile import ROOT, W, TC, sha
from pg6040_remaining33_whole import SOURCE
from pg6002_direct_jdbc_finally_review import require_finally

OWNERS = {'BackupStepRepository': 2, 'BatchRunRepository': 8, 'CleanupStepRepository': 2,
          'CleanupTerminalRepository': 8, 'InspectionSummaryRepository': 2, 'RunReferenceRepository': 2}
FIELDS = ('path', 'method', 'variable', 'firstLine', 'lastLine', 'acquisition', 'primary', 'primaryDeclaration', 'body', 'catches', 'finallyBody', 'immediate', 'operation', 'nonExecutableDeclarations')


def decode_records(output):
    result = []
    for line in output.splitlines():
        fields = line.split('\t')
        if len(fields) != len(FIELDS):
            raise ValueError('one exact parse-only descriptor schema')
        row = dict(zip(FIELDS, (base64.b64decode(x, validate=True).decode('utf-8') for x in fields)))
        row['firstLine'] = int(row['firstLine']); row['lastLine'] = int(row['lastLine'])
        result.append(row)
    return result


def validate_scope(row):
    compact = lambda s: re.sub(r'\s+', '', s)
    if row['immediate'] != 'true' or row['variable'] not in ('row', 'rows', 'statement') or row['operation'] not in ('prepareStatement', 'executeQuery'):
        raise ValueError('immediate local acquisition/primary declaration/protected try required')
    resource, primary = row['variable'], row['primary']
    allowed_io = Path(row['path']).stem == 'CleanupTerminalRepository' and row['method'] == 'references'
    union = r'SQLException\|IOException\|RuntimeException\|Error' if allowed_io else r'SQLException\|RuntimeException\|Error'
    match = re.fullmatch(r'catch\('+union+r'(?P<failure>\w+)\)\{'+re.escape(primary)+r'=(?P=failure);throw(?P=failure);\}', compact(row['catches']))
    if match is None:
        raise ValueError('one primary capture/rethrow for all SQL/unchecked failures')
    if compact(row['primaryDeclaration']).removeprefix('@Nullable') != 'Throwable'+primary+'=null;':
        raise ValueError('only nonthrowing null primary declaration between acquisition and try')
    if '=' in row['nonExecutableDeclarations']:
        raise ValueError('no initialized local expression between acquisition and protection')
    body = 'finally'+row['finallyBody']
    if 'if('+resource+'!=null)' not in compact(body):
        raise ValueError('unacquired/null resource never closed')
    bindings = re.findall(r'catch\s*\(\s*SQLException\s*\|\s*RuntimeException\s*\|\s*Error\s+(\w+)\s*\)', body)
    if len(bindings) != 1:
        raise ValueError('one exact local secondary catch binding')
    symbolic = re.sub(r'\b'+re.escape(bindings[0])+r'\b', 'secondary', body)
    closes, guards = require_finally(symbolic, 'JdbcResourceFailures.replace')
    if closes != [resource] or len(guards) != 1 or guards[0][0] != primary:
        raise ValueError('close actual acquired resource once with its own actual primary')
    if re.search(r'\breturn\s+(?:'+re.escape(resource)+r'|statement|query|checked)\s*;', row['body']):
        raise ValueError('no resource escape as domain return')
    return dict(directClose=resource, primary=primary, helper='JdbcResourceFailures.replace',
                protectedImmediately=True, nullCloseForbidden=True, sourceMethod=row['method'],
                nonExecutableDeclarations=row['nonExecutableDeclarations'], declaredIOExceptionPreserved=allowed_io)


def collect(owners, source, slot):
    if not owners or any(not re.fullmatch(r'[A-Z][A-Za-z0-9]*', name) or type(count) is not int or count < 1 for name, count in owners.items()) or not re.fullmatch(r'pg\d+-[a-z0-9-]+-v[1-9][0-9]*', slot):
        raise ValueError('explicit finite owner counts and new-only safe namespace')
    if subprocess.check_output(['git', 'diff', source, '--', 'src'], cwd=ROOT):
        raise ValueError('Main/Test frozen during original6040')
    paths = [ROOT/('src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/'+name+'.java') for name in sorted(owners)]
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    for p in paths:
        if re.search(r'\bconnection\s*\.\s*(close|commit|rollback|setAutoCommit|setReadOnly|setTransactionIsolation)\s*\(', p.read_text()):
            raise ValueError('borrowed connection mutation/close outside this ownership proof')
    os.umask(0o077); out = W/slot; out.mkdir(mode=0o700); classes = out/'toolclasses'; classes.mkdir()
    helper = ROOT/'tools/quality/SourceJdbcOwnershipInventory.java'
    commands = [[str(TC/'jdk-25.0.4/bin/javac'), '-proc:none', '-implicit:none', '-Xlint:all', '-Werror', '-d', str(classes), str(helper)],
                [str(TC/'jdk-25.0.4/bin/java'), '-cp', str(classes), 'SourceJdbcOwnershipInventory', *map(str, paths)]]
    env = {k: v for k, v in os.environ.items() if k not in ('JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS', 'CLASSPATH')}
    outputs, exits = [], []
    for index, command in enumerate(commands):
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=120)
        exits.append(result.returncode); outputs.append(result.stdout)
        with (out/('phase-'+str(index)+'.private.log')).open('x') as f:
            f.write(result.stderr)
        with (out/('phase-'+str(index)+'.output.safe.tsv')).open('x') as f:
            f.write(result.stdout)
        if result.returncode:
            raise ValueError('parse-only helper/actual Main syntax failed;never invoke Production')
    records = decode_records(outputs[-1]); verified = []
    for row in records:
        path = Path(row['path']); name = path.stem
        if path not in paths or name not in owners:
            raise ValueError('only declared six source owners')
        value = validate_scope(row)
        relative = path.relative_to(ROOT).as_posix()
        verified.append({**row, 'path': relative, 'sourcePath': relative,
                         'sourceSha256': before[relative], 'ownership': value})
    counts = {name: sum(Path(r['path']).stem == name for r in records) for name in owners}
    if counts != owners or len(records) != sum(owners.values()) or before != {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}:
        raise ValueError('all24 individual immediate protected allocations,source fixed')
    value = dict(actualExit=0, source=source, phaseExits=exits, commands=commands, helperSha256=sha(helper),
        allSourceHashes=before, counts=counts, scopes=verified, parseOnly=True, typeResolutionClaimed=False,
        sourceCodeChanged=False, productionMethodsInvoked=0, testsExecuted=0, actualCoverage=None,
        dispositionCreated=0, originalWholePending=True, formalAccepted=False, ptAlternativeCompleted=0, vmActions=0)
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, owners=len(owners), protectedAllocations=len(records), testsExecuted=0, dispositionCreated=0, manifestSha256=sha(out/'manifest.safe.json'))))


def main():
    return collect(OWNERS, SOURCE, 'pg6046-jdbc-ownership24-facts-v3')


if __name__ == '__main__':
    main()
