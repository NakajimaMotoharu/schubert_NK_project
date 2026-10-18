"""Original237 plus nine current Morning Backup sites; no prior counter/success carry."""
import json
import os
import pg5261_scope_inventory_continue as carry
import pg5264_morning_backup_selected as entry

SOURCE='4661101cae269ae709343282f029c5894d97fb95'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5264-morning-backup-green-v1-metadata-v2/manifest.json'


def main():
    value,proof=carry.continue_current(root=entry.selected.ROOT,sha=entry.selected.sha,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5262-scope-classification-backup-worker-v2/manifest.json',
        previous_sha='8a799737bb94222cb3a7ae087e7b81a226aa9c3e33ef409cf3db535984e8356c',
        previous_source='33df84270ffec0d6660a6665f68dd2eecb65c5a5',source=SOURCE,qualified_ref=QUALIFIED,
        tests=882,suites=105,new_files={'MorningBackupArtifacts.java','MorningBackupRetention.java','MorningBackupReuse.java'},
        expected_counts={'FIXED_LIMITED':154,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':82})
    value.update(semanticClasses=3,nestedDebugEquivalent=proof['nestedDebugEquivalent'],
        otherPhysicalClassesUnchanged=proof['otherPhysicalClassesUnchanged'],rawDirectoryFactories=9,
        nativeOwnerExecutionQualified=False)
    out=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5270-scope-classification-morning-backup-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':value['classificationCounts'],'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
