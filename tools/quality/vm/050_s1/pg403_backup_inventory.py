"""Read-only diagnostic metadata; no dump/credential bytes or unknown file hash emitted."""
import os, json, re, hashlib, stat
root = '/srv/schubert-nk/backup'
def metadata(s):
    return {k:getattr(s,k) for k in ['st_mode','st_uid','st_gid','st_nlink','st_size','st_dev','st_ino','st_mtime_ns','st_ctime_ns']}
result = {}
with os.scandir(root) as entries:
    names = sorted(e.name for e in entries)
assert len(names) <= 4096
for name in names:
    path = os.path.join(root,name)
    original = os.stat(path,follow_symlinks=False)
    entry = {'metadata':metadata(original)}
    if stat.S_ISDIR(original.st_mode):
        with os.scandir(path) as children:
            child_names = sorted(e.name for e in children)
        assert len(child_names) <= 4096
        files = {}
        sealed = re.fullmatch(r'[0-9]{8}-[0-9]{6}-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}',name)
        for child in child_names:
            target = os.path.join(path,child)
            observed = os.stat(target,follow_symlinks=False)
            details = metadata(observed)
            if sealed and child in ['MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'] and stat.S_ISREG(observed.st_mode):
                fd = os.open(target,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
                try:
                    assert metadata(os.fstat(fd)) == details
                    digest = hashlib.sha256()
                    while block := os.read(fd,131072): digest.update(block)
                    assert metadata(os.fstat(fd)) == details
                    details['sha256'] = digest.hexdigest()
                finally: os.close(fd)
            files[child] = details
        assert metadata(os.stat(path,follow_symlinks=False)) == entry['metadata']
        entry['files'] = files
    result[name] = entry
print(json.dumps(result,sort_keys=True,separators=(',',':')))
