"""New private Linux fixture for BUG1025; no real publication or Unit mutation."""
import ast
from pg1089_private_exchange_fixture import payload as previous
from pg1051_cold_tree_preflight_v2 import dispatch


def payload():
    raw=previous().replace('PG1089-private-exchange-fixture-v1','PG1105-stale-atime-guest-fixture-v1').replace('pg1089-exchange-fixture-v1','pg1105-stale-atime-fixture-v1')
    raw=raw.replace("readlink())=='/opt/schubert-nk/releases/0.1.0-PG932'", "readlink())=='/opt/schubert-nk/releases/0.1.0-PG1068'")
    raw=raw.replace("assert not list(pathlib.Path('/run/schubert-nk/startup').iterdir())", "assert pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes()==pathlib.Path('/var/lib/pgpt-s1-preservation/pg1094-cold-activate-v1/new-epoch.private').read_bytes()")
    marker="row=env['linked_attributes'](fd,'pg1088-current.part',old)"
    if raw.count(marker)!=1:raise ValueError('fixed private stale fixture refused')
    raw=raw.replace(marker,"os.utime('pg1088-current.part',ns=(1,1),dir_fd=fd,follow_symlinks=False)\nfirst_stat=os.fstat(old)\n"+marker)
    raw=raw.replace("assert row['metadata'][1]==old_inode", "assert os.fstat(old).st_atime_ns!=first_stat.st_atime_ns\nassert row['metadata']==[first_stat.st_dev,first_stat.st_ino,first_stat.st_uid,first_stat.st_gid,first_stat.st_mode,first_stat.st_nlink,first_stat.st_size,first_stat.st_mtime_ns,first_stat.st_ctime_ns]\nassert row['metadata'][1]==old_inode")
    raw=raw.replace("'actualCurrentActivated':False", "'staleAtimeUpdatedWithoutChangingNineContractFields':True")
    ast.parse(raw);return raw


if __name__=='__main__':dispatch('PG1105-stale-atime-guest-fixture-v1','pg1105-stale-atime-guest-fixture-v1',payload())
