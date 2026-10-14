"""Shared Current browser after genuine DONE, retaining same ordinary generations; no Root replay."""
import ast
import json
import pg2884_network_newcurrent_a01 as prior
from pg1446_current_cold_stage import W


def code():
    seal=json.loads((W/'pg2886-network-newcurrent-full-seal-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2878-network-newcurrent-terminal-v1/manifest.safe.json').read_bytes())
    if any(v.get('actualExit')!=0 or v.get('productionSource')!=prior.SOURCE for v in [seal,term])or term.get('genuineParentDone')is not True:
        raise ValueError('genuine current fullseal/terminal required, UNKNOWN never completed')
    owned=seal['observedOwned']
    raw=prior.code().replace('PG2884','PG2900').replace('pg2884','pg2900')
    guard='EXPECTED='+repr(owned)+'\nDONE_SHA='+repr(term['proofHashes']['done.private'])+'\n'+GUARD
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GUARD'for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one actual A01 owner guard required')
    raw=raw.replace(ast.get_source_segment(raw,nodes[0]),'GUARD='+repr(guard))
    raw=raw.replace("'sameCapturedParentApiWebCaddyBeforeAfter':True,","'sameCapturedParentApiWebCaddyBeforeAfter':True,'parentGenuineDoneInsteadOfAlive':True,'noRootReplay':True,")
    from pyflakes.api import check
    if check(raw,'<whole completed-parent ordinary A01>'):raise ValueError('complete same actual completed owner browser graph required')
    compile(raw,'<real unchanged Current driver and qualified completed ownership>','exec');return raw


GUARD=r'''
import hashlib,json,pathlib,subprocess
require=lambda v:None if v else (_ for _ in ()).throw(ValueError('same completed current ordinary owner refused'))
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
done=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/74729e17-91c0-43e7-b01f-74f9e6461d6a.done')
require(hashlib.sha256(done.read_bytes()).hexdigest()==DONE_SHA)
require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
fields='InvocationID,MainPID,ControlPID,Job,ExecMainStartTimestampMonotonic,ExecMainCode,ExecMainStatus,Result'
units={}
for unit in ['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
 units[unit]=dict(x.split('=',1)for x in subprocess.check_output(['systemctl','show',unit,'--property='+fields],text=True).splitlines())
parent=units['schubert-nk-morning-controller.service'];require(parent['MainPID']==parent['ControlPID']=='0'and not parent['Job']and parent['Result']=='success')
for unit in ['schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
 value=units[unit];pid,inv,ticks,argv_sha=EXPECTED[unit]
 require(value['MainPID']==pid and value['InvocationID']==inv and value['ControlPID']=='0'and not value['Job']and value['Result']=='success')
 p=pathlib.Path('/proc')/pid;raw=(p/'cmdline').read_bytes()
 require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks and hashlib.sha256(raw).hexdigest()==argv_sha and(p/'cgroup').read_text()=='0::/system.slice/'+unit+'\n')
release=pathlib.Path('/opt/schubert-nk/current');raw=(release/'RELEASE-MANIFEST.json').read_bytes()
require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG2802'and hashlib.sha256(raw).hexdigest()=='37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863')
require(json.loads(raw)['source']['commit']=='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25')
require(hashlib.sha256(done.read_bytes()).hexdigest()==DONE_SHA)
print(json.dumps(units))
'''


def main():
    ns={'__file__':__file__,'__name__':'completed_current_a01'}
    exec(compile(code(),'<genuine done and same ordinary real Browser>','exec'),ns);ns['main']()


if __name__=='__main__':main()
