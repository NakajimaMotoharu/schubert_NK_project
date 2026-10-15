"""Independent static canaries; characterize record analyzer defect without mutating Main."""
from collections import Counter
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
JDK = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
TOOLS = Path('/home/mini/codex/project1/work/toolchain/static-gates-20261015')
OUT = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg3384-static-canaries-v2')


def main(after=False):
    out = OUT if not after else OUT.with_name('pg3384-static-canaries-v3-after')
    os.umask(0o077); out.mkdir(mode=0o700)
    files = ROOT / 'tools/quality/static/canaries'
    rules = ROOT / 'tools/quality/static'
    classpath = ':'.join(str(p) for p in sorted((TOOLS / 'pmd-bin-7.28.0/lib').glob('*.jar')))
    if after:
        overlay = TOOLS / 'record-fix-v1/classes'
        assert (overlay / 'net/sourceforge/pmd/lang/java/rule/multithreading/NonThreadSafeSingletonRule.class').is_file()
        classpath = str(overlay) + ':' + classpath
    records = {}
    for name in ['GatePositive', 'GateNegative', 'GateRecord', 'GateField']:
        source = files / (name + '.java'); classes = out / (name + '-classes'); classes.mkdir()
        compile_result = subprocess.run([str(JDK / 'javac'), '--release', '25', '-Xlint:all', '-Werror',
                                         '-d', str(classes), str(source)], capture_output=True, timeout=30)
        with (out / (name + '-compile.private.log')).open('xb') as f:
            f.write(compile_result.stdout + compile_result.stderr)
        assert compile_result.returncode == 0, 'each intentional static-negative still valid Java25'
        report = out / (name + '-pmd.xml')
        argv = [str(JDK / 'java'), '-cp', classpath, 'net.sourceforge.pmd.cli.PmdCli', 'check', '-d', str(source),
                '-R', str(rules / 'pmd.xml'), '--use-version', 'java-25', '--no-cache', '--aux-classpath', str(classes),
                '-f', 'xml', '-r', str(report)]
        result = subprocess.run(argv, capture_output=True, timeout=60)
        with (out / (name + '-pmd.private.log')).open('xb') as f:
            f.write(result.stdout + result.stderr)
        root = ET.parse(report).getroot(); violations = root.findall('.//{*}violation'); errors = root.findall('.//{*}error')
        records[name] = {'compileExit': compile_result.returncode, 'pmdExit': result.returncode,
                         'rules': dict(Counter(v.get('rule') for v in violations)), 'processingErrors': len(errors),
                         'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                         'pmdReportSha256': hashlib.sha256(report.read_bytes()).hexdigest()}
    for name in ['GatePositive', 'GateNegative']:
        report = out / (name + '-checkstyle.xml')
        argv = [str(JDK / 'java'), '-jar', str(TOOLS / 'checkstyle-14.3.0-all.jar'), '-c', str(rules / 'checkstyle.xml'),
                '-f', 'xml', '-o', str(report), str(files / (name + '.java'))]
        result = subprocess.run(argv, capture_output=True, timeout=30)
        with (out / (name + '-checkstyle.private.log')).open('xb') as f:
            f.write(result.stdout + result.stderr)
        records[name]['checkstyle'] = {'exit': result.returncode, 'rules': [v.get('source').rpartition('.')[2]
            for v in ET.parse(report).getroot().findall('.//error')], 'reportSha256': hashlib.sha256(report.read_bytes()).hexdigest()}
    assert records['GatePositive']['pmdExit'] == records['GatePositive']['processingErrors'] == 0
    assert records['GatePositive']['checkstyle']['exit'] == 0
    assert records['GateNegative']['pmdExit'] == 4 and records['GateNegative']['processingErrors'] == 0
    assert {'AvoidCatchingGenericException', 'EmptyCatchBlock'} <= records['GateNegative']['rules'].keys()
    assert {'MethodNameCheck', 'EmptyStatementCheck'} <= set(records['GateNegative']['checkstyle']['rules'])
    assert records['GateRecord']['pmdExit'] == (0 if after else 5)
    assert records['GateRecord']['processingErrors'] == (0 if after else 1)
    assert records['GateField']['processingErrors'] == 0 and records['GateField']['rules'].get('NonThreadSafeSingleton') == 1
    value = {'actualExit': 0, 'run': out.name, 'records': records,
             'priorAttempt': 'v1 canary TDD assertions failed; raw reports preserved, no pass credit',
             'recordErrorFixed': after, 'F03Accepted': False, 'newProductionPtCredit': 0}
    if after:
        before = json.loads((OUT / 'manifest.safe.json').read_bytes())
        assert before['actualExit'] == 0
        for name in records:
            assert records[name]['sourceSha256'] == before['records'][name]['sourceSha256']
            assert records[name]['rules'] == before['records'][name]['rules'], 'same actual violation sensitivity'
        value['overlayClassSha256'] = hashlib.sha256((overlay / 'net/sourceforge/pmd/lang/java/rule/multithreading/NonThreadSafeSingletonRule.class').read_bytes()).hexdigest()
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, indent=2)
    print(json.dumps(value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--after', action='store_true')
    main(parser.parse_args().after)
