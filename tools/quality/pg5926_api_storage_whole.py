"""One coherent3973 campaign after storage6/API3 PG; approved isolated host fixtures only."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5886_terminal_serial_whole as previous
from pg5906_storage30_static import MODIFIED as STORAGE
from pg5914_api_expression_static import MODIFIED as API

ROOT, W = previous.ROOT, previous.W
SOURCE = '682a4b99eb0b95bcd4f1cd276fea75b5f2e62e3b'
LABEL = 'PG5926'
SLOT = 'pg5926-api-storage-six-v1'
MODIFIED = STORAGE | API


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG5886', LABEL).replace('pg5886', 'pg5926').replace(previous.SOURCE, SOURCE)
    if check(raw, '<coherent3973 storage/API runner>') or any(s in raw for s in ('systemctl', 'qemu-system', 'virsh', 'sudo ', '/opt/schubert-nk/current', '--recover', '--resume')):
        raise ValueError('complete ordinary fixture namespace; held runtime actions excluded')
    compile(raw, '<coherent3973 storage/API>', 'exec')
    return raw


def driver_source(fresh):
    raw = previous.driver_source(fresh).replace(previous.SLOT, SLOT).replace('PG5886', LABEL).replace('pg5886', 'pg5926')
    start = raw.index("'trigger': "); end = raw.index('}, sort_keys=True)', start)
    trigger = 'PG-D446/447 BUG1507/1509: six storage same-value constants/private reentrant lock sections and three API SQL-index/read/store expressions,42 raw warnings removed. Test/oracle/resources/POM unchanged from qualified3973. Storage199 on identical storage Main and current API35/all851/1666/publicABI/raw static qualified; fresh whole3973/592 verifies their shared same-source integration once. Prior-source full/native not imported; no held operational action.'
    raw = raw[:start] + "'trigger': " + repr(trigger) + raw[end:]
    compile(raw, '<new-only storage/API driver>', 'exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator first')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT):
        raise ValueError('fixed canonical Main/Test/config')
    changed = subprocess.check_output(['git', 'diff', '--name-only', previous.SOURCE, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if len(MODIFIED) != 9 or set(changed) != MODIFIED:
        raise ValueError('only declared nine Main sources; Tests/oracle/resources unchanged')
    if subprocess.check_output(['git', 'diff', previous.SOURCE, SOURCE, '--', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT):
        raise ValueError('same original quality/characterization gates')
    p = W / 'pg5912-api-expression-selected35-v1/manifest.safe.json'
    v = json.loads(p.read_bytes())
    base = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
    sp = base / 'PG5914-api-expression-static-v1/manifest.json'
    s = json.loads(sp.read_bytes()); private = W / 'pg5914-api-expression-static-v1/manifest.safe.json'
    if hashlib.sha256(sp.read_bytes()).hexdigest() != '318d3783a5bfa4fe9a3920b252d3449eca01b9131c925758eadf13f8289548b4' or not (v['source'] == s['source'] == SOURCE and v['actualExit'] == s['actualExit'] == 0 and v['selectedQualified'] and (v['tests'], v['suites']) == (35, 10) and not v['failedOrSkipped'] and s['selectedManifestSha256'] == hashlib.sha256(p.read_bytes()).hexdigest() and s['privateManifestSha256'] == hashlib.sha256(private.read_bytes()).hexdigest() and s['physicalMain'] == 1666 and s['inputSourceFiles'] == 851 and s['pmdRawFindings'] == 1544):
        raise ValueError('actual current35 and all851/1666 independent static first')
    old = json.loads((W / 'pg5904-storage30-selected199-v1/manifest.safe.json').read_bytes())
    oldp = base / 'PG5908-storage199-v1/manifest.json'
    if hashlib.sha256(oldp.read_bytes()).hexdigest() != '91f2dce1489f9aa1ec4e8d35d29f8106ae1200d306e8f1483e158962f3d62506' or old['actualExit'] != 0 or not old['selectedQualified'] or (old['tests'], old['suites']) != (199, 33):
        raise ValueError('original storage selected proof; not imported as current whole')
    current = json.loads(private.read_bytes())
    for key, digest in old['allPhysicalMainSha256'].items():
        if key.startswith('storage:') and current['auxClassHashes'][key] != digest:
            raise ValueError('all storage classes byte-identical after API-only PG')


def main():
    prerequisites(); server_source(SOURCE, '0' * 64)
    runtime = previous.previous.previous.previous.previous.RUNTIME
    fresh = runtime.preflight(); os.umask(0o077)
    with (W / 'pg5926-preflight-v1.safe.json').open('x') as f:
        json.dump(fresh, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    scope = {**vars(runtime.previous.driver), 'SOURCE': SOURCE, 'LABEL': LABEL, 'server_source': server_source}
    exec(compile(driver_source(fresh), '<coherent storage/API3973>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
