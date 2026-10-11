"""Fresh current fullpost + independent Bootstrap baseline; no startup or SQL writes."""
import ast
import inspect
import pg1340_published_stop_independent_post_v4 as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    code = previous.payload(seals)
    dependency = (previous.previous.transport.previous.R / 'pg529_dependency_graph.py').read_text()
    code = code.replace('bus=dbus.SystemBus(private=True);', dependency + '\nbus=dbus.SystemBus(private=True);')
    marker = ' native=snapshot();require(native==snapshot())'
    if code.count(marker) != 1:
        raise ValueError('one real fullpost snapshot required')
    code = code.replace(marker, marker + '''
 raw_dependencies={u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in UNITS}
 dependencies=dependency_graph(raw_dependencies,UNITS)
 roots={name:pathlib.Path('/run/schubert-nk')/name for name in ('backup-request','cleanup-request','expiry-request')};roots['runtime-parent']=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
 namespace={name:{'metadata':metadata(p),'entries':sorted(q.name for q in p.iterdir()),'xattrs':os.listxattr(p)}for name,p in roots.items()}
 value={**after,'dependencies':dependencies,'namespace':namespace,'credentials':tree(pathlib.Path('/etc/schubert-nk/credentials')),'parentPid1':receipt_rows,'native':native,'oldProofs':tree(root),'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','manifestSha256':'ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99'}
 require(len(value['rows']['schubert.app_users'])==1 and value['rows']['schubert.app_users'][0]['role']=='ADMIN')
 require(all(not roots[n].is_symlink()and not namespace[n]['entries']and not namespace[n]['xattrs']for n in roots))
 require(not any(os.path.lexists('/etc/schubert-nk/credentials/'+n)for n in ('bootstrap-admin-username','bootstrap-admin-password')))
 require(value['credentials']==tree(pathlib.Path('/etc/schubert-nk/credentials'))and raw_dependencies=={u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in UNITS})
''')
    code = code.replace('pg1340-published-terminal-post-v4', 'pg1344-current-bootstrap-before-v1')
    code = code.replace('PG1340-published-terminal-post-v4', 'PG1344-current-bootstrap-before-v1')
    marker = "with(save/'result.safe.json').open('x')as f:"
    if code.count(marker) != 1:
        raise ValueError('one private baseline save required')
    code = code.replace(marker, '''snapshot_raw=json.dumps(value,sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(snapshot_raw);f.flush();os.fsync(f.fileno())
result['beforeSha256']=hashlib.sha256(snapshot_raw).hexdigest()
result['batchRows']=len(value['rows']['schubert.batch_runs'])
''' + marker)
    ast.parse(code)
    return code

def source():
    return previous.source().replace('pg1340-published-terminal-post-v4', 'pg1344-current-bootstrap-before-v1')

def main():
    env = dict(previous.previous.transport.__dict__, SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<current Bootstrap host transport>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
