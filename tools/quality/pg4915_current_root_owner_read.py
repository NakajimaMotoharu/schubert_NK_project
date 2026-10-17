"""One bounded currentRoot witness; never start/stop/reuse an old PID as authority."""
import inspect
import json
import pg4900_current_admission_image as admission

SLOT='pg4915-current-root-owner-read-v1'


def validate(state,binding,pid):
    wanted={'MainPID':str(pid),'ControlPID':'0','Job':binding['job'],'InvocationID':binding['invocation'],
            'ExecMainStartTimestampMonotonic':str(binding['start']),'ActiveState':'activating','SubState':'start'}
    if state!=wanted:raise ValueError('same actual live Root generation required')


def server(data):
    import hashlib
    import json
    import os
    from pathlib import Path
    import select
    import stat
    import subprocess
    import time
    b=data['binding'];pid=data['rootPid'];p=Path('/proc')/str(pid)
    def require(value):
        if not value:raise ValueError('current Root owner witness refused')
    require(os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==b['boot'])
    manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()
    require(hashlib.sha256(manifest).hexdigest()==data['bom'] and json.loads(manifest)['source']['commit']==data['source'])
    def show():
        cmd=['systemctl','show','schubert-nk-morning-controller.service','--property=MainPID,ControlPID,Job,InvocationID,ExecMainStartTimestampMonotonic,ActiveState,SubState']
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=5);require(result.returncode==0)
        return dict(row.split('=',1)for row in result.stdout.splitlines())
    fd=os.pidfd_open(pid,0)
    try:
        poll=select.poll();poll.register(fd,select.POLLIN);require(poll.poll(0)==[])
        first=show();validate(first,b,pid)
        argv=(p/'cmdline').read_bytes();ticks=int((p/'stat').read_text().rsplit(')',1)[1].split()[19])
        require(ticks==data['rootTicks'] and hashlib.sha256(argv).hexdigest()==data['argvSha256'])
        status=dict(row.split(':',1)for row in(p/'status').read_text().splitlines()if ':'in row)
        require(status['Uid'].split()==status['Gid'].split()==['0']*4)
        active=Path('/var/lib/schubert-nk/maintenance/active');s=active.lstat()
        require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(active))
        raw=active.read_bytes();require(hashlib.sha256(raw).hexdigest()==data['activeSha256'])
        elapsed=(time.monotonic_ns()//1000-b['start'])/1000000
        require(0<=elapsed<1800 and show()==first and(p/'cmdline').read_bytes()==argv
                and int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==ticks and active.read_bytes()==raw and poll.poll(0)==[])
    finally:os.close(fd)
    print(json.dumps({'actualExit':0,'productionSource':data['source'],'run':b['run'],'activation':b['activation'],
                      'rootPid':pid,'ticks':ticks,'argvSha256':data['argvSha256'],'rootBudgetSeconds':1800,
                      'elapsedSeconds':elapsed,'pidfdAliveBeforeAfter':True,'sameGenerationBeforeAfter':True,
                      'rootGenuineDone':False,'stateChangingActions':0,'formalAccepted':False}))


def payload():
    outer=json.loads((admission.W/admission.LIVE/'manifest.safe.json').read_bytes())
    if not(type(outer['actualExit'])is int and outer['actualExit']==0 and outer['source']==admission.SOURCE):raise ValueError('actual current binding first')
    v=outer['result'];data={'binding':v['binding'],'rootPid':v['rootPid'],'rootTicks':v['rootTicks'],
                          'argvSha256':v['rootArgvSha256'],'activeSha256':v['activeSha256'],'source':admission.SOURCE,'bom':admission.BOM}
    return '\n'.join(inspect.getsource(f)for f in (validate,server))+'\nDATA='+repr(data)+'\nserver(DATA)\n'


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(),30))
