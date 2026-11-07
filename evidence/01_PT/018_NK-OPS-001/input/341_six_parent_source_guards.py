"""Independently unwrap exact six new TWR owners and restore full original Test tokens; source only."""
from pathlib import Path
import datetime,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG23116-six-parent-source-guards-v1';sp=importlib.util.spec_from_file_location('tokens',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def find(t,a):
 a=tok(a);matches=[i for i in range(len(t)) if t[i:i+len(a)]==a];assert matches;return matches[0],len(a)
def end(t,start,left,right):
 assert t[start]==left;depth=1;i=start+1
 while depth:
  depth+=(t[i]==left)-(t[i]==right);i+=1
 return i

def unwrap(t,owner,name,decl,restore_try,cleanup=None):
 i,n=find(t,f'try(var {owner}=new OwnedTestProcess(');j=end(t,i+n-1,'(',')');assert t[j:j+2]==[')','{'];builder=t[i+n:j-1];last=end(t,j+1,'{','}');body=t[j+2:last-1];binding=tok(f'{decl} {name}={owner}.process();');assert body[:len(binding)]==binding;body=body[len(binding):]
 if restore_try:body=tok('try{')+body+tok('}finally{'+cleanup+'}')
 elif cleanup:
  a,n=find(body,owner+'.close();');body=body[:a]+tok(cleanup)+body[a+n:]
 return t[:i]+tok(decl+' '+name+'=')+builder+tok(';')+body+t[last:]
def inverse(s,name):
 t=tok(s)
 if name=='LinuxExecDescriptorsTest.java':
  for n in ['competitor','after']:t=unwrap(t,n+'Owner',n,'var',False)
 elif name=='LinuxInodeSecurityTest.java':t=unwrap(t,'processOwner','process','Process',True,'process.destroyForcibly();')
 else:
  if name=='LinuxFileLockTest.java':t=unwrap(t,'childOwner','child','var',False,'if(child.isAlive())child.destroy();')
  t=unwrap(t,'childOwner','child','var',True,'if(child.isAlive())child.destroy();')
 return t

def main():
 assert not O.exists();oldp=B/'evidence/PG23114-six-parent-original-v1/manifest.json';m=json.loads(oldp.read_bytes());rows=[];neg=[]
 for v in m['inputs']:
  p=R/v['path'];old=B/'evidence/PG23114-six-parent-original-v1'/v['backup'];assert sha(old)==v['sha256'];s=p.read_text();assert inverse(s,p.name)==tok(old.read_text());rows.append(dict(path=v['path'],sha256=sha(p),originalSha256=v['sha256'],allOtherTokensArgvFixturesOraclesAndReturnsPreserved=True))
  # Every new owner accessor, including both distinct FileLock sites, is checked separately.
  owners=['competitorOwner','afterOwner'] if p.name=='LinuxExecDescriptorsTest.java' else ['processOwner'] if p.name=='LinuxInodeSecurityTest.java' else ['childOwner'];
  for owner in owners:
   a=owner+'.process()';starts=[i for i in range(len(s)) if s.startswith(a,i)];assert starts
   for start in starts:
    changed=s[:start]+a+'.toHandle()'+s[start+len(a):]
    try:valid=inverse(changed,p.name)==tok(old.read_text())
    except AssertionError:valid=False
    assert not valid;neg.append(dict(path=v['path'],owner=owner,offset=start))
 assert len(neg)==6;assert sha(R/m['retainedHelper'])==m['retainedHelperSha256'];O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=rows,metadataNegativeGuards=neg,retainedHelper=dict(path=m['retainedHelper'],sha256=m['retainedHelperSha256']),sourceParentRemedies=6,totalParentSourceRemedies=8,originalTestCompileRun=0,productTestsExecuted=0,actualProcessActions=0,actualPass=None,coverage=None,forkCommandSitesStillOpen=5,bugs=['BUG-2467','BUG-2468'],ykts=['YKT-2205','YKT-2206']);(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('all six owners inverse whole4 source tokens0/owner negatives6; actual Test/process actions0')
if __name__=='__main__':main()
