"""New-only ordinary25 after exact dependency-diagnostic oracle correction."""
from types import FunctionType
import pg6164_native_retention_selected as profile

OLD='423f329ce7dcdbd339669018f1e10ad23dc1b8d3'
TESTS={
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/OwnedRetentionProcess.java',
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/ApiFactoryNativeRetentionTest.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebFactoryNativeRetentionTest.java'}


def main():
    root=profile.ROOT
    current=profile.subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    changed=set(profile.subprocess.check_output(['git','diff','--name-only',OLD,current,'--','src'],cwd=root,text=True).splitlines())
    if changed!=TESTS:raise ValueError('exact three fixture paths; production unchanged')
    if profile.subprocess.check_output(['git','diff',OLD,current,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=root):
        raise ValueError('build/static/Current unchanged')
    return FunctionType(profile.main.__code__,{**vars(profile),'CODE':current,
        'SLOT':'pg6170-native-retention-selected-v3'})()


if __name__=='__main__':raise SystemExit(main())
