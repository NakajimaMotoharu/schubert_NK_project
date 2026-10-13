"""Independent same-root Backup content after signed owned stop; readonly only."""
import ast
import types
from pyflakes.api import check
import pg2068_retained_backup_replay_history_post as old_backup
import pg2280_current_signed_owned_post as current_post

SLOT='pg2288-current-run-backup-content-v1'


def payload(seals):
    raw=current_post.payload(seals).replace(current_post.SLOT,SLOT).replace('PG2281-current-signed-owned-post-v2','PG2288-current-run-backup-content-v1')
    tree=ast.parse(old_backup.payload(seals))
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='qualify_backup')
    fixtures=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIXTURE_SOURCE'for t in n.targets)]
    if len(fixtures)!=1:raise ValueError('one independent fixture config source required')
    extra=ast.get_source_segment(old_backup.payload(seals),fixtures[0])+'\n'+ast.get_source_segment(old_backup.payload(seals),function)+'\n'
    for old,new in [('4148e3e8-f107-431a-ab27-d6e6d1f1772e','91f5484b-9702-4c7c-97f3-dd5110a853f9'),('2026-10-12T18:20:32.598894Z','2026-10-13T15:01:53.237266Z'),('0.1.0-PG1638/config/templates/api.yml','0.1.0-PG2126/config/templates/api.yml')]:
        if old not in extra:raise ValueError('one exact approved currentrun Backup role required')
        extra=extra.replace(old,new)
    marker='bus = dbus.SystemBus(private=True)'
    point=raw.index('\n'+marker+'\n');raw=raw[:point]+'\n'+extra+raw[point:]
    marker='native = snapshot()'
    if raw.count(marker)!=1:raise ValueError('one full current stopped metadata scope required')
    raw=raw.replace(marker,marker+'\n    backup_result,listing_bytes = qualify_backup()',1)
    marker="save = base / '"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one current result save required')
    raw=raw.replace(marker,"result.update(independentCurrentRunBackupSummary=backup_result[0],physicalConfigSummary=backup_result[1],ordinaryPgRestoreListExit=0,dumpListSha256=hashlib.sha256(listing_bytes).hexdigest(),backupReplay0=True,restorePruneIntentAccepted=False)\n"+marker)
    if check('HASHES={}\nRECEIPT="actual"\n'+raw,'<whole current Backup readonly>'):raise ValueError('whole reader exports required')
    compile(raw,'<currentrun Backup readonly>','exec');return raw


def entry():
    fn=current_post.entry()
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'current_run_backup_content_entry')


if __name__=='__main__':raise SystemExit(entry()())
