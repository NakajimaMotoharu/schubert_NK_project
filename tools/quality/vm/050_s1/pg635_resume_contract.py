"""SSC228 exact new one-use resume delta; independent of Production serializers."""
import re
import stat
from pg633_pending_contract import same_value
from pg604_unit_sources import sources

MORNING='schubert-nk-morning-controller.service'
RUN='e49243d5-de84-4714-8612-6912ddc17e9e'
RUNTIME='/run/systemd/system/'+MORNING+'.d'
NAME='pg635-once-resume.conf'
TARGET=RUNTIME+'/'+NAME
NATIVE='/etc/systemd/system/'+MORNING+'.d/pg477-native-coverage.conf'
HISTORY_UNITS=frozenset(('artemis.service','caddy.service','schubert-nk-api.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','schubert-nk-web.service'))


def require(v):
    if not v: raise ValueError('fixed one-use resume delta refused')


def record(value):
    if type(value) is not str or len(value)>65536: return None
    pattern=r'\{ path=([^ ;\r\n]+) ; argv\[\]=([^\r\n]*?) ; ignore_errors=(yes|no) ; start_time=\[([^\]\r\n]*)\] ; stop_time=\[([^\]\r\n]*)\] ; pid=([0-9]+) ; code=([^ ;\r\n]+) ; status=([^ ;\r\n]+) \}'
    match=re.fullmatch(pattern,value)
    if match is None: return None
    parts=match.groups()
    if not parts[0].startswith('/') or any(x in parts[1] for x in [' ; ignore_errors=',' ; start_time=',' ; stop_time=',' ; pid=',' ; code=',' ; status=']):return None
    return parts


def fixed_dropin(base,native):
    require(type(base) is bytes and type(native) is bytes)
    starts=[r.removeprefix(b'ExecStart=') for r in base.splitlines() if r.startswith(b'ExecStart=')]
    require(len(starts)==1 and starts[0].startswith(b'/usr/bin/java ')
            and starts[0].endswith(b' dev.codex.schubert.nk.batch.file.MorningProcessMain')
            and b'--resume' not in starts[0] and b'-javaagent' not in starts[0])
    agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false '
    argv=starts[0].replace(b'/usr/bin/java ',agent,1)
    expected=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
    require(native==expected)
    return b'# SSC228: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+b' --resume '+RUN.encode()+b'\n'


def unit_sources(rows,changed):
    require(type(changed) is bool and type(rows) is dict)
    adjusted={u:dict(v)for u,v in rows.items()}
    if changed:
        raw=adjusted[MORNING]['DropInPaths'];require(type(raw) is str and raw.split().count(TARGET)==1)
        adjusted[MORNING]['DropInPaths']=' '.join(p for p in raw.split() if p!=TARGET)
    result=list(sources(adjusted))
    if changed:result.append(TARGET)
    return tuple(sorted(result))


def changed_only(before,after,dropin):
    require(type(before) is dict and type(after) is dict and set(before)==set(after))
    require(before['runtime'] is None and type(after['runtime']) is dict)
    require(type(dropin) is bytes)
    for key in before.keys()-{'configuration','runtime','unitFiles','caddyPre'}:require(same_value(before[key],after[key]))
    expected_argv=next(r[10:].decode('ascii') for r in dropin.splitlines() if r.startswith(b'ExecStart=') and r!=b'ExecStart=')
    require(expected_argv.endswith(' --resume '+RUN))
    for unit,old in before['configuration'].items():
        new=after['configuration'][unit];require(set(new)==set(old))
        if unit!=MORNING and unit not in HISTORY_UNITS:
            require(same_value(old,new));continue
        allowed={'ExecStart','DropInPaths'} if unit==MORNING else {'ExecStart'}
        require(all(same_value(old[k],new[k])for k in old.keys()-allowed))
        a,b=record(old['ExecStart']),record(new['ExecStart']);require(a is not None and b is not None)
        require(a[:3]==('/usr/bin/java',expected_argv.removesuffix(' --resume '+RUN),'no') if unit==MORNING else a[:3]==b[:3])
        if unit==MORNING:
            require(b[:3]==('/usr/bin/java',expected_argv,'no')and b[3:]==('n/a','n/a','0','(null)','0/0'))
            require(old['DropInPaths']==NATIVE and new['DropInPaths']==NATIVE+' '+TARGET)
        else:require(old['ExecStart']==new['ExecStart'] or b[3:]==('n/a','n/a','0','(null)','0/0'))
    a,b=record(before['caddyPre']),record(after['caddyPre']);require(a is not None and b is not None and a[:3]==b[:3])
    if before['caddyPre']!=after['caddyPre'] or before['configuration']['caddy.service']['ExecStart']!=after['configuration']['caddy.service']['ExecStart']:
        c=record(after['configuration']['caddy.service']['ExecStart'])
        require(b[3:]==c[3:]==('n/a','n/a','0','(null)','0/0'))
        history=after['units']['caddy.service']
        require(history['Result']=='success' and history['ExecMainCode']=='1' and history['ExecMainStatus']=='0')
    require(set(after['unitFiles'])==set(before['unitFiles'])|{TARGET})
    require(all(same_value(v,after['unitFiles'][p])for p,v in before['unitFiles'].items()))
    runtime=after['runtime'];require(set(runtime)=={'metadata','sha256'}and same_value(runtime,after['unitFiles'][TARGET]))
    metadata=runtime['metadata'];require(type(metadata) is list and len(metadata)==9 and all(type(v)is int for v in metadata))
    require(metadata[2:7]==[0,0,stat.S_IFREG|0o644,1,len(dropin)])
    import hashlib
    require(runtime['sha256']==hashlib.sha256(dropin).hexdigest())
    return True
