import types
from pg469_native_file_identity import identity
fields={'st_uid':0,'st_gid':0,'st_mode':0o100600,'st_nlink':1,'st_size':42,'st_dev':28,'st_ino':5678,'st_mtime_ns':100,'st_ctime_ns':110,'st_atime_ns':120}
assert identity(types.SimpleNamespace(**fields))==(0,0,0o100600,1,42,28,5678,100,110)
for name in fields:
 altered=dict(fields);altered[name]+=1
 assert (identity(types.SimpleNamespace(**fields))==identity(types.SimpleNamespace(**altered)))==(name=='st_atime_ns')
print('PG469_NATIVE_FILE_ORACLE independentAssertions=11 nativeMutation0=true')
