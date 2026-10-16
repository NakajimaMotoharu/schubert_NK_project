"""Read exact post-Java/pre-Python boundary refusal; never reissue Java/Caddy actions."""
import ast
import hashlib
import json
import os
import subprocess
import pg4360_pool_bound_partial_sources as current
import pg4368_pool_bound_recover as entry
import pg4168_retained_pair_keeper as keeper
from pg4060_original_profile_dual_stack import once
from pg1446_current_cold_stage import W, SSH
from pg4152_exact_failed_done_recover import durable, process

SLOT = 'pg4374-current-half-handoff-read-v1'


def payload():
    raw = current.keeper()
    if hashlib.sha256(raw.encode()).hexdigest() != '647dd2d1c3430587f83ee29c8443155f8e57887eb10209cb82eee5d40aa94641':
        raise ValueError('preserve exact original current keeper')
    raw = raw[:raw.index('import time,signal,select,ctypes,dbus,traceback')]
    raw = once(raw, "save=base/('" + current.KEEPER + "-'+MODE)", "save=base/'" + SLOT + "'")
    # Prefix uses datetime only in the operational result, not this read.
    raw = once(raw, 'import json,hashlib,os,subprocess,datetime', 'import json,hashlib,os,subprocess')
    record = next(n for n in ast.parse(keeper.BODY).body if isinstance(n, ast.FunctionDef) and n.name == 'private_record')
    raw += '\n' + ast.get_source_segment(keeper.BODY, record) + '\n' + current.extension()
    hashes = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in current.files().items()}
    raw += '\nKEEPER_PROGRAM=' + repr(entry.bootstrap('keeper.py', hashes)) + '\n' + BODY
    return raw


BODY = r'''
folder=base/'pg4364-pool-bound-keeper-v3-recover'
matches=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:args=(p/'cmdline').read_bytes().split(b'\0')[:-1]
 except(FileNotFoundError,ProcessLookupError,PermissionError):continue
 if args==[b'python3',b'-B',b'-c',KEEPER_PROGRAM.encode(),b'recover']:matches.append(int(p.name))
require(len(matches)==1)
retainer=proc(matches[0]);python=proc(815643)
fields=(Path('/proc/815726/stat').read_text().rsplit(')',1)[1].split())
require(fields[0]=='Z'and int(fields[1])==815643 and int(fields[19])==15409721 and not list(Path('/proc/815726/fd').iterdir()))
first=capture_snapshot();second=capture_snapshot()
require(not first['flocks']and not second['flocks']and not first['database']['locks']and not second['database']['locks'])
keys=['units','actors','detailedActors','durable','native','startup','runtime','ordinaryDatabaseFds']
changed=[key for key in keys if first[key]!=second[key]]
evidence={name:json.loads((folder/name).read_bytes())for name in ['failure.private.json','java-terminal.private.json','rejected-boundary-pair.changed.private.json']}
hashes={'first':private_record('first.private.json',first),'second':private_record('second.private.json',second),
 'owners':private_record('owners.private.json',{'retainer':retainer,'python':python,'retainerSecond':proc(matches[0]),'pythonSecond':proc(815643),'evidence':evidence})}
require(first['database']['rows']==second['database']['rows']and all(first[k]==second[k]for k in ['durable','native','startup','runtime','actors']))
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'privateSha256':hashes,
 'retainerPid':retainer['pid'],'retainerTicks':retainer['ticks'],'retainerArgvSha256':retainer['argvSha256'],'retainerFdCount':len(retainer['fds']),
 'retainerCgroup':retainer['cgroup'],'retainerParent':retainer['authority']['PPid'],
 'pythonPid':python['pid'],'pythonTicks':python['ticks'],'pythonArgvSha256':python['argvSha256'],'pythonFdCount':len(python['fds']),
 'oldJavaZombieNoFds':True,'oldJavaTermReissueAllowed':False,'managementFlockAdvisory0':True,
 'currentBoundaryChangedKeys':changed,'all24OriginalsStable':True,'originalUnknownNormal':False,'newUnknownNormal':False,
 'signalsStartStopRevokeAck':0,'formalAccepted':False}
private_record('manifest.safe.json',value);print(json.dumps(value))
'''


def main():
    original = W / 'pg4316-current-failed-dispatch-v1-recover'
    owner = json.loads((original / 'start.safe.json').read_bytes())['owner']
    if process(owner['pid']) != owner:
        raise ValueError('original gate owner unchanged before diagnostic')
    os.umask(0o077); out = W / SLOT; out.mkdir(mode=0o700)
    raw = payload(); compile(raw, '<half handoff read>', 'exec')
    with (out / 'payload.private.py').open('x') as f: f.write(raw)
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-', 'proof'], input=raw.encode(), capture_output=True, timeout=180)
    for name, content in [('stdout.private.log', r.stdout), ('stderr.private.log', r.stderr)]:
        with (out / name).open('xb') as f: f.write(content)
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),
             'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'operationsIssued': 0}
    if r.returncode == 0: value['result'] = json.loads(r.stdout)
    durable(out / 'manifest.safe.json', value); print(json.dumps(value))


if __name__ == '__main__':
    main()
