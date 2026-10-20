"""New-only25 after the owned reader-lifetime fixture fix; original v1 remains rejected."""
from types import FunctionType
import pg6164_native_retention_selected as profile

OLD='f2273aac71569e671b3ba1805f19479cd9dab864'
TEST='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/OwnedRetentionProcess.java'


def main():
    root=profile.ROOT
    current=profile.subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if set(profile.subprocess.check_output(['git','diff','--name-only',OLD,current,'--','src'],cwd=root,text=True).splitlines())!={TEST}:
        raise ValueError('one Test helper fix only; all production/other tests unchanged')
    if profile.subprocess.check_output(['git','diff',OLD,current,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=root):
        raise ValueError('build/static/Current unchanged')
    scope={**vars(profile),'CODE':current,'SLOT':'pg6166-native-retention-selected-v2'}
    return FunctionType(profile.main.__code__,scope)()


if __name__=='__main__':raise SystemExit(main())
