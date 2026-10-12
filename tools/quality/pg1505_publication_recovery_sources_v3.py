"""BUG1115: current fixed perfdata mmap and journal FD kernel join, no M/A relaxation."""
from pathlib import Path
from pg1489_publication_recovery_sources import java as old_java,refs as old_refs

def remap(raw):
    return raw.replace('Pg1489PublicationOnlyRecovery','Pg1505PublicationOnlyRecovery').replace('pg1489-publication-only-tools-v1','pg1505-publication-only-tools-v3').replace('pg1489_publication_recovery_refs.py','pg1505_publication_recovery_refs.py').replace('pg1492-publication-only-recovery-v1','pg1507-publication-only-recovery-v3').replace('PG1492_','PG1507_')

def java():return remap(old_java())

def refs():
    raw=remap(old_refs());begin=raw.index('   found=[]');end=raw.index('   if BROKER_LOCKS is None:',begin)
    raw=raw[:begin]+NEW_PROOF+raw[end:]
    marker="STOPPED=[];STOP_RECEIPTS={};RETIRED=False;BROKER_LOCKS=None"
    assert raw.count(marker)==1
    source=Path(__file__).with_name('pg1504_broker_lock_mapping.py').read_text()
    raw=raw.replace(marker,'KERNEL_SOURCE='+repr(source)+"\nkernel_contract=types.ModuleType('fixed_broker_kernel');exec(KERNEL_SOURCE,kernel_contract.__dict__)\n"+marker)
    compile(raw,'<corrected typed broker mapping source>','exec');return raw

NEW_PROOF=r'''
   fd_keys=[]
   for fd in(p/'fd').iterdir():
    try:st=fd.stat()
    except FileNotFoundError:continue
    fd_keys.append((os.major(st.st_dev),os.minor(st.st_dev),st.st_ino))
   lines=pathlib.Path('/proc/locks').read_text().splitlines();maps=(p/'maps').read_text().splitlines()
   found=kernel_contract.validate(lines,41805,fd_keys,maps)
   key=next(key for kind,key in found if kind=='FLOCK')
   mapping=kernel_contract.fixed_mapping(maps,41805,key)
   # Fixed proc magic-root anchor belongs to the exact authenticated Broker generation.
   perf=pathlib.Path('/proc/41805/root')/mapping['path'].lstrip('/')
   fd=os.open(perf,os.O_RDONLY|os.O_NOFOLLOW)
   try:
    st=os.fstat(fd);require(stat.S_ISREG(st.st_mode)and(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)==key and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink,st.st_size)==(994,979,0o600,1,32768))
   finally:os.close(fd)
'''
