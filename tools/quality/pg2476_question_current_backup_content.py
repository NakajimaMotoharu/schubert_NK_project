"""Independent current new-run Backup payload/config/list checks, no replay or restore."""
import ast
import types
from pyflakes.api import check
import pg2288_current_run_backup_content as backup
import pg2464_question_current_owned_post as current

SLOT='pg2476-question-current-backup-content-v1'


def payload(seals):
    raw=current.payload(seals).replace(current.SLOT,SLOT).replace('PG2464-question-current-owned-post-v1','PG2476-question-current-backup-content-v1')
    old=backup.payload(seals);tree=ast.parse(old)
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='qualify_backup']
    fixtures=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIXTURE_SOURCE'for t in n.targets)]
    if len(functions)!=1 or len(fixtures)!=1:raise ValueError('one independent canonical Backup oracle required')
    extra='\n'.join(ast.get_source_segment(old,n)for n in fixtures+functions)+'\n'
    for a,b in [('91f5484b-9702-4c7c-97f3-dd5110a853f9','06236d14-a6f8-4d05-a6ff-49c713cc2647'),
                ('2026-10-13T15:01:53.237266Z','2026-10-13T21:16:10.125382Z'),
                ('0.1.0-PG2126/config/templates/api.yml','0.1.0-PG2428/config/templates/api.yml')]:
        if a not in extra:raise ValueError('one current run/cutoff/config role required')
        extra=extra.replace(a,b)
    marker='\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker)!=1:raise ValueError('one current independent resource boundary required')
    raw=raw.replace(marker,'\n'+extra+marker,1)
    marker='native = snapshot()'
    if raw.count(marker)!=1:raise ValueError('one current stopped snapshot required')
    raw=raw.replace(marker,marker+'\n    backup_result,listing_bytes = qualify_backup()',1)
    marker="save = base / '"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one new-only current backup read required')
    raw=raw.replace(marker,"result.update(independentCurrentRunBackupSummary=backup_result[0],physicalConfigSummary=backup_result[1],ordinaryPgRestoreListExit=0,dumpListSha256=hashlib.sha256(listing_bytes).hexdigest(),backupReplay0=True,restorePruneAccepted=False)\n"+marker)
    if check('HASHES={}\nRECEIPT="actual"\n'+raw,'<current new source Backup all post>'):raise ValueError('whole backup reader globals required')
    compile(raw,'<current new source Backup content>','exec');return raw


def entry():
    fn=current.entry()
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'question_current_backup_content')


if __name__=='__main__':raise SystemExit(entry()())
