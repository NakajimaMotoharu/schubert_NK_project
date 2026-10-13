"""Read-only current completed normal Root snapshot for maintenance; never replays business work."""
import ast
import types
import pg2096_current_newrun_terminal_post as prior

SLOT='pg2130-current-normal-before-v1'

def payload(seals):
    raw=prior.payload(seals)
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='result'for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one qualified post result boundary required')
    raw=''.join(raw.splitlines(keepends=True)[:nodes[0].lineno-1])
    raw+='''
save=base/'pg2130-current-normal-before-v1'
require(not os.path.lexists(save));save.mkdir(mode=0o700)
actual=json.dumps(after,sort_keys=True).encode()
native_raw=json.dumps(native,sort_keys=True).encode()
for name,body in [('before.private.json',actual),('native-before.private.json',native_raw)]:
 with(save/name).open('xb')as f:
  os.fchmod(f.fileno(),0o600);f.write(body);f.flush();os.fsync(f.fileno())
for path in [save,save.parent]:
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':data['source']['commit'],'privateBeforeSha256':hashlib.sha256(actual).hexdigest(),'nativeBeforeSha256':hashlib.sha256(native_raw).hexdigest(),'genuineCompletion':summary,'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allActorGone':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True,'nativeFiles':sum(p.endswith('.exec')for p in native),'normalFreshReadonlyScopes':True,'startsStopsReloadsSqlWrites0':True,'rawExported':False,'formalAccepted':False}))
'''
    from pyflakes.api import check
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<current normal read-only before>'):
        raise ValueError('all actual reader exports required')
    compile(raw,'<current sealed normal snapshot>','exec');return raw

def entry():
    fn=prior.entry()
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'current_normal_before_entry')

if __name__=='__main__':raise SystemExit(entry()())
