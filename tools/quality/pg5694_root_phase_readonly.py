"""One currentRoot same-generation phase/technical step read; no lifecycle or data mutation."""
import pg5644_current_admission_image as admission

SLOT='pg5694-root-phase-readonly-v1'


def payload(binding):
    return 'BINDING='+repr(binding)+'\nSOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+r'''
import datetime,hashlib,json,pathlib,subprocess,time
def require(value):
 if value is not True:raise ValueError('same original Root phase read refused')
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==BINDING['boot'])
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
names=['schubert-nk-morning-controller.service','schubert-nk-backup.service','artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service']
units={}
for name in names:
 r=subprocess.run(['systemctl','show',name,'--property=MainPID,ControlPID,Job,ActiveState,SubState,InvocationID,ExecMainStartTimestampMonotonic,ExecMainStatus'],capture_output=True,text=True,timeout=10)
 require(r.returncode==0);units[name]=dict(line.split('=',1)for line in r.stdout.splitlines())
root=units[names[0]];require(root['InvocationID']==BINDING['invocation']and root['ExecMainStartTimestampMonotonic']==str(BINDING['start']))
require(len(BINDING['run'])==36 and all(c in '0123456789abcdef-'for c in BINDING['run']))
sql="begin isolation level repeatable read read only;set local statement_timeout='5s';select coalesce(jsonb_agg(jsonb_build_object('step',step,'status',status,'attempt',attempt,'target_count',target_count,'success_count',success_count,'failure_count',failure_count,'started_at',started_at,'ended_at',ended_at,'error_code',error_code) order by step),'[]'::jsonb)from schubert.batch_runs where run_id='"+BINDING['run']+"'::uuid;commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=sql.encode(),capture_output=True,timeout=15)
require(r.returncode==0);rows=json.loads(r.stdout);require(type(rows)is list)
require(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()==manifest)
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':SOURCE,'BOM':BOM,'run':BINDING['run'],'elapsedSeconds':time.monotonic()-BINDING['start']/1e6,'units':units,'technicalBatchSteps':rows,'readOnly':True,'newStartStopReload':False,'formalAccepted':False}))
'''


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(admission.live()),150))
