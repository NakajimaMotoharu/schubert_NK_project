"""New-only22 after one import correction; early syntax check is not a PT or relaxed gate."""
import datetime
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import pg6376_web_fatal_callback_selected as previous
from pg5940_private_lock_compile import ROOT, W, TC, sha

OLD = 'a688d637cd63f24988d3a8906b50cfefc6aef24c'
inventory = previous.inventory


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [previous.TEST]:
        raise ValueError('one Test import only; every Main/oracle fixed')
    old = subprocess.check_output(['git', 'show', OLD+':'+previous.TEST], cwd=ROOT)
    new = subprocess.check_output(['git', 'show', source+':'+previous.TEST], cwd=ROOT)
    line = b'import static org.junit.jupiter.api.Assertions.assertSame;\n'
    if new.count(line) != 1 or new.replace(line, b'', 1) != old:
        raise ValueError('exact import line only, no expectation change')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('normal build/null/static/Current gates unchanged')


def failed_compile():
    path = W/'pg6376-web-fatal-callback-selected-v1/manifest.safe.json'; value = json.loads(path.read_bytes())
    if not (sha(path) == 'e838d132db45048ab56342f4910aaba15dec23ae188b67768453e573c25f6711'
            and value['source'] == OLD and value['actualExit'] == value['mavenActualExit'] == 1
            and value['sourceFixed'] and (value['tests'], value['suites']) == (6, 4)):
        raise ValueError('original compile failure preserved, no old result replay')


def precompile(source):
    # Read only a qualified nonsecret classpath property; never run a Production class/processor.
    xml = W/'pg6370-web-startup-retry-v1/source/src/schubert-nk-web/target/surefire-reports/TEST-dev.codex.schubert.nk.web.bootstrap.WebLogApplicationRuntimeTest.xml'
    if sha(xml) != 'a40deab46ca499fe81e9e7a25971c104eb62ade832a25014971c3f2e38a05f57':
        raise ValueError('immutable qualified classpath source')
    properties = {p.get('name'): p.get('value') for p in ET.parse(xml).getroot().findall('properties/property')}
    cp = properties.get('surefire.test.class.path')
    if not cp:
        raise ValueError('explicit original classpath, no fallback to unknown environment')
    os.umask(0o077); out = W/'pg6382-import-precompile-v1'; out.mkdir(mode=0o700); classes = out/'classes'; classes.mkdir()
    command = [str(TC/'jdk-25.0.4/bin/javac'), '--release', '25', '-proc:none', '-classpath', cp,
               '-d', str(classes), str(ROOT/previous.TEST)]
    before = sha(ROOT/previous.TEST); began = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (out/'compile.private.log').open('xb') as log:
        code = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=60).returncode
    value = dict(source=source, actualExit=code, startedUTC=began, completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        testSourceSha256=before, sourceUnchanged=before == sha(ROOT/previous.TEST), classpathReferenceXmlSha256=sha(xml),
        classpathSha256=hashlib.sha256(cp.encode()).hexdigest(), compileLogSha256=sha(out/'compile.private.log'),
        purpose='SYNTAX_IMPORT_ONLY_NOT_REGULAR_NULL_STATIC_BUILD_OR_PT', generatedClassesNotUsedByPt=True,
        productionClassesExecuted=0, testsExecuted=0, nativeQualified=False, formalAccepted=False)
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    if code != 0 or not value['sourceUnchanged']:
        raise ValueError('precompile failed; do not issue new PT')


def runner():
    raw = previous.runner()
    if raw.count('pg6376-web-fatal-callback-selected-v1') != 1:
        raise ValueError('one new-only corrected22 namespace')
    return raw.replace('pg6376-web-fatal-callback-selected-v1', 'pg6382-web-fatal-callback-retry-v1', 1)


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed import correction/operator first')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    guard_source(source); failed_compile(); precompile(source)
    scope = {**vars(previous.previous.previous.previous.prior), 'inventory': inventory}
    exec(compile(runner(), '<new22 with import precompile before normal PT>', 'exec'), scope)
    return scope['run_selected']()


if __name__ == '__main__':
    raise SystemExit(main())
