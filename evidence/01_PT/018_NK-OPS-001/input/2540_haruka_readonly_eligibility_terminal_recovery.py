"""Correct inventory error recording after a nonzero read; no job restart, signals or service changes."""
from pathlib import Path
import json,datetime,hashlib
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';src=b/'input/2539_haruka_readonly_gate_eligibility.py';old=src.read_text();e=b/'evidence/PG30586-haruka-readonly-gate-eligibility-v1'
assert not (e/'manifest.json').exists();(e/'original-driver.py.txt').write_text(old)
(e/'manifest.json').write_text(json.dumps(dict(actualExit=None,status='READONLY_INVENTORY_NONZERO_BEFORE_RESULT_RECORDING',atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='689c5ffff95dd73cb717f2709bd5e4d384001dee',localProducerExit=1,remoteExit='NONZERO_EXACT_VALUE_NOT_PERSISTED',cause='UNKNOWN_REMOTE_DETAIL_NOT_PERSISTED_BY_ORIGINAL_DRIVER',platformSafetyRejectionObserved=False,remoteStateMustNotBeInferred=True,newTests=0,newRuntimeJobs=0,sourceUploads=0,servicesChanged=0,signalsSent=0,next='New-only read-only inventory with missing-path and all-terminal recording; no original job or operation restart; retain failed producer and no successful qualification.'),indent=2)+'\n')
new=old.replace('PG30586-haruka-readonly-gate-eligibility-v1','PG30588-haruka-readonly-gate-eligibility-recorded-v2')
new=new.replace(' s=os.lstat(p);return dict('," if not os.path.lexists(p):return dict(exists=False,path=str(p))\n s=os.lstat(p);return dict(exists=True,")
new=new.replace("assert c.exitstatus==0,'Read-only command nonzero; private output not published'","""terminal=dict(sshExit=c.exitstatus,sshSignal=c.signalstatus,authPrompts=auth,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputPublished=False)
(out/'terminal.json').write_text(json.dumps(terminal,indent=2)+'\\n')
if c.exitstatus!=0:
 # Only allow public inventory traceback lines; raw SSH/auth text stays private in memory.
 lines=[line for line in text.splitlines() if line.startswith(('FileNotFoundError:','PermissionError:','IndexError:','AssertionError:','SyntaxError:'))]
 (out/'failure.json').write_text(json.dumps(dict(actualExit=c.exitstatus,publicInventoryErrors=lines,testsExecuted=0,newRuntimeJobs=0),indent=2)+'\\n')
 raise SystemExit('Read-only inventory failed; terminal and bounded public error preserved, no runtime continuation')""")
new=new.replace("assert v['host']=='haruka' and v['uid']==v['base']['uid']==v['runs']['uid']", "assert v['host']=='haruka' and v['uid']==v['base'].get('uid')==v['runs'].get('uid')")
new=new.replace("and v['unreadableOwnProcessCwds']==0", "and v['unreadableOwnProcessCwds']==0 and v['mavenRepository'].get('exists') is True")
p=b/'input/2541_haruka_readonly_gate_eligibility_recorded_v2.py';assert not p.exists();p.write_text(new)
print(json.dumps(dict(actualExit=0,originalFailurePreserved=True,driverChangedOnlyForAbsentPathAndTerminalRecording=True,newDriver=str(p.relative_to(r)))))
