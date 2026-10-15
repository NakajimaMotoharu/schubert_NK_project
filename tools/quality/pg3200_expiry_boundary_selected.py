"""Two finite public Expiry DB suites; exact qualified3691 Main, never guest DB.

PT-OPS-CDB3200001/EXP3202001..002, SS331/341/343/451. New Test/helper bytes are
compiled in an isolated directory; original whole fixtures and all Main immutable.
"""
import inspect
import sys
import pg3044_expiry_boundary_selected as base

ROOT = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
FILES = [ROOT + n for n in ['repository/CleanupDatabaseSessionTest.java', 'repository/ExpiryAuditRepositoryTest.java', 'platform/RootReleaseAdmissionTest.java']]
FILES += ['tools/quality/vm/050_s1/SelectedClassContractLauncher.java', 'tools/quality/vm/050_s1/NativeCoverageXml471.java']
CHOICES = {
    'cleanup': ('PG3200', 'pg3200-expiry-connection-selected-v1', 'CleanupDatabaseSessionTest', 'CleanupDatabaseSession', ['cdb3200001ExpiryFactoryRetainsRoleFreshSchemaAndClosesEveryOwner']),
    'audit': ('PG3202', 'pg3202-expiry-audit-selected-v1', 'ExpiryAuditRepositoryTest', 'ExpiryAuditRepository', ['exp3202001EmptyAndSameRunSuccessUseLiteralAuditWithoutMutation', 'exp3202002SuccessRefusesForeignDayFutureEndNullAndSqlBeforeAnyRewrite']),
}


def server(choice):
    label, _, test, subject, methods = CHOICES[choice]
    raw = base.server().replace('PG3044', label).replace('source-full-PG3026', 'source-full-PG3054')
    raw = raw.replace('platform.ExpiryWorkerRequestTest', 'repository.' + test)
    start = raw.index("{'ereq3042001")
    end = raw.index('}.issubset(names)', start)
    raw = raw[:start] + '{' + ','.join(repr(name) for name in sorted(methods)) + '}' + raw[end+1:]
    raw = raw.replace('dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest$Expiry$PriorExpiry', 'dev/codex/schubert/nk/batch/repository/' + subject)
    from pyflakes.api import check
    if check('INPUT={}\n' + raw, '<complete public Expiry selected ' + choice + '>'):
        raise ValueError('complete selected namespace required')
    compile(raw, '<independent public Expiry DB oracle>', 'exec')
    return raw


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in CHOICES:
        raise ValueError('exact cleanup/audit suite required')
    choice = sys.argv[1]
    label, slot, test, _, _ = CHOICES[choice]
    raw = inspect.getsource(base.main)
    for old, new in [('pg3044-expiry-boundary-selected-v1', slot), ('PG3044-candidate-v1', label + '-candidate-v1'),
                     ('pg3028-extra-row-full-qualified-v1', 'pg3056-boundary-group-full-qualified-v1'),
                     ('3685', '3691'), ('pg3030-current-resume-native-qualified-v1', 'pg3188-browser-native-qualified-v1')]:
        raw = raw.replace(old, new)
    ns = {**base.__dict__, 'FILES': FILES, 'TEST': ROOT + 'repository/' + test + '.java', 'server': lambda: server(choice)}
    exec(compile(raw, '<isolated two-suite Test byte transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
