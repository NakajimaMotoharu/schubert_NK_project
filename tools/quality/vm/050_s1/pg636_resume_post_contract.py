"""Independent SSC229 prepared-runtime post; no deployment helper imports."""
import json
import re
import hashlib

MORNING='schubert-nk-morning-controller.service'
RUNTIME='/run/systemd/system/'+MORNING+'.d/pg635-once-resume.conf'
RUN='e49243d5-de84-4714-8612-6912ddc17e9e'
RESET={'artemis.service','caddy.service','schubert-nk-api.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','schubert-nk-web.service'}


def prepared(before,after,raw):
    def require(v):
        if not v: raise ValueError('independent prepared runtime rejected')
    def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)
    def decl(v):
        require(type(v)is str)
        m=re.fullmatch(r'\{ path=([^ ;\r\n]+) ; argv\[\]=([^\r\n]+) ; ignore_errors=(no|yes) ; start_time=\[([^\]\r\n]*)\] ; stop_time=\[([^\]\r\n]*)\] ; pid=([0-9]+) ; code=([^ ;]+) ; status=([^ ;]+) \}',v)
        require(m is not None);return m.groups()
    fields=set('backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split())
    require(type(before)is dict and type(after)is dict and set(before)==set(after)==fields and type(raw)is bytes)
    require(before['runtime']is None)
    require(all(exact(before[k],after[k])for k in fields-{'configuration','runtime','unitFiles','caddyPre'}))
    require(set(before['configuration'])==set(after['configuration']))
    a=decl(before['configuration'][MORNING]['ExecStart']);newargv=a[1]+' --resume '+RUN
    require(a[0]=='/usr/bin/java'and a[2]=='no'and '--resume'not in a[1])
    expected=b'# SSC228: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+newargv.encode('ascii')+b'\n'
    require(raw==expected)
    native='/etc/systemd/system/'+MORNING+'.d/pg477-native-coverage.conf'
    for unit,old in before['configuration'].items():
        new=after['configuration'][unit];require(set(new)==set(old))
        if unit!=MORNING and unit not in RESET:require(exact(old,new));continue
        allowed={'ExecStart','DropInPaths'}if unit==MORNING else{'ExecStart'}
        require(all(exact(old[k],new[k])for k in old.keys()-allowed))
        x,y=decl(old['ExecStart']),decl(new['ExecStart'])
        if unit==MORNING:
            require(y[:3]==('/usr/bin/java',newargv,'no')and y[3:]==('n/a','n/a','0','(null)','0/0'))
            require(old['DropInPaths']==native and new['DropInPaths']==native+' '+RUNTIME)
        else:require(x[:3]==y[:3]and(exact(old['ExecStart'],new['ExecStart'])or y[3:]==('n/a','n/a','0','(null)','0/0')))
    x,y=decl(before['caddyPre']),decl(after['caddyPre']);require(x[:3]==y[:3])
    if before['caddyPre']!=after['caddyPre']or before['configuration']['caddy.service']['ExecStart']!=after['configuration']['caddy.service']['ExecStart']:
        require(y[3:]==decl(after['configuration']['caddy.service']['ExecStart'])[3:]==('n/a','n/a','0','(null)','0/0'))
    require(set(after['unitFiles'])==set(before['unitFiles'])|{RUNTIME})
    require(all(exact(v,after['unitFiles'][p])for p,v in before['unitFiles'].items()))
    runtime=after['runtime'];require(type(runtime)is dict and set(runtime)=={'metadata','sha256'}and exact(runtime,after['unitFiles'][RUNTIME]))
    m=runtime['metadata'];require(type(m)is list and len(m)==9 and all(type(v)is int for v in m))
    require(m[2:7]==[0,0,33188,1,len(raw)]and runtime['sha256']==hashlib.sha256(raw).hexdigest())
    return True
