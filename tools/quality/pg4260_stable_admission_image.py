"""BUG1347 stable nanosecond metadata; preserve failed reader and live Root."""
import inspect
import pg4250_current_admission_image as previous
from pg4060_original_profile_dual_stack import once

SLOT='pg4260-stable-admission-image-v1'
SOURCE,BOM,LIVE,ONCE,PUBLICATION=previous.SOURCE,previous.BOM,previous.LIVE,previous.ONCE,previous.PUBLICATION
live,project,execute=previous.live,previous.project,previous.execute


def metadata(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


def payload(binding):
    raw=previous.payload(binding)
    raw=once(raw,'def read(path):',inspect.getsource(metadata)+'\ndef read(path):')
    raw=raw.replace('path.lstat()==s','metadata(path.lstat())==metadata(s)').replace('os.fstat(fd)==s','metadata(os.fstat(fd))==metadata(s)')
    return raw


def before():
    ns={**vars(previous),'SLOT':SLOT}
    exec(compile(inspect.getsource(previous.before),'<new actual stable before receipt>','exec'),ns);return ns['before']()


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
