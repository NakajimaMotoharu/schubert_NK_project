"""Same genuine new Root/ordinary four owners around finite real Chromium business cases."""
import datetime
import hashlib
import json
import os
import subprocess
import sys
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
import pg1191_chr_socks_owner as socks_owner
from pg2900_network_completed_owner_a01 import GUARD
from pg3138_browser_cohort_ready import require_ready, classpath, JAVA, SLOT as READY
from pg3120_prepared_browser_observer import SOURCE

SLOT = 'pg3184-browser-business-actual-v3'

TLS_WITNESS = r'''
def independent_tls_peer():
 import ssl,socket,stat
 def listener():
  inodes=set()
  for fd in(pathlib.Path('/proc')/EXPECTED['caddy.service'][0]/'fd').iterdir():
   try:value=str(fd.readlink())
   except FileNotFoundError:continue
   if value.startswith('socket:[')and value.endswith(']'):inodes.add(value[8:-1])
  found={parts[9]for line in pathlib.Path('/proc/net/tcp').read_text().splitlines()[1:]if len(parts:=line.split())>9 and parts[1]=='0F02000A:D778'and parts[3]=='0A'and parts[9]in inodes}
  require(bool(found));return found
 owned=listener()
 ca=pathlib.Path('/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt')
 s=ca.lstat();require(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and not os.listxattr(ca))
 before=(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 certificate=ca.read_bytes();context=ssl.create_default_context(cafile=str(ca))
 require(context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED)
 with socket.create_connection(('10.0.2.15',55160),timeout=3)as connected:
  with context.wrap_socket(connected,server_hostname='10.0.2.15')as secured:
   require(secured.version()in {'TLSv1.2','TLSv1.3'})
   peer=secured.getpeercert(binary_form=True);require(bool(peer))
 s=ca.lstat();require(before==(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)and certificate==ca.read_bytes()and owned==listener())
 return {'normalChainAndIpSanValidated':True,'sameOwnedCaddyListener':True,'caSha256':hashlib.sha256(certificate).hexdigest(),'leafSha256':hashlib.sha256(peer).hexdigest(),'httpRequestsSent':0}
tls=independent_tls_peer()
'''


def guard(seal, terminal, binding):
    if seal.get('actualExit') != 0 or terminal.get('actualExit') != 0 or terminal.get('genuineParentDone') is not True or any(item.get('productionSource') != SOURCE for item in [seal, terminal]):
        raise ValueError('current genuine terminal and all24 fullseal required')
    raw = GUARD.replace('74729e17-91c0-43e7-b01f-74f9e6461d6a', binding['activation'])
    raw = raw.replace("'caddy.service']", "'caddy.service','artemis.service']")
    raw = raw.replace('import hashlib,json,pathlib,subprocess', 'import hashlib,json,pathlib,subprocess,os')
    marker = 'print(json.dumps(units))'
    if raw.count(marker) != 1:
        raise ValueError('one fixed owned Browser output boundary required')
    raw = raw.replace(marker, TLS_WITNESS + "\nprint(json.dumps({'units':units,'tls':tls}))")
    return 'EXPECTED=' + repr(seal['observedOwned']) + '\nDONE_SHA=' + repr(terminal['proofHashes']['done.private']) + '\n' + raw


