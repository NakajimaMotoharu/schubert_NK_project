"""One fresh fixed-source host qualification; safe tool evidence, not Production PT."""
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG1116-1119-receipt-native-qualification'


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('fresh fixed clean source required')
    if OUT.exists(): raise ValueError('prior qualification evidence preserved')
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s',
               'tools/quality/vm/050_s1', '-p', 'pg111[679]*test.py', '-v']
    start = datetime.datetime.now(datetime.timezone.utc)
    run = subprocess.run(command, cwd=ROOT, capture_output=True)
    log = run.stdout + run.stderr
    OUT.mkdir(parents=True, mode=0o755)
    (OUT / 'qualification.log').write_bytes(log)
    files = {}
    for name in ['pg609_parent_receipt.py','pg1116_current_receipt.py',
                 'pg1116_current_receipt_test.py','pg1117_current_done_probe.py',
                 'pg1117_current_done_probe_test.py','pg1118_receipt_qualification.py',
                 'pg1119_cold_native_contract.py','pg1119_cold_native_contract_test.py']:
        path = ROOT / 'tools/quality/vm/050_s1' / name
        files[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = dict(run='PG1116-1119-receipt-native-qualification', scope='HOST_TOOL_ONLY',
        formalAccepted=False, productionTestsAdded=0, wholeWbsAcceptedDelta=0,
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        productionSource='d5b00104280028d9ea81b44c1d1c805f3c2861ed',
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        startedUTC=start.isoformat(), completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        os=platform.platform(), python=platform.python_version(), command=command,
        actualExit=run.returncode, expected='13 host tool tests, all OK; no VM operations',
        passed=run.returncode==0 and b'Ran 13 tests' in log and log.rstrip().endswith(b'OK'),
        oracle='literal byte/journal/current captured binding; pre-existing independent PID1 oracle unchanged',
        logSha256=hashlib.sha256(log).hexdigest(), toolSourceSha256=files,
        trace=['NK-OPS-001','SS343','SS353','SSC253','SSC254','PT-DEP-1116001..004','PT-DEP-1117001..004','PT-DEP-1119001..005'],
        coverage='NOT_APPLICABLE_TO_THIS_HOST_TOOL_QUALIFICATION; Production counters unchanged',
        failuresPreserved='Pre-qualification TDD fixture corrections: arbitrary cursor is valid; start binding key is not systemctl mutation',
        pending=['actual current receipt','whole originals/DB/source closure','same-source native','owned stop'],
        bugs=['BUG-1028','BUG-1029'], crossChecks=['YKT-797','YKT-798'],
        secretsIncluded=False)
    with (OUT / 'manifest.json').open('x') as f:
        json.dump(manifest, f, indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':run.returncode,'passed':manifest['passed'],
        'manifest':str(OUT/'manifest.json'),
        'manifestSha256':hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest()}))
    return 0 if manifest['passed'] else 1


if __name__=='__main__': raise SystemExit(main())
