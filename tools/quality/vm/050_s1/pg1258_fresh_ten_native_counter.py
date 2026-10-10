"""Current fresh run eight plus two real Inspector streams, exact D5 host only."""
import json
import os
from pathlib import Path
import subprocess
import pg1221_current_eight_native_counter as previous
from pg1247_fresh_owned_stop_sources import CHANGES,SOURCE,W

P=previous.P;R=previous.R
BEFORE='8679f1fc50bfe6a1f13d196f314e2c40463050b598decfd0468c382f9e34dd84'
AFTER='7b48c21af7d30d0bdad3d0341ad3a29412fff405540ef95c0ca97328608f8f77'
INSPECTOR='99c487c7c9444c81bf20813d03875565'

def catalog():
    s=previous.catalog().replace('pg1216-native-stop-v1','pg1253-native-stop-v1').replace(previous.BEFORE,BEFORE)
    marker="root=pathlib.Path('/run/schubert-nk/pt-coverage');result={}"
    if s.count(marker)!=1:raise ValueError('fixed current catalog closure required')
    s=s.replace(marker,"names.extend(['ordinary-inspector196/"+INSPECTOR+".terminal.exec','ordinary-inspector196/"+INSPECTOR+".closing.exec'])\n"+marker)
    s=s.replace('assert len(result)==8','assert len(result)==10')
    compile(s,'<actual fresh ten native catalog>','exec');return s

def code(hashes):
    if type(hashes)is not dict or len(hashes)!=10:raise ValueError('ten actual fresh stream hashes required')
    s=previous.code(hashes).replace(previous.BEFORE,BEFORE).replace(previous.AFTER,AFTER)
    for old,new in CHANGES:s=s.replace(old,new)
    for old,new in [('pg1247-native-stop-v1','pg1253-native-stop-v1'),('pg1218-stop-v1.exit','pg1256-stop-v1.exit'),('pg1220-full32-terminal-post-v1','pg1257-fresh-terminal-post-v1'),('pg1221-current-eight-native-v1','pg1258-fresh-ten-native-v1'),('PG1221-current-eight-native-v1','PG1258-fresh-ten-native-v1')]:s=s.replace(old,new)
    marker='for name,unit in names:'
    if s.count(marker)!=1:raise ValueError('actual ten session selection closure required')
    extra="names.extend([('ordinary-inspector196/"+INSPECTOR+".terminal.exec','schubert-nk-inbox-inspector.service'),('ordinary-inspector196/"+INSPECTOR+".closing.exec','schubert-nk-inbox-inspector.service')])\n"
    s=s.replace(marker,extra+marker)
    marker="else:start=int(b['units'][unit]['ExecMainStartTimestampMonotonic']);end=int(a['units'][unit]['ExecMainExitTimestampMonotonic'])"
    if s.count(marker)!=1:raise ValueError('actual Inspector PID1 session interval insertion required')
    s=s.replace(marker,"elif unit=='schubert-nk-inbox-inspector.service':start=61345315043;end=61348488918\n "+marker)
    s=s.replace('len(selected)==8','len(selected)==10').replace("len({v['relative']for v in selected})==8","len({v['relative']for v in selected})==10")
    old="'currentNativeStreams':8,'requiredPlannedStreams':9,'missingCurrentStreams':['ordinary-inspector196 actual current generation terminal'],'wholeNativeAccepted':False,"
    if s.count(old)!=1:raise ValueError('current complete native scope insertion required')
    s=s.replace(old,"'currentNativeStreams':10,'requiredNativeRoles':9,'currentNativeRoles':9,'missingCurrentStreams':[],'qualifiedCurrentNativeSubcampaign':True,'wholeNativeAccepted':False,")
    s=s.replace("'streams':8","'streams':10")
    compile(s,'<actual ten current native and exact D5 host only>','exec');return s

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed current source required')
    post=json.loads((W/'pg1257-fresh-terminal-post-v1.safe.json').read_bytes())
    inspector=json.loads((W/'pg1241-fresh-inspector-provenance-v1.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0']or inspector['actualExit']!=0 or not inspector['genuinePid1StartDoneStop']:raise ValueError('actual same-source full post and Inspector provenance required')
    available=os.statvfs(W).f_bavail*os.statvfs(W).f_frsize;needed=10*16777216*2+268435456+536870912
    if available<needed:raise ValueError('bounded native capture and normal-close cushion insufficient')
    capacity={'availableBytes':available,'boundedNativeInputsBytes':167772160,'temporaryBytes':167772160,'analysisAllowanceBytes':268435456,'normalCloseCushionBytes':536870912,'requiredBytes':needed,'capacityFits':True,'deletions0':True,'extraVmCopies0':True}
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    hashes=json.loads(subprocess.check_output(ssh,input=catalog().encode(),timeout=30))
    expected={INSPECTOR+'.terminal.exec':'330c868ea20828a2fff3666a6cbedd77f06fcf30095d7de711412ce47183025f',INSPECTOR+'.closing.exec':'47910f38118892b0c7618714514a0017ee51d1549e3eb9d37ab339b6606daae6'}
    if any(hashes.get('ordinary-inspector196/'+n)!=digest for n,digest in expected.items()):raise ValueError('actual preserved Inspector hashes changed')
    env={'__name__':'qualified_fresh_ten_d5_native','__file__':str(R/'pg1258_fresh_ten_native_counter.py'),'CAPACITY':capacity}
    exec(compile(code(hashes),'<actual new ten native counter>','exec'),env);env['main']()

if __name__=='__main__':main()
