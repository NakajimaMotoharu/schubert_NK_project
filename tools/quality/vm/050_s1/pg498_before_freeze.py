"""BUG807/YKT576: fresh complete terminal/raw guard before fixed candidate freeze."""
import pathlib,sys,json,hashlib,os
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6')
import pg496_timeout_owned as h
h.load_definitions()
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-before/snapshot.private.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='ec24c48c4960466d5e14617c3f5df3dfb6bdd486bfe8866696c382354f6b4728'
before=json.loads(raw)
for ignored in range(2):
 units={u:h.show(u) for u in h.ORDER+h.EXTRA}
 for u,v in units.items():
  assert v['MainPID']==v['ControlPID']=='0' and v['Job']=='';h.kernel_empty(u)
 assert dict(h.snapshot(),units=units,current=str(pathlib.Path('/opt/schubert-nk/current').readlink()))==before
 sql="select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_backup','schubert_inbox_inspector','schubert_web_session');select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"
 assert h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0']
assert pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495').is_dir()
assert not pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-pending-codeonly').exists()
print('PG498_FREEZE_GUARD allOriginalValuesTwice=true all10Terminal=true businessPeer0=true advisory0=true')
