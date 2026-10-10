"""New private guest fixture only, no real current/epoch/DB/Unit mutation."""
import hashlib
from pathlib import Path
from pg1051_cold_tree_preflight_v2 import dispatch


def payload():
    code=Path(__file__).with_name('pg1088_cold_exchange_io.py').read_bytes()
    prefix='SOURCE='+repr(code.decode())+'\nSOURCE_SHA='+repr(hashlib.sha256(code).hexdigest())+'\n'
    body=r'''
import pathlib,hashlib,json,os,subprocess
assert os.geteuid()==0
assert hashlib.sha256(SOURCE.encode()).hexdigest()==SOURCE_SHA
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6'
def unchanged():
 assert str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG932'
 assert not list(pathlib.Path('/run/schubert-nk/startup').iterdir())
 assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1068/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'
 assert 'ro'in subprocess.check_output(['findmnt','--target','/opt/schubert-nk/releases/0.1.0-PG1068','--noheadings','--output','VFS-OPTIONS'],text=True).strip().split(',')
unchanged()
env={'__name__':'private_fixture_only'};exec(SOURCE,env)
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1089-exchange-fixture-v1')
assert not os.path.lexists(root);root.mkdir(mode=0o700)
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
os.symlink('/fixture/old','current',dir_fd=fd);os.symlink('/fixture/new','pg1088-current.part',dir_fd=fd);os.fsync(fd)
old=os.open('current',os.O_PATH|os.O_NOFOLLOW,dir_fd=fd)
new=os.open('pg1088-current.part',os.O_PATH|os.O_NOFOLLOW,dir_fd=fd)
old_inode=os.fstat(old).st_ino;new_inode=os.fstat(new).st_ino
first=env['linked_attributes'](fd,'current',old);assert first['target']=='/fixture/old'and first['acl']==[]
env['exchange'](fd,'pg1088-current.part');os.fsync(fd)
assert os.stat('current',dir_fd=fd,follow_symlinks=False).st_ino==new_inode
assert os.readlink('current',dir_fd=fd)=='/fixture/new'
row=env['linked_attributes'](fd,'pg1088-current.part',old)
assert row['metadata'][1]==old_inode and row['metadata'][5]==1 and row['target']=='/fixture/old'and row['acl']==[]
os.mkdir('private',mode=0o700,dir_fd=fd);private=os.open('private',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
os.rename('pg1088-current.part','current-link.private',src_dir_fd=fd,dst_dir_fd=private);os.fsync(fd);os.fsync(private)
final=env['linked_attributes'](private,'current-link.private',old)
assert final['metadata'][1]==old_inode and final['metadata'][5]==1 and final['target']=='/fixture/old'and final['acl']==[]
assert os.readlink('current',dir_fd=fd)=='/fixture/new'
unchanged()
os.close(private);os.close(new);os.close(old);os.close(fd)
print(json.dumps({'run':'PG1089-private-exchange-fixture-v1','actualExit':0,'fixtureOnly':True,
 'realCurrentEpochDbUnitsUnmodified':True,'sameFilesystemAtomicExchange':True,'publicFixtureLinkNeverRemoved':True,
 'oldInodeTargetAndAttrsPreservedLinked':True,'oldLinkPrivateAndSingle':True,'allFixtureFdsNormalClosed':True,
 'actualCurrentActivated':False,'formalAccepted':False}))
'''
    return prefix+body


if __name__=='__main__':dispatch('PG1089-private-exchange-fixture-v1','pg1089-private-exchange-fixture-v1',payload())
