"""BUG1125 fixed debug-only record delta; preserve old1533 refused qualification."""
import inspect
from pathlib import Path
import pg1533_filesystem_full_qualification as prior

RECORDS=['dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy$Metadata.class','dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy$Snapshot.class']

def server_source():
    raw=prior.CODE
    old="require(set(changed)=={'batch:dev/codex/schubert/nk/batch/file/InspectorEnvironmentReader$NioIo.class','batch:dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy.class'})"
    new="require(set(changed)=={'batch:dev/codex/schubert/nk/batch/file/InspectorEnvironmentReader$NioIo.class','batch:dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy.class','batch:dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy$Metadata.class','batch:dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy$Snapshot.class'})"
    if raw.count(old)!=1:raise ValueError('fixed independent whole delta boundary refused')
    contract=Path(__file__).with_name('pg1540_debug_line_delta.py').read_text()
    addition="\nDEBUG_SOURCE="+repr(contract)+"\ndebug={};exec(compile(DEBUG_SOURCE,'<fixed independent debug delta>','exec'),debug)\ndebug_lines={}\n"
    addition+="with zipfile.ZipFile(B/'source-full-PG1476/src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar')as zold,zipfile.ZipFile(S/'src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar')as znew:\n"
    addition+=' for p in '+repr(RECORDS)+":\n  a=zold.read(p);bnew=znew.read(p);require(hashlib.sha256(a).hexdigest()==old['modules']['batch']['mainClassHashes'][p]and hashlib.sha256(bnew).hexdigest()==v['modules']['batch']['mainClassHashes'][p])\n  debug_lines[p]=debug['verify'](a,bnew,1)\n"
    raw=raw.replace(old,new+addition).replace("'changedClasses':sorted(changed)","'debugLineQualification':debug_lines,'semanticChangedClasses':2,'debugOnlyChangedClasses':2,'changedClasses':sorted(changed)")
    compile(raw,'<corrected independently bounded full qualification>','exec')
    return raw

def main():
    raw=inspect.getsource(prior.main).replace('pg1533-filesystem-full-qualified-v1','pg1541-filesystem-full-qualified-v2')
    ns={**prior.__dict__,'CODE':server_source()}
    exec(compile(raw,'<new-only full qualification transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
