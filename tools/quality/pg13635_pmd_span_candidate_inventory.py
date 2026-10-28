"""Read-only public Python endcolumn-consumer inventory; no held content or target execution."""
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13635-pmd-span-candidate-inventory-v1'
HELD = {'tools/quality/pg9892_snapshot_key_close_witness.py', 'tools/quality/architecture/SnapshotKeyCloseWitness.java'}
SELF = 'tools/quality/pg13635_pmd_span_candidate_inventory.py'

if __name__ == '__main__':
    invocation = capture(__file__)
    assert not OUT.exists()
    names = set()
    for args in [('ls-files', '-z', '--', 'tools/quality'), ('ls-files', '--others', '--exclude-standard', '-z', '--', 'tools/quality')]:
        names.update(p.decode() for p in subprocess.check_output(['git', *args], cwd=data.ROOT).split(b'\0') if p)
    # Exclusion is done by name before metadata/content access.
    names -= HELD | {SELF}
    selected = sorted(p for p in names if p.startswith('tools/quality/') and p.endswith('.py') and '/private' not in p)
    assert not set(selected) & HELD and SELF not in selected
    rows = []
    scanned = 0
    for name in selected:
        path = data.ROOT/name
        assert not path.is_symlink() and path.is_file()
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        scanned += 1
        matches = []
        for number, line in enumerate(text.splitlines(), 1):
            if 'endcolumn' in line and re.search(r'\bint\s*\(', line):
                matches.append(dict(line=number, minusOneSyntaxPresent=bool(re.search(r'endcolumn[^\n]*?\)\s*-\s*1\b', line))))
        if matches:
            rows.append(dict(path=name, sourceSha256=data.sha(raw), candidateLines=matches,
                disposition='ENDCOLUMN_INPUT_CONTRACT_AND_INTERVAL_CONSUMER_REVIEW_REQUIRED'))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'candidates.json', dict(rows=rows))
    data.write(OUT/'manifest.json', dict(actualExit=0, invocation=invocation,
        candidateInventorySha256=data.sha((OUT/'candidates.json').read_bytes()), scannedPublicPythonFiles=scanned,
        candidateFiles=len(rows), candidateLines=sum(len(r['candidateLines']) for r in rows),
        selector='TRACKED_OR_CURRENT_UNTRACKED_PUBLIC_PYTHON; END_COLUMN_AND_INT_ON_SAME_LINE; NOT_ALL_COLUMN_SCHEMAS',
        syntaxIsNotCorrectnessProof=True, candidatesNotAutomaticallyDefects=True,
        horizontalExpansionComplete=False, bug='BUG-2071', expansion='YKT-1819',
        heldNamesExcludedBeforeAccess=sorted(HELD), productTestsExecuted=0, externalActions=0,
        newAccepted=0, formalUpdated=False))
    print(dict(manifestSha256=data.sha((OUT/'manifest.json').read_bytes()), candidates=len(rows), horizontalExpansionComplete=False))
