"""Independent literal vectors/real FD/all IO faults; synthetic Root, no VM actions."""
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
import pg1160_runtime_writer as writer


class WriterTest(unittest.TestCase):
    def test_base_native_literal_and_negative(self):
        base=b'[Service]\nExecStart=/usr/bin/java -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
        agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain'
        native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+agent+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
        golden=b'# SSC259: cold fixed same-active same-cutoff resume; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+agent+b' --resume 343a5a1b-d064-47d5-88c2-31c36d7ba7a4\n'
        self.assertEqual(writer.fixed_dropin(base,native),golden)
        for b,n in [(None,native),(base,None),(base,b'foreign'),(base+base,native),(base.replace(b'-cp',b'--resume x -cp'),native),(base.replace(b'-cp',b'-javaagent:foreign -cp'),native),(base.replace(b'/usr/bin/java',b'java'),native)]:
            with self.assertRaises(ValueError):writer.fixed_dropin(b,n)

    def exercise(self,fault=0,zero=False,foreign=False,owned=False):
        events=[];fds=set()
        class Ops:
            def __getattr__(self,n):
                native=getattr(os,n)
                if not callable(native):return native
                def call(*args,**kwargs):
                    events.append(n)
                    if len(events)==fault:raise OSError('independent injected IO')
                    if n=='open'and args[0]=='/':args=(anchor,*args[1:])
                    if n=='write':return 0 if zero else native(args[0],args[1][:13])
                    value=native(*args,**kwargs)
                    if n=='open':fds.add(value)
                    if n=='close':fds.remove(args[0])
                    return value
                return call
        def md(fd):
            s=ops.fstat(fd);return [s.st_dev,s.st_ino,0,0,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
        def named_md(name,fd):
            s=ops.stat(name,dir_fd=fd,follow_symlinks=False);return [s.st_dev,s.st_ino,0,0,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
        ops=Ops()
        with tempfile.TemporaryDirectory(prefix='pg1160-root-synthetic-')as tmp:
            anchor=Path(tmp)/'anchor';anchor.mkdir(mode=0o755)
            if owned:
                (anchor/'run').mkdir(mode=0o755);(anchor/'run/systemd').mkdir(mode=0o755);p=anchor/'run/systemd/system'
            else:p=Path(tmp)/'system'
            p.mkdir(mode=0o755);p.chmod(0o755);s=p.stat();expected=[s.st_dev,s.st_ino,0,0,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
            golden=b'[Service]\nExecStart=independent --resume public\n'
            if foreign:(p/'foreign').write_bytes(b'preserved-independent')
            error=None
            with patch.object(writer,'os',ops),patch.object(writer,'metadata',md),patch.object(writer,'named_metadata',named_md):
                try:writer.owned_prepare(expected,golden)if owned else writer.prepare(p,expected,golden)
                except (OSError,ValueError)as failure:error=failure
            try:
                if error is None:
                    self.assertEqual((p/writer.UNIT/writer.NAME).read_bytes(),golden)
                    self.assertEqual((p/writer.UNIT).stat().st_mode&0o777,0o755)
                    self.assertEqual((p/writer.UNIT/writer.NAME).stat().st_mode&0o777,0o644)
                    self.assertFalse(fds)
                if foreign:self.assertEqual((p/'foreign').read_bytes(),b'preserved-independent');self.assertNotIn('mkdir',events)
                return events,error
            finally:
                for fd in fds:os.close(fd)

    def test_real_fd_shortwrites_every_io_fault_and_foreign(self):
        events,error=self.exercise();self.assertIsNone(error)
        self.assertGreater(events.count('write'),1)
        for point in range(1,len(events)+1):
            with self.subTest(point=point,operation=events[point-1]):
                _,error=self.exercise(fault=point);self.assertIsInstance(error,OSError)
        _,error=self.exercise(zero=True);self.assertIsInstance(error,ValueError)
        _,error=self.exercise(foreign=True);self.assertIsInstance(error,ValueError)
        print('PG1160_RUNTIME_ORACLE faultPositions='+str(len(events))+' realFD=true shortWrites=true syntheticRoot=true VM0=true')

    def test_owned_ancestor_real_fd_every_fault(self):
        events,error=self.exercise(owned=True);self.assertIsNone(error)
        for point in range(1,len(events)+1):
            with self.subTest(point=point,operation=events[point-1]):
                _,error=self.exercise(fault=point,owned=True);self.assertIsInstance(error,OSError)
        _,error=self.exercise(foreign=True,owned=True);self.assertIsInstance(error,ValueError)
        print('PG1160_ANCESTOR_ORACLE faultPositions='+str(len(events))+' heldAncestorFD=true syntheticRoot=true VM0=true')


if __name__=='__main__':unittest.main()
