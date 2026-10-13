"""Newrun retained Backup content inside current stopped full-post scopes, no Backup replay."""
import ast
from pyflakes.api import check
import pg2068_retained_backup_replay_history_post as old_backup
from pg2096_current_newrun_terminal_post import payload as current_post,entry as post_entry

SLOT='pg2110-current-newrun-backup-content-v1'


def payload(seals):
    raw=current_post(seals).replace('pg2096-current-newrun-terminal-post-v1',SLOT)
    reader=old_backup.payload(seals);tree=ast.parse(reader)
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='qualify_backup')
    fixtures=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIXTURE_SOURCE'for t in n.targets)]
    if len(fixtures)!=1:raise ValueError('one independent config fixture oracle required')
    extra=ast.get_source_segment(reader,fixtures[0])+'\n'+ast.get_source_segment(reader,function)+'\n'
    for old,new in [('4148e3e8-f107-431a-ab27-d6e6d1f1772e','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'),('2026-10-12T18:20:32.598894Z','2026-10-13T03:08:18.452473Z'),('0.1.0-PG1638/config/templates/api.yml','0.1.0-PG1846/config/templates/api.yml')]:
        if old not in extra:raise ValueError('one current newrun Backup archive role required')
        extra=extra.replace(old,new)
    marker='bus = dbus.SystemBus(private=True)'
    point=raw.index('\n'+marker+'\n');raw=raw[:point]+'\n'+extra+raw[point:]
    marker='native = snapshot()'
    if raw.count(marker)!=1:raise ValueError('one current owned metadata scope required')
    raw=raw.replace(marker,marker+'\n    backup_result,listing_bytes = qualify_backup()',1)
    marker="save = base / '"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one current result save required')
    raw=raw.replace(marker,"result.update(independentNewRunBackupSummary=backup_result[0],physicalConfigSummary=backup_result[1],ordinaryPgRestoreListExit=0,dumpListSha256=hashlib.sha256(listing_bytes).hexdigest(),backupReplay0=True,restoreAndPruneAccepted=False)\n"+marker)
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<actual current newrun Backup whole post>'):raise ValueError('all actual Backup exports required')
    compile(raw,'<newrun Backup content>','exec');return raw


def entry():
    fn=post_entry()
    import types
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'newrun_backup_content_entry')


if __name__=='__main__':raise SystemExit(entry()())
