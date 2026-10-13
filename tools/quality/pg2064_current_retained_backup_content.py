"""Current-source retained Backup bytes/SQL/profile/config/list oracle, never replay Backup."""
import ast
import json
import subprocess
from pg1446_current_cold_stage import W
from pg1847_warning_backup_readonly import payload as archived_reader
from pg2062_native_augmented_retirement_post import payload as current_post
from pg2040_fresh_normal_warning_terminal_post import SEALS
import pg2060_fresh_runtime_retirement_independent_post as transport
from pyflakes.api import check

SLOT='pg2064-current-retained-backup-content-v1'


def payload(seals):
    raw=current_post(seals).replace('pg2062-native-augmented-runtime-retirement-post-v1',SLOT)
    reader=archived_reader();tree=ast.parse(reader)
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='qualify_backup')
    fixtures=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FIXTURE_SOURCE'for t in n.targets)]
    if len(fixtures)!=1:raise ValueError('one independent retained fixture oracle required')
    extra=ast.get_source_segment(reader,fixtures[0])+'\n'+ast.get_source_segment(reader,function)+'\n'
    # Historical archive references the retained PG1638 template. Do not bind it
    # to a newer template solely because the running source is PG1846.
    marker='bus = dbus.SystemBus(private=True)'
    point=raw.index('\n'+marker+'\n',raw.index('prior_raw='))
    raw=raw[:point]+'\n'+extra+raw[point:]
    marker='native = snapshot()'
    if raw.count(marker)!=1:raise ValueError('one owned current full snapshot scope required')
    raw=raw.replace(marker,marker+'\n    backup_result,listing_bytes = qualify_backup()',1)
    marker="save = base / '"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one current public result save required')
    raw=raw.replace(marker,"result.update(independentRetainedBackupSummary=backup_result[0],physicalConfigSummary=backup_result[1],ordinaryPgRestoreListExit=0,dumpListSha256=hashlib.sha256(listing_bytes).hexdigest(),backupReplay0=True,restoreAndPruneAccepted=False)\n"+marker)
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<whole current retained Backup content>'):raise ValueError('actual complete Backup oracle globals required')
    compile(raw,'<current retained Backup content>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean current retained Backup operator required')
    post=json.loads((W/'pg2062-native-augmented-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or not post['exactRuntimeEntryRetired']:raise ValueError('actual current post required')
    original=transport.payload
    transport.payload=payload;transport.SLOT=SLOT
    try:return transport.main()
    finally:transport.payload=original


if __name__=='__main__':raise SystemExit(main())
