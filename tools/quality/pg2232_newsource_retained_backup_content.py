"""Independent actual newsource Backup content under fresh cold whole-post refs.

PT-OPS-2232-001. No Backup replay, restore, prune, epoch or business write.
"""
import ast
import inspect
from pyflakes.api import check
import pg2068_retained_backup_replay_history_post as old
import pg1453_current_cold_post as transport
from pg2040_fresh_normal_warning_terminal_post import SEALS
from pg2218_current_newboot_cold_post import payload as cold_post

SLOT='pg2232-newsource-retained-backup-content-v1'


def payload():
    reader=old.payload({n:'a'*64 for n in SEALS});t=ast.parse(reader)
    f=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='qualify_backup')
    fixtures=[n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(q,ast.Name)and q.id=='FIXTURE_SOURCE'for q in n.targets)]
    if len(fixtures)!=1:raise ValueError('one independently approved fixture config source required')
    extra=ast.get_source_segment(reader,fixtures[0])+'\n'+ast.get_source_segment(reader,f)+'\n'
    for a,b in [('4148e3e8-f107-431a-ab27-d6e6d1f1772e','02bddddf-9cd3-4668-9d67-7561232fc4e4'),
      ('2026-10-12T18:20:32.598894Z','2026-10-13T06:29:34.698736Z'),
      ('0.1.0-PG1638/config/templates/api.yml','0.1.0-PG2126/config/templates/api.yml')]:
        if a not in extra:raise ValueError('exact newsource retained Backup binding required '+a)
        extra=extra.replace(a,b)
    extra+='\ndef metadata9(s):\n return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]\n'
    raw=cold_post().replace('pg2218-current-newboot-cold-independent-post-v1',SLOT).replace('PG2218-current-newboot-cold-independent-post-v1','PG2232-newsource-retained-backup-content-v1')
    marker='bus=dbus.SystemBus(private=True);manager='
    index=raw.index(marker);raw=raw[:index]+extra+raw[index:]
    marker=" first=snapshot();require(first==before['current'] and first==snapshot());runtime=runtime_check();require(runtime==runtime_check())"
    if raw.count(marker)!=1:raise ValueError('one whole current owned metadata scope required')
    extra="\n after={'backup':first['durable']['backup'],'rows':first['rows']}\n data=json.loads(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126/RELEASE-MANIFEST.json').read_bytes())\n backup_result,listing=qualify_backup()\n require(first==snapshot())"
    raw=raw.replace(marker,marker+extra)
    marker="with(SAVE/'result.safe.json').open('x')"
    raw=raw.replace(marker,"result.update(independentBackupSummary=backup_result[0],physicalConfigSummary=backup_result[1],ordinaryPgRestoreListExit=0,dumpListSha256=hashlib.sha256(listing).hexdigest(),backupReplay0=True,restorePruneIntentAccepted=False)\n"+marker)
    if check(raw,'<actual newsource retained Backup content>'):raise ValueError('whole actual exports required')
    compile(raw,'<newsource Backup independent content post>','exec');return raw


def main():
    raw=inspect.getsource(transport.main).replace('pg1452-current-cold-owned-prepare-v1','pg2212-current-newboot-cold-owned-prepare-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**transport.__dict__,'payload':payload}
    exec(compile(raw,'<fresh retained Backup content transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
