"""Original237 partition after twelve current Directory owners; formal leaf credit zero."""
import json
import os
import pg5261_scope_inventory_continue as carry
import pg5272_cleanup_factory_selected as entry

SOURCE='3551be4f84f14c07c63425a807690478067532c1'
NEW_FILES={name+'.java' for name in entry.OUTERS}
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5272-cleanup-factory-green-v1-metadata-v2/manifest.json'


def main():
    value,proof=carry.continue_current(root=entry.selected.ROOT,sha=entry.selected.sha,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5270-scope-classification-morning-backup-v1/manifest.json',
        previous_sha='139906babcb2badaf671eb867aeedcecc8516f3dc47c1399e67a17047d374264',
        previous_source='4661101cae269ae709343282f029c5894d97fb95',source=SOURCE,qualified_ref=QUALIFIED,
        tests=907,suites=111,new_files=NEW_FILES,
        expected_counts={'FIXED_LIMITED':166,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':70})
    value.update(semanticClasses=6,nestedDebugEquivalent=proof['nestedDebugEquivalent'],
        otherPhysicalClassesUnchanged=proof['otherPhysicalClassesUnchanged'],rawDirectoryFactories=12,
        nativeOwnerExecutionQualified=False)
    out=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5278-scope-classification-cleanup-factory-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':value['classificationCounts'],'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
