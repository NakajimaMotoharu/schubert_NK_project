"""Root file primitive oracle in a new isolated fixture; no app, authority, DB or source transition."""
import os,pathlib,stat,sys
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg471-completed-tools-v1')
from pg471_prepare_native_v2 import create_file
assert os.geteuid()==0
base=pathlib.Path('/var/tmp/pg471-private-archive-v1');assert not base.exists() and not base.is_symlink();base.mkdir(mode=0o700);os.chmod(base,0o700)
old=len(list(pathlib.Path('/proc/self/fd').iterdir()))
literal=b'private archive independent vector\n';p=base/'new.private.exec';create_file(p,literal,0o600)
s=p.lstat();assert (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink,s.st_size)==(0,0,0o600,1,35) and p.read_bytes()==literal
identity=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
for dest in [p,base/'link.private.exec',base/'directory']:
 if dest.name=='link.private.exec':dest.symlink_to(p)
 if dest.name=='directory':dest.mkdir(mode=0o700)
 try:create_file(dest,b'must not replace',0o600);raise AssertionError('must reject existing file/link/directory')
 except FileExistsError:pass
 assert p.read_bytes()==literal
s=p.lstat();assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==identity
assert len(list(pathlib.Path('/proc/self/fd').iterdir()))==old
print('PG471_PRIVATE_ARCHIVE actualRoot600=true literal35Bytes=true collisions3Refused=true oldBytesAndIdentityPreserved=true normalFdClose=true sync=true apps0=true')
