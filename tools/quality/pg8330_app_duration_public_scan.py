"""Public app duration/role correction evidence only; no runtime/private scan or global claim."""
import pg6990_recovery_public_scan as scan
import public_delta_tombstone_contract as tombstone

if __name__ == '__main__':
    scan.BEFORE = '4e7e2197eb8852b5172b652506dc2d1bb91f8681'
    scan.OUT = scan.scan.BASE / 'PG8330-app-duration-public-delta-v1'
    base = 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/monitoring/'
    scan.TOMBSTONES = frozenset({base + 'PrometheusSummaryExporter.java', base + 'package-info.java',
        (base + 'PrometheusSummaryExporterTest.java').replace('/main/', '/test/')})
    tombstone.verify_scope(scan.TOMBSTONES, set(scan.TOMBSTONES))
    rejected = 0
    for declared, observed in ((set(), set(scan.TOMBSTONES)),
        (set(scan.TOMBSTONES), set()), (set(scan.TOMBSTONES), set(scan.TOMBSTONES) | {'src/unknown.java'})):
        try:
            tombstone.verify_scope(declared, observed)
        except ValueError:
            rejected += 1
    for mode, kind, size in (('120000', 'blob', 1), ('040000', 'tree', 1), ('100644', 'blob', 0), ('100644', 'blob', 2097153)):
        try:
            tombstone.verify_blob(mode, kind, size)
        except ValueError:
            rejected += 1
    if rejected != 7:
        raise ValueError('all explicit tombstone negatives must reject')
    scan.main()
