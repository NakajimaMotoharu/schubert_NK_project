"""Independent bounded Linux nonleader-exec fixture; no business Unit/DB/permit operation."""
import pg5644_current_admission_image as admission

SLOT='pg5706-exec-generation-reproducer-v1'
GUEST=r'''
import json,os,pathlib,select,subprocess,time
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
child_program=r"""
import os,sys,threading,time
gate=threading.Event()
for _ in range(24):
 t=threading.Thread(target=lambda:gate.wait(5));t.start()
def replacement():
 print('READY',flush=True)
 assert sys.stdin.readline()=='EXEC\n'
 os.execv('/usr/bin/sleep',['sleep','0.08'])
threading.Thread(target=replacement).start()
while True:time.sleep(.01)
"""
def snapshot(pid):
 text=pathlib.Path('/proc',str(pid),'stat').read_text();fields=text.rsplit(') ',1)[1].split()
 return fields[0],int(fields[19])
trials=[];overall=time.monotonic()+25
for attempt in range(32):
 if time.monotonic()>=overall:break
 p=subprocess.Popen(['python3','-B','-c',child_program],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 with select.epoll()as notice:
  notice.register(p.stdout.fileno(),select.EPOLLIN)
  assert notice.poll(3)and p.stdout.readline()=='READY\n'
 before=snapshot(p.pid);fd=os.pidfd_open(p.pid);poll=select.poll();poll.register(fd,select.POLLIN)
 p.stdin.write('EXEC\n');p.stdin.flush();states=[];transient=[];after_exec=None
 try:
  deadline=time.monotonic()+3
  while time.monotonic()<deadline:
   try:
    state,ticks=snapshot(p.pid)
    if not states or states[-1]!=state:states.append(state)
    ready=bool(poll.poll(0))
    if state=='Z'and not ready:transient.append({'state':state,'sameStartTicks':ticks==before[1],'pidfdExitReady':False})
    command=pathlib.Path('/proc',str(p.pid),'cmdline').read_bytes()
    if command==b'sleep\x000.08\x00':after_exec={'state':state,'sameStartTicks':ticks==before[1],'pidfdExitReady':ready}
    if ready:break
   except FileNotFoundError:break
  code=p.wait(timeout=3);stderr=p.stderr.read();assert code==0 and stderr==''
  trials.append({'attempt':attempt+1,'states':states,'transientZombieWhileGroupNotExited':transient[:4],'sameGenerationAfterExec':after_exec,'naturalExit':code,'signalsSent':0})
 finally:
  os.close(fd);p.stdin.close();p.stdout.close();p.stderr.close()
 if transient and after_exec and after_exec['sameStartTicks']and after_exec['pidfdExitReady']is False:break
found=any(r['transientZombieWhileGroupNotExited']and r['sameGenerationAfterExec']and r['sameGenerationAfterExec']['sameStartTicks']and r['sameGenerationAfterExec']['pidfdExitReady']is False for r in trials)
print(json.dumps({'actualExit':0,'independentKernelFixture':True,'transientZombieExecReproduced':found,'trials':trials,'productionRootReplayed':False,'newBusinessUnitStarted':False,'dbWrites':0,'formalAccepted':False}))
'''


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,GUEST,90))
