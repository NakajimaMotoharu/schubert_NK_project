"""Original237 plus ten current Backup sites, no previous success/counter transplantation."""
import json
import os
import pg5261_scope_inventory_continue as carry
import pg5256_backup_worker_selected as entry

SOURCE='33df84270ffec0d6660a6665f68dd2eecb65c5a5'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5256-backup-worker-green-v1-metadata-v2/manifest.json'


def main():
    value,proof=carry.continue_current(root=entry.selected.ROOT,sha=entry.selected.sha,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5254-scope-classification-startup-view-v1/manifest.json',
        previous_sha='b237cf2d0d583d1fd4f2fa5daa3318ff8ad24b47dca38a925d92d175b45a70c0',
        previous_source='86968fd6f6edb54511a1db02959f5bfe3c3b92fb',source=SOURCE,qualified_ref=QUALIFIED,
        tests=864,suites=101,new_files={'BackupDatabaseWorker.java','BackupDatabaseCopy.java','BackupBundlePublisher.java'},
        expected_counts={'FIXED_LIMITED':145,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':91})
    value.update(semanticClasses=3,nestedDebugEquivalent=proof['nestedDebugEquivalent'],
        otherPhysicalClassesUnchanged=proof['otherPhysicalClassesUnchanged'],checkedNullIoFactories=3,directPortFactories=4)
    value.update(metadataCorrection='BUG1435: fixed legacy count text only; original v1 retained',
        originalV1Sha256='7ef88a64b788a4a50af70f52fbbe313cbfc982ce65681c28aa22ad8c6514dfee')
    out=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5262-scope-classification-backup-worker-v2'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':value['classificationCounts'],'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
