"""Read identity contract excludes access time; never mutates runtime files."""
def identity(s):
 return (s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_dev,s.st_ino,s.st_mtime_ns,s.st_ctime_ns)
