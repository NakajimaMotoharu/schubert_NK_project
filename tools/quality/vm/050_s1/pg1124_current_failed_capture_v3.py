"""New-only corrected current failed capture, both old/current source scopes."""
import ast
import inspect
from pathlib import Path
import pg1120_current_failed_capture as transport
from pg1122_current_failed_capture_v2 import payload as previous

R=Path(__file__).resolve().parent


def payload():
    raw=previous().replace('failed-capture-v2','failed-capture-v3')
    marker="for name,digest in baseline['artifacts'].items():require(hashlib.sha256((release/name).read_bytes()).hexdigest()==digest)"
    if raw.count(marker)!=1:raise ValueError('fixed dual artifact insertion refused')
    code=r'''
 old_release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG932')
 current_path='/opt/schubert-nk/releases/0.1.0-PG1068'
 original={name[len(current_path):].lstrip('/'):entry for name,entry in before['trees']['/opt/schubert-nk'].items()if name==current_path or name.startswith(current_path+'/')}
 now={name[len(current_path):].lstrip('/'):entry for name,entry in tree(pathlib.Path(current_path)).items()}
 artifactSummary=artifacts.qualify(baseline['artifacts'],original,now,(release/'RELEASE-MANIFEST.json').read_bytes(),lambda name:(old_release/name).read_bytes(),lambda name:(release/name).read_bytes(),'d5b00104280028d9ea81b44c1d1c805f3c2861ed','0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d')
'''
    raw=raw.replace(marker,code)
    raw=raw.replace("baseline['artifacts']['config/effective/backup-profile.json']",
                    "artifactSummary['currentArtifactHashes']['config/effective/backup-profile.json']")
    raw=raw.replace("'backupSummary':backupSummary","'artifactSummary':artifactSummary,'backupSummary':backupSummary")
    raw=raw.replace("'currentSource':value['source']","'currentSource':value['source'],'dualSourceScopesVerified':True")
    oracle=(R/'pg1123_dual_source_artifacts.py').read_text()
    raw="import types\nartifacts=types.ModuleType('independent_dual_source');exec("+repr(oracle)+",artifacts.__dict__)\n"+raw
    ast.parse(raw);return raw


def main():
    raw=inspect.getsource(transport.main)
    raw=raw.replace('pg1120-current-failed-capture-v1','pg1124-current-failed-capture-v3')
    raw=raw.replace('PG1120-current-failed-capture-v1','PG1124-current-failed-capture-v3')
    env=dict(transport.__dict__);env['PAYLOAD']=payload()
    exec(compile(raw,'<new-only two-source current failed capture>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
