"""BUG1345 new-only entry; unchanged observer and production, complete existing epoch oracle."""
import inspect
import pg4222_fresh_current_noargs_once as previous
import pg4138_independent_revoked_epoch as epoch
from pg4060_original_profile_dual_stack import once

SLOT='pg4234-canonical-fresh-noargs-once-v1'


def payload(hashes):
    raw=previous.payload(hashes).replace(previous.SLOT,SLOT)
    oracle=inspect.getsource(epoch).replace('from pg4086_failed_done_recovery_contract import invalid_epoch,require','from recovery_plan import invalid_epoch,require')
    raw='EPOCH_SOURCE='+repr(oracle)+'\n'+raw
    old="epoch=Path('/run/schubert-nk/startup/epoch.current').read_bytes();require(epoch.startswith(b'state=INVALID\\n'))"
    block=r'''epoch_path=Path('/run/schubert-nk/startup/epoch.current');epoch=epoch_path.read_bytes()
sys.path.insert(0,str(frozen));epoch_contract={};exec(EPOCH_SOURCE,epoch_contract)
# Validate complete canonical record/cohort BEFORE using its UUID as a filename.
validated=epoch_contract['former_issued'](epoch,'0'*64)
epoch_id=validated.decode('ascii').split('\n')[3].split('=',1)[1]
permit=epoch_path.parent/(epoch_id+'.permit');require(str(permit)in before_current['startup'])
expected_permit=before_current['startup'][str(permit)];require(metadata(permit)==expected_permit['metadata'])
fd=os.open(permit,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 s=os.fstat(fd);require([s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]==expected_permit['metadata']and 0<s.st_size<=8192)
 permit_raw=os.pread(fd,s.st_size+1,0);require(len(permit_raw)==s.st_size and hashlib.sha256(permit_raw).hexdigest()==expected_permit['sha256']and metadata(permit)==expected_permit['metadata'])
finally:os.close(fd)
epoch_contract['former_issued'](epoch,expected_permit['sha256'])
require(hashlib.sha256(epoch).hexdigest()==before_current['startup'][str(epoch_path)]['sha256']and epoch_path.read_bytes()==epoch)'''
    # The original statement is inside the retained metadata scope.
    return once(raw,old,block.replace('\n','\n '))


def main():
    ns={**vars(previous),'SLOT':SLOT,'payload':payload}
    raw=inspect.getsource(previous.main).replace('pg4230-final-fresh-observer-qualification-v1','pg4236-canonical-fresh-qualification-v1')
    exec(compile(raw,'<same qualified host guard/new canonical full entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
