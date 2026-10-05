"""SSC193: manager Invocation substitution in one independent transient ordinary probe.
No application start/stop, ready/permit, secret environment or production unit mutation.
"""
import datetime,json,os,pathlib,subprocess
UNIT='pgpt-p469-invocation-env-v1.service'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg469-invocation-env-v1')
def main():
 assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
 r=subprocess.run(['/usr/bin/systemctl','show',UNIT,'--property=LoadState'],capture_output=True,timeout=5)
 assert r.stdout==b'LoadState=not-found\n' and not SAVE.exists()
 SAVE.mkdir(mode=0o700)
 code="import os,re,sys,json; value=os.environ['INVOCATION_ID']; assert re.fullmatch(r'(?!0{32}$)[0-9a-f]{32}',value); assert sys.argv[1]==value; assert os.getuid()==999; print(json.dumps({'managerArgumentEqualsActualInvocation':True,'ordinaryUid999':True,'noSecretEnvironmentExported':True}))"
 args=['/usr/bin/systemd-run','--unit='+UNIT,'--wait','--pipe','--collect','--expand-environment=yes','--property=Type=exec','--property=User=schubert-api','--property=Group=schubert-api','--property=NoNewPrivileges=yes','--property=CapabilityBoundingSet=','--property=Restart=no','--property=RuntimeMaxSec=5','--property=TimeoutStartSec=10','--property=TimeoutStopSec=5','--property=SendSIGKILL=no','/usr/bin/python3','-c',code,'${INVOCATION_ID}']
 (SAVE/'reserved.private.json').write_text(json.dumps({'unit':UNIT,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'applicationStartStop0':True}));(SAVE/'reserved.private.json').chmod(0o600)
 r=subprocess.run(args,capture_output=True,timeout=25)
 p=SAVE/'execution.private.log';p.write_bytes(r.stdout+r.stderr);p.chmod(0o600)
 assert r.returncode==0
 value=json.loads(r.stdout);assert value==dict(managerArgumentEqualsActualInvocation=True,ordinaryUid999=True,noSecretEnvironmentExported=True)
 after=subprocess.run(['/usr/bin/systemctl','show',UNIT,'--property=LoadState,MainPID,ControlPID,Job'],capture_output=True,timeout=5)
 fields=dict(l.split('=',1) for l in after.stdout.decode().splitlines())
 assert fields==dict(LoadState='not-found',MainPID='0',ControlPID='0',Job='')
 summary={**value,'actualExit':r.returncode,'transientCollected':True,'applicationStartStop0':True,'formal':False}
 p=SAVE/'complete.safe.json';p.write_text(json.dumps(summary));p.chmod(0o600);print(json.dumps(summary))
if __name__=='__main__':main()
