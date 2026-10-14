"""QA052 approved online active-child48→56 grow; same boot/QEMU, old backing read-only."""
import inspect
import pg2012_online_capacity_grow as prior
from pg2814_network_newboot_readonly import one

SLOT='pg2868-network-online-capacity-grow-v1'
NEW_SIZE=60129542144
DISK='/home/mini/schubert-nk-pgpt/vm/pg2810-network-resume-cold-v1/active.qcow2'
BOOT='79a3260a-e16d-42bf-942a-b914ed144c28'


def lan_payload():
    raw=prior.LAN
    for a,b in [('51539607552','60129542144'),('42949672960','51539607552'),
        ('/home/mini/schubert-nk-pgpt/vm/pg1435-cold-v1/active.qcow2',DISK),
        ('/home/mini/schubert-nk-pgpt/vm/pg1431/guest.qcow2','/home/mini/schubert-nk-pgpt/vm/pg2200-outage-cold-v1/active.qcow2'),
        ('/proc/13204','/proc/4599'),('(13204,0,0)','(4599,0,0)'),("'pid':13204","'pid':4599"),
        ('PG2012-grow-v1','PG2868-grow-v1')]:raw=raw.replace(a,b)
    extra="""assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='c7964823-c628-4ef2-99b5-07b0f0b62bba'
assert tick==101242 and hashlib.sha256(argv).hexdigest()=='f765c39c924d24fc03739355785e22c06b302d68418a85860e3d661960a2b106'
backing_paths=[pathlib.Path(p)for p in ['/home/mini/schubert-nk-pgpt/vm/pg2200-outage-cold-v1/active.qcow2',
 '/home/mini/schubert-nk-pgpt/vm/pg1435-cold-v1/active.qcow2','/home/mini/schubert-nk-pgpt/vm/pg1431/guest.qcow2']]
def metadata(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
backing_metadata={str(p):metadata(p)for p in backing_paths}
for p in backing_paths:
 matches=[fd for fd in(proc/'fd').iterdir()if str(fd.readlink())==str(p)]
 assert len(matches)==1
 flags=next(line.split()[1]for line in(proc/'fdinfo'/matches[0].name).read_text().splitlines()if line.startswith('flags:'))
 assert int(flags,8)&os.O_ACCMODE==os.O_RDONLY
"""
    raw=one(raw,"root=pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2868-grow-v1')",extra+"root=pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2868-grow-v1')")
    raw=one(raw,"persist('after.private.json',{'blocks':after,'samePidTicksInode':True});f.close();s.close()",
        "assert backing_metadata=={str(p):metadata(p)for p in backing_paths}\npersist('after.private.json',{'blocks':after,'samePidTicksInode':True,'oldThreeBackingMetadataUnchanged':True,'backingMetadata':backing_metadata});f.close();s.close()")
    compile(raw,'<same owned QEMU only activechild grow>','exec');return raw


def guest_payload():
    raw=prior.GUEST
    for a,b in [('51539607552','60129542144'),('42949672960','51539607552'),('81561567','98338783'),
        ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),('PG1846','PG2802'),('pg2012-online-grow-v1','pg2868-network-online-grow-v1')]:raw=raw.replace(a,b)
    marker=" persist('partition-before.private.json',before)"
    extra=""" saved=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2866-network-capacity-before-v1/partition-before.private.json').read_bytes()
 import hashlib
 assert hashlib.sha256(saved).hexdigest()=='716c660caeee0696485fb1b505bdb7f516720eac9bb12e2d848fc0a45da4df05'and before==json.loads(saved)
 failed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2864-network-newcurrent-noargs-once-v1')
 assert not os.path.lexists(failed/'external-start-guard.private.json')and not os.path.lexists(failed/'external-start-issued.private.json')
"""
    raw=one(raw,marker,extra+marker)
    compile(raw,'<fresh owned locks quiescent one partition FS grow>','exec');return raw


def main():
    raw=inspect.getsource(prior.main)
    raw=one(raw,"W/'pg2006-existing-runtime-independent-post-v1/manifest.safe.json'","W/'pg2866-network-capacity-before-v1/manifest.safe.json'")
    raw=one(raw,"prior['actualExit']!=0 or prior['allClientAdvisoryFlock0']is not True",
        "prior['actualExit']!=0 or prior['guest']['parentBackendAdvisoryFlocksGone']is not True or prior['guest']['oldOrdinaryGuardStartAbsent']is not True")
    ns={**prior.__dict__,'SLOT':SLOT,'LAN':lan_payload(),'GUEST':guest_payload(),'NEW_SIZE':NEW_SIZE}
    exec(compile(raw,'<once current48to56 online grow dispatcher>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
