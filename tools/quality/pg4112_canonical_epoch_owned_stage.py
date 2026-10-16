"""BUG1338: new-only corrected plan; retain and reuse the already-qualified Java bytes."""
import inspect
import json
import sys
import types
import pg4098_interruption_checked_owned_stage as previous
import pg4088_failed_done_owned_sources as source
import pg4058_original_read_profile as transport
from pg4060_original_profile_dual_stack import once

TOOLS='pg4112-canonical-epoch-owned-tools-v1'
INSPECT='pg4114-canonical-epoch-owned-inspect-v1'


def payload(action):
    role=types.SimpleNamespace(**{**vars(source),'TOOLS':TOOLS,'INSPECT':INSPECT})
    ns={**vars(previous),'role':lambda:role}
    exec(compile(inspect.getsource(previous.payload),'<corrected epoch stage>','exec'),ns)
    raw=ns['payload'](action)
    if action=='compile':
        oldraw=(transport.W/(previous.TOOLS+'-compile')/'manifest.safe.json').read_bytes()
        old=json.loads(oldraw)
        if old['actualExit']!=0 or old['result']['actualExit']!=0:raise ValueError('qualified former compile required')
        original="r=subprocess.run(args,env=env,capture_output=True,timeout=40);(save/'compile.private.log').write_bytes(r.stdout+r.stderr)"
        reuse="\nFORMER="+repr(old['result'])+"\nformer=Path('/var/lib/pgpt-s1-preservation/"+previous.TOOLS+"')\n"+REUSE
        raw=once(raw,original,reuse)
        raw=once(raw,"'compileCommand':args", "'compileCommand':None,'javaCompileIssued':False,'classReuseFrom':"+repr(previous.TOOLS))
    compile(raw,'<corrected epoch full owned stage>','exec');return raw


REUSE=r'''
require(hashlib.sha256(java_raw).hexdigest()==FORMER['javaSha256']and ANNOTATION_SHA==FORMER['annotationSha256'])
for name,digest in FORMER['inputFileHashes'].items():
 p=former/name;before=metadata(p);s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest and metadata(p)==before)
for name,digest in FORMER['classHashes'].items():
 require(name.startswith('dev/codex/schubert/nk/batch/file/')and '..'not in Path(name).parts and name.endswith('.class'))
 p=former/'classes'/name;before=metadata(p);s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));content=p.read_bytes();require(hashlib.sha256(content).hexdigest()==digest and metadata(p)==before)
 target=classes/name;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with target.open('xb')as f:f.write(content);f.flush();os.fsync(f.fileno())
import types
r=types.SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
(save/'compile.private.log').write_bytes(b'No javac: exact qualified Java/annotation/class bytes reused; corrected plan independently staged\n')
'''


def main():
    if sys.argv[1:]not in (['compile'],['inspect']):raise SystemExit('compile(copy qualified class) or inspect')
    ns={**vars(previous),'TOOLS':TOOLS,'INSPECT':INSPECT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<corrected epoch transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
