"""Independent all-originals/resource post and finite native delta, not native dump."""
import ast
import inspect
from pg1147_terminal_management_post import payload as previous
import pg1148_native_five_policy as policy
import pg1120_current_failed_capture as transport


def payload():
    s=previous().replace('terminal-management-post-v1','native-five-post-v1')
    i=s.index('COMPLETE=pathlib.Path(');end=s.index('for name,digest in fixed.items():',i)
    s=s[:i]+PINS+s[end:]
    marker=" value=capture();require(value['rows']==expected['rows'])"
    if s.count(marker)!=1:raise ValueError('fixed independent native post insertion refused')
    s=s.replace(marker,marker+NATIVE)
    i=s.index('def post():')
    s=s[:i]+"native_policy=types.ModuleType('independent-five-policy');exec("+repr(inspect.getsource(policy))+",native_policy.__dict__)\n"+s[i:]
    s=s.replace("'allRowsOriginalsBackupSourceUnchanged':True", "'allRowsOriginalsBackupSourceUnchanged':True,'fiveNativeDirectoriesPrepared':True,'oldSixRolesFourExecFullMetadataPreserved':True,'nativeDumpAccepted':False")
    ast.parse(s);return s


PINS=r'''
COMPLETE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1148-native-five-recovery-v2')
fixed={'before.private.json':'85d86f84d2ec7877708f32a0027827a4a2b33d96a717e1cf76fc085cbb3af418',
 'prepared.private.json':'2fee063c194b5ae4ef9e526ba3566d4f567a9526bbfec5cead3c8370a07e7d57',
 'after.private.json':'2fee063c194b5ae4ef9e526ba3566d4f567a9526bbfec5cead3c8370a07e7d57',
 'complete.private':'b1c2f4caace44c011c0a54ccfa80e81adbef205eed2bf1517c21012a044ca714',
 'refs.private.err':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
'''
NATIVE=r'''
 old_native=json.loads((COMPLETE/'before.private.json').read_bytes())['trees']['/run/schubert-nk/pt-coverage'];now=value['native'];common='/run/schubert-nk/pt-coverage'
 names={'root-api193':'root','root-web193':'root','ordinary-api193':'schubert-api','ordinary-web193':'schubert-web','ordinary-inspector196':'schubert-inbox-inspector'}
 identities={n:[int(command(['/usr/bin/id','-u',a])),int(command(['/usr/bin/id','-g',a]))]for n,a in names.items()}
 require(native_policy.coverage_delta(now,old_native,identities))
 require(set(now)==set(old_native)|{common+'/'+n for n in names}and now[common]['metadata'][4]==stat.S_IFDIR|0o755)
 for n,identity in identities.items():
  p=pathlib.Path(common,n);m=md(p);require(m[2:6]==[*identity,stat.S_IFDIR|0o700,2]and not list(p.iterdir())and not os.listxattr(p))
  require(command(['/usr/bin/findmnt','--target',str(p),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1159-native-five-post-v1').replace('PG1120-current-failed-capture-v1','PG1159-native-five-post-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<independent prepared native post>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
