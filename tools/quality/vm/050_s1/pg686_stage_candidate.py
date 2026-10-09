"""SSC233 place signed unused PG682; exact old current and protected state unchanged."""
from pathlib import Path

R = Path(__file__).resolve().parent

PROTECTED = r'''
baseline_path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg684-completed-baseline-v2/before.private.json')
baseline_raw=baseline_path.read_bytes();assert hashlib.sha256(baseline_raw).hexdigest()=='c039e70561fd7e5bab3ecf5ce204462d8415f4022d13793711c338a64d2f663d'
baseline=json.loads(baseline_raw)
def protected():
 value={}
 paths=['/run/schubert-nk/startup','/etc/schubert-nk/credentials','/var/lib/schubert-nk/maintenance','/srv/schubert-nk/backup','/var/lib/pgpt-s1-preservation/pg664-bootstrap-tools-v1','/var/lib/pgpt-s1-preservation/pg664-bootstrap-verify-v1','/var/lib/pgpt-s1-preservation/pg664-bootstrap-existing-v1','/etc/schubert-nk/release-approval/current','/run/systemd/system/schubert-nk-morning-controller.service.d','/run/schubert-nk/backup-request','/run/schubert-nk/cleanup-request','/run/schubert-nk/expiry-request']
 for name in paths:
  p=pathlib.Path(name);items=(p,*sorted(p.rglob('*')))if p.is_dir()else(p,)
  entries={}
  for q in items:
   s=q.lstat();assert not q.is_symlink()and(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode))
   record=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,sorted(os.listxattr(q))]
   if q.is_file():record.append(hashlib.sha256(q.read_bytes()).hexdigest())
   assert q.lstat().st_ino==s.st_ino;entries[str(q)]=record
  value[name]=entries
 value['units']={u:subprocess.check_output(['systemctl','show',u,'--property='+','.join(sorted(baseline['units'][u]))],text=True)for u in units}
 value['configuration']={u:subprocess.check_output(['systemctl','show',u,'--property='+','.join(sorted(baseline['configuration'][u]))],text=True)for u in units}
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in baseline['rows']:
  assert re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',table)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+" t)q;"
 rows={}
 for line in subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;'],text=True).splitlines():
  row=json.loads(line);assert row['table']not in rows;rows[row['table']]=row['rows']
 assert rows==baseline['rows']and len(rows)==24 and len(rows['schubert.batch_runs'])==514
 value['rows']=rows;value['current']=str(current.readlink());terminal();return value
before=protected();assert before==protected()
'''


def source():
    raw = (R/'pg632_stage_candidate.py').read_text()
    for old, new in (
        ('pg632', 'pg686'), ('PG632', 'PG686'), ('pg631', 'pg682'), ('PG631', 'PG682'),
        ('0.1.0-PG621', '0.1.0-PG631'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe', '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e', '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'),
    ):
        assert old in raw, old
        raw = raw.replace(old, new)
    old = 'import datetime,grp,hashlib,json,os,pathlib,stat,subprocess,tarfile'
    assert raw.count(old) == 1
    raw = raw.replace(old, old+',re')
    assert raw.count("terminal()\nroot=") == 1
    raw = raw.replace("terminal()\nroot=", "terminal()\n"+PROTECTED+"\nroot=")
    old = 'terminal();assert current.readlink()==old'
    assert raw.count(old) == 1
    raw = raw.replace(old, old+';assert protected()==before')
    assert 'PG621' not in raw and 'pg632' not in raw
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R/'pg686_stage_candidate.py'), '__name__': 'new_unused_candidate_only'}
    exec(compile(source(), '<fixed PG682 unused candidate stage>', 'exec'), env)
    env['main']()
