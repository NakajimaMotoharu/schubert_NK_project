"""Independent new-only stage/stop dispatch; genuine846+A01 required, no start/revoke."""
import ast
from pathlib import Path
import sys
R=Path(__file__).resolve().parent
def source():
 raw=(R/'pg841_resume.py').read_text()
 # Use the already qualified standalone transport, not its mode/profile entrypoint.
 from pg841_resume import source as previous
 raw=previous('stage').replace('Pg841RuntimeResume','Pg847NativeStop').replace('pg841-resume-tools-v1','pg847-native-tools-v1').replace('pg841-fixed-stage-v1','pg847-fixed-stage-v1').replace('pg841-frozen-v1.safe.json','pg847-frozen-v1.safe.json').replace('pg841-','pg847-')
 raw=raw.replace("sys.argv[1]in ('stage','prepare')","sys.argv[1]in ('stage','stop')").replace('Pg847NativeStop prepare','Pg847NativeStop stop').replace('Pg847NativeStopTest','Pg847NativeArgumentTest')
 raw=raw.replace("'genuineParentAccepted':False","'genuineParentAccepted':True,'genuineSourceProofVerified':True")
 marker="    action=sys.argv[1];assert not subprocess.check_output(['git','status','--porcelain'])"
 assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"\n    assert(W/'pg846-completed-readonly-v1.exit').read_text()=='0\\n'and(W/'pg849-chr-a01-native-v1.exit').read_text()=='0\\n'\n    proof=json.loads((W/'pg846-completed-readonly-v1.safe.json').read_text());assert proof['genuineCompletion']['genuineRootDone']and proof['genuineCompletion']['genuinePid1StartDone']")
 ast.parse(raw);return raw
if __name__=='__main__':
 assert sys.argv[1:]in(['stage'],['stop'])
 exec(compile(source(),'<847 genuine original ordered TERM only>','exec'),{'__file__':str(R/'pg847_native_stop.py'),'__name__':'__main__'})
