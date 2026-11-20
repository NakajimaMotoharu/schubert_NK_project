"""Independently reconcile javap signatures, fixed findings and the admitted source set."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
JAVAP = Path('../toolchain/jdk-25.0.4/bin/javap').resolve()
LITERAL_OWNER_PREFIXES = {
    'java.io.PrintWriter': 6,
    'java.io.PrintStream': 6,
    'java.util.Formatter': 8,
    'java.util.Scanner': 6,
}
EXPECTED_FINDING_OWNERS = {**dict.fromkeys(LITERAL_OWNER_PREFIXES, 2), 'java.io.File': 1}


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def load(id):
    path, = OPS.glob(id + '-*/manifest.json')
    return path, json.loads(path.read_bytes())


def main():
    raw, red = load('PG41166')
    corrected, green = load('PG41168')
    scopes, prior = load('PG41100')
    table = corrected.with_name('audit.stdout.txt')
    assert pin(table) == green['steps']['audit']['stdout']
    findings = [line.split('\t') for line in table.read_text().splitlines() if line.startswith('FINDING\t')]
    assert all(len(line) == 4 and line[1] == 'CONTROLLER_BOUNDARY' for line in findings)
    assert Counter(line[3] for line in findings) == EXPECTED_FINDING_OWNERS
    assert len(red['cases']) == len(green['cases']) == 15
    assert red['missingBeforeOrAfter'] == 8 and green['missingBeforeOrAfter'] == 0
    assert green['fileSystemFixtureExecuted'] == green['productOperations'] == 0
    commands = []
    for binary, count in LITERAL_OWNER_PREFIXES.items():
        cmd = [str(JAVAP), binary]
        result = subprocess.run(cmd, capture_output=True, check=True, timeout=20)
        constructors = re.findall(r'(?m)^  public '+re.escape(binary)+r'\(([^)]*)\)', result.stdout.decode())
        first_types = ('java.io.File', 'java.nio.file.Path' if binary.endswith('Scanner') else 'java.lang.String')
        assert sum(s.split(', ', 1)[0] in first_types for s in constructors) == count
        commands.append(dict(command=cmd, constructorCount=len(constructors), filesystemOverloads=count,
                             exit=result.returncode, stdoutSha256=sha256(result.stdout).hexdigest()))
    assert green['productionCore'] == prior['productionCore']
    rule_names = re.compile(r'\b(?:PrintWriter|PrintStream|Formatter|Scanner)\b')
    for ref in prior['controllerSourcePins']:
        path = Path(ref['path'])
        assert pin(path) == ref and not rule_names.search(path.read_text())
    output = OPS/'PG41170-f02-controller-file-ctor-independent-v1'
    output.mkdir()
    target = output/'manifest.json'
    result = dict(actualExit=0, toolSource=green['toolSource'], core=green['productionCore'],
                  outcomes=[pin(raw), pin(corrected)], declaredOverloadCommands=commands,
                  originalSourceScope=pin(scopes), existingControllerSources=len(prior['controllerSourcePins']),
                  existingSyntacticMentions=0, syntheticCases=15, detected=9, allowed=6,
                  qualifiedScope='synthetic bytecode plus prior admitted controller source',
                  actualFileCalls=0, productTests=0, wholeF02=False, whole451=False, formalDelta=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with target.open('x') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(pin(target))


if __name__ == '__main__':
    main()
