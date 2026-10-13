"""Readonly current Backup/original qualification after genuine finite retirement.

PT-OPS-PG2400-001: SS343/353/354; no replay, restore or pruning.
"""
import ast
import types
from pyflakes.api import check
import pg2288_current_run_backup_content as backup
import pg2398_current_runtime_retirement_post as retired

SLOT = 'pg2400-retired-current-backup-content-v1'


def payload(seals):
    raw = retired.payload(seals).replace(retired.SLOT, SLOT).replace(
        'PG2398-current-runtime-retirement-post-v1', 'PG2400-retired-current-backup-content-v1')
    old = backup.payload(seals)
    tree = ast.parse(old)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'qualify_backup']
    fixtures = [n for n in tree.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == 'FIXTURE_SOURCE' for t in n.targets)]
    if len(functions) != 1 or len(fixtures) != 1:
        raise ValueError('one independent current Backup oracle required')
    extra = '\n'.join(ast.get_source_segment(old, n) for n in fixtures + functions)
    marker = 'bus = dbus.SystemBus(private=True)'
    if raw.count('\n' + marker + '\n') != 1:
        raise ValueError('one current retired resource boundary required')
    raw = raw.replace('\n' + marker + '\n', '\n' + extra + '\n' + marker + '\n', 1)
    marker = 'native = snapshot()'
    if raw.count(marker) != 1:
        raise ValueError('one current stopped snapshot required')
    raw = raw.replace(marker, marker + '\n    backup_result,listing_bytes = qualify_backup()', 1)
    marker = "save = base / '" + SLOT + "'"
    if raw.count(marker) != 1:
        raise ValueError('one new-only readonly result required')
    raw = raw.replace(marker,
        "result.update(independentCurrentRunBackupSummary=backup_result[0],physicalConfigSummary=backup_result[1],ordinaryPgRestoreListExit=0,dumpListSha256=hashlib.sha256(listing_bytes).hexdigest(),backupReplay0=True,restorePruneAccepted=False)\n" + marker)
    if check('HASHES={}\nRECEIPT="actual"\n' + raw, '<retired current Backup full observer>'):
        raise ValueError('all independent observer globals required')
    compile(raw, '<retired current Backup observer>', 'exec')
    return raw


def entry():
    # Keep the actual retirement/ABI guards and management gate unchanged.
    function = retired.main
    return types.FunctionType(function.__code__,
        {**function.__globals__, 'SLOT': SLOT, 'payload': payload}, 'retired_current_backup_entry')


if __name__ == '__main__':
    raise SystemExit(entry()())
