"""Read-only Backup content oracle bound to the actual fresh stopped generation."""
import ast
import types
from pyflakes.api import check
import pg2476_question_current_backup_content as previous
import pg2560_strict_current_owned_post as current

SLOT = 'pg2566-strict-current-backup-content-v1'


def payload(seals):
    raw = current.payload(seals).replace(current.SLOT, SLOT).replace(
        'PG2560-strict-current-owned-post-v1', 'PG2566-strict-current-backup-content-v1')
    old = previous.payload(seals)
    tree = ast.parse(old)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'qualify_backup']
    fixtures = [n for n in tree.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == 'FIXTURE_SOURCE' for t in n.targets)]
    if len(functions) != 1 or len(fixtures) != 1:
        raise ValueError('one independent Backup oracle and literal configuration fixture required')
    extra = '\n'.join(ast.get_source_segment(old, n) for n in fixtures + functions) + '\n'
    for before, after in [
        ('06236d14-a6f8-4d05-a6ff-49c713cc2647', 'b29fb3e5-2c46-4eac-b8f3-d03b986338e3'),
        ('2026-10-13T21:16:10.125382Z', '2026-10-14T00:36:06.976135Z'),
        ('0.1.0-PG2428/config/templates/api.yml', '0.1.0-PG2512/config/templates/api.yml'),
    ]:
        if before not in extra:
            raise ValueError('exact current run/cutoff/configuration oracle role required')
        extra = extra.replace(before, after)
    marker = '\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker) != 1:
        raise ValueError('one independent resource boundary required')
    raw = raw.replace(marker, '\n' + extra + marker, 1)
    marker = 'native = snapshot()'
    if raw.count(marker) != 1:
        raise ValueError('one current stopped snapshot required')
    raw = raw.replace(marker, marker + '\n    backup_result,listing_bytes = qualify_backup()', 1)
    marker = "save = base / '" + SLOT + "'"
    if raw.count(marker) != 1:
        raise ValueError('one new-only read-only receipt required')
    raw = raw.replace(marker,
        "result.update(independentCurrentRunBackupSummary=backup_result[0],physicalConfigSummary=backup_result[1],ordinaryPgRestoreListExit=0,dumpListSha256=hashlib.sha256(listing_bytes).hexdigest(),backupReplay0=True,restorePruneAccepted=False)\n" + marker, 1)
    if check('HASHES={}\nRECEIPT="actual"\n' + raw, '<fresh Backup read-only whole post>'):
        raise ValueError('whole reader namespace required')
    compile(raw, '<fresh stopped generation Backup content>', 'exec')
    return raw


def entry():
    fn = current.entry()
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload},
                              'strict_current_backup_content')


if __name__ == '__main__':
    raise SystemExit(entry()())
