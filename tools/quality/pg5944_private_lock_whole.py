"""One necessary3973 for33 private-lock source changes; isolated approved host fixture profile."""
import json
import os
import subprocess
from pyflakes.api import check
import pg5926_api_storage_whole as previous
from pg5780_jms_primary_whole import RUNTIME
from pg5940_private_lock_compile import validate_source, plan, sha, BASE

ROOT, W = previous.ROOT, previous.W
SOURCE = '288062f3960a0a50ec82685da3b407f0c9e2934e'
LABEL = 'PG5944'
SLOT = 'pg5944-private-lock-six-v1'


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG5926', LABEL).replace('pg5926', 'pg5944').replace(previous.SOURCE, SOURCE)
    if check(raw, '<3973 private-lock standalone>') or any(s in raw for s in ('systemctl', 'qemu-system', 'virsh', 'sudo ', '/opt/schubert-nk/current', '--recover', '--resume')):
        raise ValueError('approved ordinary fixture namespace only, complete definitions')
    compile(raw, '<3973 private-lock standalone>', 'exec')
    return raw


def driver_source(fresh):
    raw = previous.driver_source(fresh).replace(previous.SLOT, SLOT).replace('PG5926', LABEL).replace('pg5926', 'pg5944')
    start = raw.index("'trigger': "); end = raw.index('}, sort_keys=True)', start)
    trigger = 'PG-D448/BUG1514:33 exclusive private final locks/93 identical critical sections, nonserialized Object-parent owners; no aliases/waitnotify/shared monitors. All851/1666 compile/null/SpotBugs/publicABI and unsuppressed PMD93 removal qualified; one necessary full3973/592 replaces duplicated almost-full selection then whole. Test/oracle/resources/POM unchanged. Prior-source PT/native not imported; held runtime/failed-cohort actions excluded.'
    raw = raw[:start]+"'trigger': "+repr(trigger)+raw[end:]
    compile(raw, '<new-only private-lock3973 driver>', 'exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator/source first')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical Main/Test frozen')
    validate_source(SOURCE, ROOT)
    debug = BASE/'PG5943-private-lock-debug20-v1/manifest.json'
    d = json.loads(debug.read_bytes())
    if d['source'] != SOURCE or d['actualExit'] != 0 or len(d['debugOnlyClasses']) != 20 or not all(r['exactPrivateDescriptorsAndBytecodeEqual'] for r in d['moduleProofs']):
        raise ValueError('all20 other physical differences proved nonexecutable first')
    p = BASE/'PG5942-private-lock-static-v1/manifest.json'; v = json.loads(p.read_bytes())
    private = W/'pg5942-private-lock-static-v1/manifest.safe.json'; body = json.loads(private.read_bytes())
    cp = W/'pg5940-private-lock-compile-v1/manifest.safe.json'
    if not (v['source'] == body['source'] == SOURCE and v['actualExit'] == body['actualExit'] == 0 and v['privateManifestSha256'] == sha(private) and v['compileManifestSha256'] == sha(cp)
            and v['pmdRawFindings'] == 1451 and v['rawDiagnosticsRemovedByPg'] == 93 and v['pmdProcessingErrors'] == v['checkstyleFindings'] == 0 and v['existingPublicAbiUnchanged']
            and body['inputSourceFiles'] == 851 and body['physicalMain'] == 1666 and set(plan()['requiredClassKeys']) <= set(body['changedPhysicalClasses'])):
        raise ValueError('actual same-source all851/1666/33source/34required targets/ABI/raw1451 first')


def main():
    prerequisites(); server_source(SOURCE, '0'*64)
    fresh = RUNTIME.preflight(); os.umask(0o077)
    with (W/'pg5944-preflight-v1.safe.json').open('x') as f:
        json.dump(fresh, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    scope = {**vars(RUNTIME.previous.driver), 'SOURCE': SOURCE, 'LABEL': LABEL, 'server_source': server_source}
    exec(compile(driver_source(fresh), '<one private-lock3973>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
