"""SSC233 independent current21 readonly post, no startup/stop/write authority."""
from pathlib import Path
import pg685_sources as profile

R = Path(__file__).resolve().parent

LIVE21 = r'''
  require(after['runtime']is None and not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir()))
  require(after['dependencies']=={u:{k:sorted(v.split())for k,v in show(u,{'Requires','Before','After','PartOf','BindsTo'}).items()}for u in UNITS})
  require(after['caddyPre']==show('caddy.service',{'ExecStartPre'})['ExecStartPre'])
  for n in ('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1'):require(tree(base/n)==after['currentBootstrapProofs'][n])
  paths={**{n:pathlib.Path('/run/schubert-nk')/n for n in ('backup-request','cleanup-request','expiry-request')},'runtime-parent':pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')}
  namespace={n:{'metadata':metadata(p),'entries':sorted(c.name for c in p.iterdir()),'xattrs':os.listxattr(p)}for n,p in paths.items()}
  require(namespace==after['namespace'])
  observed=[json.loads(l)for l in command(['/usr/bin/journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=095f6d1d7f8442b7b2b44ae59a4314f5','-o','json','--no-pager']).splitlines()]
  require(observed==after['parentPid1'])
  for unit,value in after['pid1Stop'].items():
   p=base/'pg655-native-stop-v1'/(unit+'.stopped.private');require(metadata(p)==value['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256'])
  require(metadata(approval)==after['approval']['metadata']and hashlib.sha256(approval.read_bytes()).hexdigest()==after['approval']['sha256'])
'''


def source():
    raw = profile.bind((R/'pg625_completed_post.py').read_text())
    for old, new in (
        ('pg625', 'pg687'),
        ("caddyPre'.split()", "caddyPre namespace currentBootstrapProofs'.split()"),
        ("'PG600'if MODE=='verify'else'PG621'", "'PG631'if MODE=='verify'else'PG682'"),
        ("==492", "==514"), ("'batchRows':492", "'batchRows':514"),
        ("'fields':19", "'fields':21"),
        ('pg611-native-stop-v1', 'pg655-native-stop-v1'),
        ("  for name in ('backup-request','cleanup-request','expiry-request'):", LIVE21+"\n  for name in ('backup-request','cleanup-request','expiry-request'):"),
    ):
        assert old in raw, old
        raw = raw.replace(old, new)
    assert "'PG600'" not in raw and 'pg624' not in raw and '==492' not in raw
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R/'pg687_completed_post.py'), '__name__': 'independent_completed21_post'}
    exec(compile(source(), '<independent completed21 readonly post>', 'exec'), env)
    env['main']()
