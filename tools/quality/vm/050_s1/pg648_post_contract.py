"""Independent SSC230 literal postconditions, no retirement helper imports."""
import hashlib
import json
import re

MORNING = 'schubert-nk-morning-controller.service'
RUNTIME = '/run/systemd/system/'+MORNING+'.d/pg635-once-resume.conf'
RESET = {'artemis.service','caddy.service','schubert-nk-api.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','schubert-nk-web.service'}


def retired(before, after):
    def require(v):
        if not v: raise ValueError('independent completed retirement rejected')
    def exact(a,b): return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)
    def decl(v):
        require(type(v) is str)
        m=re.fullmatch(r'\{ path=([^ ;\r\n]+) ; argv\[\]=([^\r\n]+) ; ignore_errors=(no|yes) ; start_time=\[([^\]\r\n]*)\] ; stop_time=\[([^\]\r\n]*)\] ; pid=([0-9]+) ; code=([^ ;]+) ; status=([^ ;]+) \}',v)
        require(m is not None); return m.groups()
    fields=set('backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split())
    require(type(before) is dict and type(after) is dict and set(before)==set(after)==fields)
    require(after['runtime'] is None and all(exact(before[k],after[k])for k in fields-{'configuration','runtime','unitFiles','caddyPre'}))
    require(set(before['configuration'])==set(after['configuration']))
    x=decl(before['configuration'][MORNING]['ExecStart'])
    suffix=' --resume e49243d5-de84-4714-8612-6912ddc17e9e'
    require(x[0]=='/usr/bin/java' and x[2]=='no' and x[1].endswith(suffix))
    plain=x[1][:-len(suffix)];require('--resume' not in plain)
    raw=b'# SSC228: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+x[1].encode('ascii')+b'\n'
    require(type(before['runtime']) is dict and before['runtime']['sha256']==hashlib.sha256(raw).hexdigest()
            and exact(before['runtime'],before['unitFiles'][RUNTIME]))
    native='/etc/systemd/system/'+MORNING+'.d/pg477-native-coverage.conf'
    for unit, old in before['configuration'].items():
        new=after['configuration'][unit];require(set(old)==set(new))
        if unit!=MORNING and unit not in RESET:require(exact(old,new));continue
        allowed={'ExecStart','DropInPaths'}if unit==MORNING else{'ExecStart'}
        require(all(exact(old[k],new[k])for k in old.keys()-allowed))
        a,b=decl(old['ExecStart']),decl(new['ExecStart'])
        if unit==MORNING:
            require(b==('/usr/bin/java',plain,'no','n/a','n/a','0','(null)','0/0'))
            require(old['DropInPaths']==native+' '+RUNTIME and new['DropInPaths']==native)
        else:require(a[:3]==b[:3] and (old['ExecStart']==new['ExecStart']or b[3:]==('n/a','n/a','0','(null)','0/0')))
    a,b=decl(before['caddyPre']),decl(after['caddyPre']);require(a[:3]==b[:3])
    if before['caddyPre']!=after['caddyPre']or before['configuration']['caddy.service']['ExecStart']!=after['configuration']['caddy.service']['ExecStart']:
        require(b[3:]==decl(after['configuration']['caddy.service']['ExecStart'])[3:]==('n/a','n/a','0','(null)','0/0'))
    require(set(after['unitFiles'])==set(before['unitFiles'])-{RUNTIME}
            and all(exact(v,before['unitFiles'][p])for p,v in after['unitFiles'].items()))
    return True
