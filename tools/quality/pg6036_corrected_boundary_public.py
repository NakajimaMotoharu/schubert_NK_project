"""Independent new-source965 qualification; never upgrade old b2 failed static gate."""
import inspect
import pg6030_error_boundary_public as previous
from pg6034_corrected_boundary_static import SOURCE


def reader_source():
    raw = inspect.getsource(previous.main)
    changes = {
        'pg6026-error-boundary-selected965-v1': 'pg6032-error-boundary-selected965-v1',
        'PG6028-error-boundary-static-v2': 'PG6034-corrected-boundary-static-v1',
        'pg6028-error-boundary-static-v2': 'pg6034-corrected-boundary-static-v1',
        "sha(op) == '9ecd53b6a1aa5380db0c8420f38323e9d2282871d68f146e636a9d03e088ab6f'": "sha(op) == s['selectedManifestSha256']",
        "v['actualExit'] == v['mavenActualExit'] == 1 and v['phaseExits'] == [0, 1] and v['sourceFixed'] and not v['selectedQualified']": "v['actualExit'] == v['mavenActualExit'] == 0 and v['phaseExits'] == [0, 0] and v['sourceFixed'] and v['selectedQualified']",
        "v['staticIssues'] == dict(protocol=0, storage=0, bootstrap=0, api=0, web=0, batch=3)": "v['staticIssues'] == dict(protocol=0, storage=0, bootstrap=0, api=0, web=0, batch=0)",
        "s['originalSelectedOverallExit'] == 1 and not s['originalSelectedOverallAccepted']": "s['originalSelectedOverallExit'] == 0 and s['originalSelectedOverallAccepted']",
        "s['rawDiagnosticsRemovedByPg'] == 21 and s['pmdRawFindings'] == 1327": "s['rawDiagnosticsRemovedByPg'] == 19 and s['pmdRawFindings'] == 1329",
        "BASE/'PG6030-error-boundary965-v1'": "BASE/'PG6036-corrected-boundary965-v1'",
        "'PT-PG6026-'": "'PT-PG6032-'",
        'pmdRawFindings=1327, rawDiagnosticsRemovedByPg=21': 'pmdRawFindings=1329, rawDiagnosticsRemovedByPg=19',
        'originalSelectedOverallExit=1, originalSelectedOverallAccepted=False': 'originalSelectedOverallExit=0, originalSelectedOverallAccepted=True',
        "unresolvedBug='BUG1526'": "resolvedGateBug='BUG1526'"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one separate corrected actual XML/source binding: '+old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<corrected965 actual qualification>', 'exec')
    return raw


def main():
    scope = {**vars(previous), 'SOURCE': SOURCE}
    exec(compile(reader_source(), '<corrected original965 XML only>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
