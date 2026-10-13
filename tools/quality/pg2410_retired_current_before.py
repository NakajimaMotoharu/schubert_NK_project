"""Current retired, completed 3b7f image for new-resource maintenance, readonly only."""
import ast
import types
from pyflakes.api import check
import pg2400_retired_current_backup_content as prior

SLOT = 'pg2410-retired-current-before-v1'


def payload(seals):
    raw = prior.payload(seals)
    results = [n for n in ast.parse(raw).body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == 'result' for t in n.targets)]
    if len(results) != 1:
        raise ValueError('one independently qualified retired image boundary required')
    raw = ''.join(raw.splitlines(keepends=True)[:results[0].lineno - 1])
    raw += '''
save=base/'pg2410-retired-current-before-v1'
require(not os.path.lexists(save));save.mkdir(mode=0o700)
# The original maintenance schema stores native metadata separately. Preserve
# every other authenticated field, and verify the sole extracted field.
require(set(after)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'})
require(after['native']==native)
flat={k:v for k,v in after.items()if k!='native'}
actual=json.dumps(flat,sort_keys=True).encode()
native_raw=json.dumps(native,sort_keys=True).encode()
for name,body in [('before.private.json',actual),('native-before.private.json',native_raw)]:
 with(save/name).open('xb')as f:
  os.fchmod(f.fileno(),0o600);f.write(body);f.flush();os.fsync(f.fileno())
for path in [save,save.parent]:
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':data['source']['commit'],'privateBeforeSha256':hashlib.sha256(actual).hexdigest(),'nativeBeforeSha256':hashlib.sha256(native_raw).hexdigest(),'genuineCompletion':summary,'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allActorGone':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True,'nativeFiles':sum(p.endswith('.exec')for p in native),'normalFreshReadonlyScopes':True,'runtimeAlreadyRetired':True,'independentBackupSummary':backup_result[0],'startsStopsReloadsSqlWrites0':True,'rawExported':False,'formalAccepted':False}))
'''
    if check('HASHES={}\nRECEIPT="actual"\n' + raw, '<current retired maintenance before>'):
        raise ValueError('all actual retained original globals required')
    compile(raw, '<current retired before>', 'exec')
    return raw


def entry():
    fn = prior.entry()
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT':SLOT,'payload':payload},
                              'retired_current_before_entry')


if __name__ == '__main__':
    raise SystemExit(entry()())