def owned_socks():
    value = json.loads((W / 'pg3126-browser-business-socks-v1/running.safe.json').read_bytes())
    socks_owner.EXPECTED = {'pid': value['pid'], 'ticks': value['ticks'], 'argvSha256': value['argvSha256'], 'executable': '/usr/bin/ssh', 'ppid': value['parentPid'], 'uids': (1000, 1000, 1000, 1000), 'gids': (1000, 1000, 1000, 1000), 'listenerAddresses': ('0100007F:D781',)}
    return socks_owner.require_owner()


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed Browser operator required')
    require_ready()
    prefix = json.loads((W / 'pg3162-failed-menu-partial-login-post-v1/manifest.safe.json').read_bytes())
    if not (prefix['actualExit'] == 0 and prefix['sourceQualified'] and prefix['result']['all24PartialQualified'] and prefix['sameFourOwners'] and prefix['sameSocks']):
        raise ValueError('failed first Menu cohort side effects must be independently qualified before a new cohort')
    prefix2 = json.loads((W / 'pg3172-failed-admin-auth-read-post-v1/manifest.safe.json').read_bytes())
    if not (prefix2['actualExit'] == 0 and prefix2['sourceQualified'] and prefix2['result']['all24PartialQualified'] and prefix2['sameFourOwners'] and prefix2['sameSocks']):
        raise ValueError('failed ADMIN cohort side effects must be independently qualified before a new cohort')
    seal = json.loads((W / 'pg3134-browser-resume-full-seal-v1/manifest.safe.json').read_bytes())
    terminal = json.loads((W / 'pg3130-browser-resume-terminal-v1/manifest.safe.json').read_bytes())
    live = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())
    raw = guard(seal, terminal, live['binding'])
    out = W / SLOT; out.mkdir(mode=0o700)
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out / 'guard.private.py').write_text(raw)
    before_socks = owned_socks()
    with management_gate(P / 'current-management-critical.lock'):
        before = subprocess.check_output(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), timeout=25)
        env = {**os.environ, 'PLAYWRIGHT_BROWSERS_PATH': '/home/mini/codex/project1/work/characterization-tools/playwright-browsers', 'PLAYWRIGHT_HOST_PLATFORM_OVERRIDE': 'ubuntu24.04-x64', 'LD_LIBRARY_PATH': '/home/mini/codex/project1/work/characterization-tools/root/usr/lib/x86_64-linux-gnu'}
        command = [str(JAVA / 'java'), '-cp', classpath(W / READY / 'classes'), 'dev.codex.schubert.characterization.NativeNkBrowserBusinessCohort', 'run', str(out / 'cases')]
        with (out / 'browser.private.log').open('xb') as log:
            result = subprocess.run(command, stdout=log, stderr=log, env=env, timeout=600)
        after = subprocess.check_output(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), timeout=25)
    if json.loads(before) != json.loads(after) or before_socks != owned_socks():
        raise ValueError('same ordinary owner/SOCKS generation must survive Browser')
    codes = [result.returncode]
    if not result.returncode:
        with (out / 'all24.private.log').open('xb') as log:
            actual = subprocess.run([sys.executable, '-B', 'tools/quality/pg3136_browser_rows_oracle.py', str(out / 'cases/before-rows.private.json'), str(out / 'cases/after-rows.private.json'), str(out / 'cases/context.private.json')], stdout=log, stderr=log, timeout=30)
        codes.append(actual.returncode)
    value = {'actualExit': next((code for code in codes if code), 0), 'phaseExits': codes, 'operatorSource': operator, 'productionSource': SOURCE, 'sourceQualified': operator == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() and not subprocess.check_output(['git', 'status', '--porcelain']), 'guardSha256': hashlib.sha256(raw.encode()).hexdigest(), 'sameFourOrdinaryOwnersBeforeAfter': True, 'sameSocksBeforeAfter': True, 'independentNormalTlsBeforeAfter': json.loads(before)['tls'], 'sharedCurrentBrowserIgnoreHttpsErrors': True, 'browserStandardTrustStoreQualified': False, 'plannedCases': 12, 'passedCases': len(list((out / 'cases').glob('PT-NBR-*.safe.json'))), 'all24IndependentPost': len(codes) == 2 and not any(codes), 'startedUTC': start, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'formalAccepted': False, 'ownedStopIssued': False, 'nativeGlobalAccepted': False}
    with (out / 'manifest.safe.json').open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())
    print(json.dumps(value, sort_keys=True))
    return value['actualExit'] or (0 if value['sourceQualified'] else 1)


if __name__ == '__main__':
    raise SystemExit(main())
