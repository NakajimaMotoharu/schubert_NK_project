"""BUG1147: distinguish attribute FDs, lock FDs and shared OFD by kcmp.

Fixed current owner only. Any unsupported syscall or changed identity refuses.
No permissions relaxation, lock mutation or signal capability is introduced.
"""
import inspect
import pg1650_retained_no_db_readonly_proof as prior

SLOT = 'pg1651-retained-no-db-proof-v2'


def fd_relation(name, linked, locking, compare):
    expected = {'maintenance.lock': (['30', '33', '34'], ['34']), 'startup-admission.lock': (['43', '128'], ['43', '128'])}
    if name not in expected or type(linked) is not list or type(locking) is not list or (linked, locking) != expected[name]:
        raise ValueError('fixed attribute/locking FD sets required')
    values = []
    for i, a in enumerate(linked):
        for b in linked[i + 1:]:
            result = compare(int(a), int(b))
            if type(result) is not int or result < 0 or (result == 0) != (name == 'startup-admission.lock'):
                raise ValueError('exact current OFD relation required')
            values.append({'a': a, 'b': b, 'sameOfd': result == 0})
    return values


BODY = r'''
def owned_lock(name):
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 hits=[]
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  f=line.split()
  if len(f)<8:continue
  d=f[5].split(':')
  if len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):hits.append(f)
 require(len(hits)==1 and hits[0][1:5]==['FLOCK','ADVISORY','WRITE','289328'])
 actual=actor();linked=sorted([fd for fd,v in actual['fds'].items()if tuple(v['metadata'][:2])==(s.st_dev,s.st_ino)],key=int);locking=[]
 for fd in linked:
  words=[line.split()for line in(P/'fdinfo'/fd).read_text().splitlines()if line.startswith('lock:')]
  require(len(words)<=1)
  if words:
   require(words[0][2:6]==['FLOCK','ADVISORY','WRITE','289328']and words[0][6:]==[f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}','0','EOF']);locking.append(fd)
 def compare(a,b):
  import ctypes
  libc=ctypes.CDLL(None,use_errno=True);ctypes.set_errno(0)
  value=libc.syscall(312,289328,289328,0,a,b)
  require(ctypes.get_errno()==0);return value
 relations=fd_relation(name,linked,locking,compare)
 return {'name':name,'metadata':metadata9(s),'fds':linked,'lockingFds':locking,'relations':relations}
'''


def payload():
    raw = prior.payload()
    start = raw.index('def owned_lock(name):')
    end = raw.index('bus=dbus.SystemBus(private=True);manager=', start)
    raw = raw[:start] + inspect.getsource(fd_relation) + '\n' + BODY + '\n' + raw[end:]
    raw = raw.replace('pg1650-retained-no-db-proof-v1', SLOT)
    compile(raw, '<fixed current attribute/locking/OFD readonly proof>', 'exec')
    return raw


def main():
    ns = {**prior.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(prior.main), '<new-only current noDB proof v2>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
