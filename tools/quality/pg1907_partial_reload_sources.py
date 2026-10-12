"""SSC283 new owner closes only remaining reload; no epoch/current/Unit reexchange."""
from pg1872_warning_ro_marker_sources import sources as base_sources
from pg1900_unit_metadata9_sources import source as unit_source
from pg1844_warning_unit_full_six import CANDIDATE,OLD
from pg1877_warning_publication_sources import once,BOM

TOOLS='pg1907-partial-reload-tools-v1'
SAVE='pg1911-partial-reload-v1'
CLASS='Pg1907PartialReload'
BEFORE='16ec6b95e9de832eec5eaf90849a64e6a54c94600b3b6f3f7a09527b17515ad4'


def bind(raw):
    return raw.replace('pg1872','pg1907').replace('Pg1872','Pg1907').replace('PG1872','PG1907').replace('pg1874-warning-candidate-host-ro-v1',SAVE).replace('pg1907-warning-candidate-ro-tools-v1',TOOLS).replace('CandidateRo','PartialReload')


def sources():
    result={}
    for name,raw in base_sources(BOM,'1928d1bd0d8aa0f00d3b1e4bb120e78c0bc710a9d5a219d89b3853d4929a11d6').items():
        name=bind(name);raw=bind(raw)
        raw=raw.replace('pg1849-warning-completed-current-before-v1','pg1904-partial-recovery-closed-post-v1').replace('1928d1bd0d8aa0f00d3b1e4bb120e78c0bc710a9d5a219d89b3853d4929a11d6',BEFORE)
        raw=raw.replace('PG1638','PG1846').replace('pg1638','pg1846').replace(OLD,CANDIDATE).replace('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',BOM)
        raw=raw.replace('prepare-ro','finish-reload')
        if name==CLASS+'.java':
            raw=once(raw,'epoch.state()==StartupPermitRecords.State.ISSUED','epoch.state()==StartupPermitRecords.State.INVALID')
            raw=once(raw,'require(epoch.equals(files.current()) && done.equals(MaintenanceRunFiles.create().execute(x->x.observeStartup(epoch.activation())).completed().orElseThrow()));','require(Arrays.equals(StartupPermitRecords.epoch(epoch),Files.readAllBytes(Path.of("/var/lib/pgpt-s1-preservation/pg1895-warning-publication-v1/expected-epoch.private"))));\n      require(epoch.equals(files.current()) && done.equals(MaintenanceRunFiles.create().execute(x->x.observeStartup(epoch.activation())).completed().orElseThrow()));')
            raw=once(raw,'\"ro\".equals(name)','\"reload\".equals(name)')
            start=raw.index('  static void candidateReadOnly()');end=raw.index('  public static void main',start);raw=raw[:start]+raw[end:]
            raw=once(raw,'phase=\"CANDIDATE_RO\";candidateReadOnly();refs.check(\"ro\");','phase=\"ONLY_NORMAL_RELOAD\";refs.check(\"reload\");')
            raw=raw.replace('candidateReadOnlyVerified=true','partialExistingUnitVerified=true\\nnormalSingleReload=true').replace('startsStopsReloadsEpochWrites0=true','startsStopsEpochSqlWrites0=true')
        elif name=='Pg1907OriginalTupleTest.java':
            raw=raw.replace('State.ISSUED','State.__OLD__').replace('State.INVALID','State.ISSUED').replace('State.__OLD__','State.INVALID')
        elif name=='pg1907_native_owned_stop.py':raw=raw.replace("'ro'","'reload'")
        elif name=='pg1907_native_refs.py':
            start=raw.index('    candidate_root=');end=raw.index('    held = owner()',start);raw=raw[:start]+raw[end:]
            raw=once(raw,'    first = None','    first = None\n    existing_unit=unit_io.ExistingUnit(SAVE)')
            raw=once(raw,"'SuccessExitStatus': ''","'SuccessExitStatus': '10'if placed else''")
            raw=once(raw,"if action == 'ro':","if action == 'reload':")
            raw=once(raw,'            candidate_ro_post(candidate_before)','            existing_unit.reload()')
            raw=once(raw,'            bus.close()','            existing_unit.close();bus.close()')
            raw='import pg1907_existing_unit as unit_io\n'+raw
        if name.endswith('.py'):compile(raw,'<actual reload-only Python>','exec')
        result[name]=raw
    result['pg1907_existing_unit.py']=unit_source().replace('pg1877-morning-unit.part','pg1907-morning-unit.part')+'\n'+EXISTING
    return result


EXISTING=r'''
class ExistingUnit(UnitExchange):
    def __init__(self,save):
        require(os.geteuid()==0)
        self.directory=os.open(DIRECTORY,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        self.private=os.open('/var/lib/pgpt-s1-preservation/pg1895-warning-publication-v1',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        self.record=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        for fd,mode in [(self.directory,0o755),(self.private,0o700),(self.record,0o700)]:
            s=os.fstat(fd);require(s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==mode)
        require(os.fstat(self.directory).st_dev==os.fstat(self.private).st_dev==os.fstat(self.record).st_dev)
        self.old=os.open(PRIVATE,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.private)
        self.old_attributes=attributes(self.old,OLD_SHA)
        require((self.old_attributes.st_dev,self.old_attributes.st_ino,self.old_attributes.st_size,self.old_attributes.st_mtime_ns)==(64769,3227,1836,1790785949034979724))
        self.names=sorted(os.listdir(self.directory));self.begin_ns=1791846667971598421
        self.exchanged=True;self.reloaded=False;self.verify()
    def exchange(self):
        raise ValueError('Existing Unit must never be exchanged again')
    def reload(self):
        require(self.exchanged and not self.reloaded);self.verify()
        fd=os.open('daemon-reload-reserved.private',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600,dir_fd=self.record)
        try:os.write(fd,b'one normal daemon-reload; no retry\n');os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.record)
        result=subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
        require(result.returncode==0 and result.stdout==result.stderr==b'')
        self.reloaded=True;self.verify()
    def close(self):
        require(self.reloaded);self.verify()
        for fd in [self.old,self.private,self.directory,self.record]:os.close(fd)
'''
