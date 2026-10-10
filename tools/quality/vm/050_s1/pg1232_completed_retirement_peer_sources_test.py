"""Execute actual changed holder with independent proc/FD/FLOCK vectors, VM0."""
import ast
from pathlib import Path
import os
import stat
import tempfile
import types
import unittest
from pg1232_completed_retirement_peer_sources import generated

class PeerClosureTest(unittest.TestCase):
    def exercise(self,action='retire',baduid=False,badlock=False,missingfd=False,ticks=100):
        s=generated()['pg1232_native_owned_stop.py'];nodes=[n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)and n.name in {'require','tick','holder'}]
        self.assertEqual(len(nodes),3)
        with tempfile.TemporaryDirectory(prefix='pg1232-proc-port-')as tmp:
            root=Path(tmp);proc=root/'proc';run=root/'locks';parent=proc/'7417'
            (parent/'fd').mkdir(parents=True);run.mkdir()
            (parent/'cmdline').write_bytes(b'/opt/jdk-25.0.4/bin/java\x00Pg1232NativeStop\x00'+action.encode()+b'\x00')
            fields=['0']*20;fields[19]=str(ticks);(parent/'stat').write_text('7417 (java) '+' '.join(fields))
            lines=[]
            for i,name in enumerate(['maintenance.lock','startup-admission.lock']):
                p=run/name;p.touch(mode=0o600);p.chmod(0o600);m=p.stat()
                if not missingfd or i!=0:(parent/'fd'/str(i)).symlink_to(p)
                lines.append('1: FLOCK ADVISORY WRITE '+('9999'if badlock else'7417')+' '+f'{os.major(m.st_dev):02x}:{os.minor(m.st_dev):02x}:{m.st_ino}'+' 0 EOF')
            (proc/'locks').write_text('\n'.join(lines)+'\n')
            class PortPath:
                def __init__(self,p):
                    p=str(p)
                    if p=='/proc':p=str(proc)
                    elif p=='/proc/locks':p=str(proc/'locks')
                    elif p=='/run/schubert-nk':p=str(run)
                    self.native=Path(p)
                def __truediv__(self,n):return PortPath(self.native/n)
                def __str__(self):return str(self.native)
                def read_bytes(self):return self.native.read_bytes()
                def read_text(self):return self.native.read_text()
                def readlink(self):return self.native.readlink()
                def iterdir(self):return[PortPath(p)for p in self.native.iterdir()]
                def stat(self):
                    m=self.native.stat();return types.SimpleNamespace(st_uid=1 if baduid else 0,st_gid=0,st_mode=m.st_mode,st_nlink=m.st_nlink,st_dev=m.st_dev,st_ino=m.st_ino)
            scope={'pathlib':types.SimpleNamespace(Path=PortPath),'os':types.SimpleNamespace(getppid=lambda:7417,major=os.major,minor=os.minor),'stat':stat}
            exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual changed peer holder>','exec'),scope)
            return scope['holder']()

    def test_actual_holder_normal_unknown_action_owner_fd_lock_and_generation(self):
        self.assertEqual(self.exercise(),(7417,100))
        for action in ['stop','resume','retire foreign','retire\n','']:
            with self.subTest(action=action),self.assertRaises(ValueError):self.exercise(action=action)
        for field in ['baduid','badlock','missingfd']:
            with self.subTest(field=field),self.assertRaises(ValueError):self.exercise(**{field:True})
        self.assertNotEqual(self.exercise(ticks=101),self.exercise(ticks=100))
        values=generated();j=values['Pg1232NativeStop.java'];r=values['pg1232_native_refs.py']
        self.assertTrue('"retire".equals(args[0])'in j and '"retire".equals(name)'in j and 'refs.check("retire")'in j)
        self.assertTrue("sys.argv[1]=='retire'"in r)
        self.assertFalse('pg1224-native-stop-v1'in j)
        print('PG1232_ACTUAL_HOLDER_ORACLE action/owner/fd/flock/generation qualified; VM0=true')

if __name__=='__main__':unittest.main()
