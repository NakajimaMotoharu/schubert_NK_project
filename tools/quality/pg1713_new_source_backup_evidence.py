"""Emit680 safe hashes/counts only, never raw Backup/credential/dump/manifest."""
import hashlib
import json
import os
from pathlib import Path
from pg1446_current_cold_stage import W
from pg1700_new_source_live_binding import SOURCE


def main():
    records={};hashes={}
    for name,relative in [('backup','pg1711-new-source-backup-readonly-v1/manifest.safe.json'),
                          ('retention','pg1712-new-source-retired-backup-v1/manifest.safe.json'),
                          ('post','pg1707-new-source-terminal-post-v1.safe.json')]:
        raw=(W/relative).read_bytes();value=json.loads(raw)
        if type(value.get('actualExit'))is not int or value['actualExit']!=0:raise ValueError('actual0 evidence required')
        records[name]=value;hashes[name]={'path':relative,'sha256':hashlib.sha256(raw).hexdigest()}
    b,r,p=(records[k]for k in ['backup','retention','post'])
    if b.get('productionSource')!=SOURCE or p.get('productionSource')!=SOURCE or r.get('vmDbCurrentBackupModified0')is not True:
        raise ValueError('same current proof and no mutation required')
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/output/680_manifest.json'
    value={'program':'NK-OPS-001','testIds':['PT-OPS-BACKUP-1711-001','PT-OPS-RETENTION-1712-001'],'productionSource':SOURCE,
           'records':hashes,'backupSummary':b['independentBackupManifest'],'physicalConfigSummary':b['physicalConfigSummary'],
           'pgRestoreListExit':b['ordinaryPgRestoreListExit'],'dumpListSha256':b['dumpListSha256'],
           'same24Full32Signed187OriginalNativeResourcesPreserved':b['same24Full32Signed187OriginalNativeResourcesPreserved'],
           'preservedFiles':r['preservedFiles'],'preservedBytes':r['preservedBytes'],'privateManifestSha256':r['privateManifestSha256'],
           'exactOldInodeAndBytesMatched':r['exactOldInodeAndBytesMatched'],'certifiedReadonlyBaseUnchanged':r['certifiedReadonlyBaseUnchanged'],
           'retainedSevenAndOldestRetiredVerified':r['retainedSevenAndOldestRetiredVerified'],'rawBackupOnlyPrivate':r['rawBackupOnlyPrivate'],
           'newBackupRetireRestoreVmStartActiveDiskCopyIssued':False,'formalAccepted':False,'wholeLeafAcceptedDelta':0,
           'classification':'LIMITED_SAME_SOURCE_BACKUP_BYTES_RETENTION_NOT_FULL_MATRIX','actualAllocatedPp':None}
    os.umask(0o077)
    with out.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps({'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
