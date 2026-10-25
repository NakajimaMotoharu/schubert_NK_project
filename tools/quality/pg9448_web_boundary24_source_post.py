"""Independent frozen fullpath Web boundary24 labels, related scopes and module counterexample."""
from pathlib import Path
import explicit_primary_source_post as post

def other_module(path):
    prefix='src/schubert-nk-web/'
    if not path.startswith(prefix):raise ValueError('explicit Web source module required')
    return 'src/schubert-nk-api/'+path.removeprefix(prefix)

if __name__=='__main__':
    assert other_module('src/schubert-nk-web/src/test/java/p/Foo.java')=='src/schubert-nk-api/src/test/java/p/Foo.java'
    try:other_module('src/schubert-nk-api/src/test/java/p/Foo.java')
    except ValueError:pass
    else:raise AssertionError('unscoped module mutation accepted')
    post.run(Path(__file__),post.BASE/'PG9448-web-boundary24-source-post-v1','PG9446-web-boundary24-source-metadata-v1',
      '5b5a5f49cf35b72e83c90e0a339c9bd6598688ad543bfae52628c2cbd440892d','fb92c1a50796f5fa07f2dceb1437e48b729e3634ee4000217d3de339fb6ec50f',
      'evidence/01_PT/018_NK-OPS-001/1918_G13WebBoundary24_主関連責任仕様.md','9e59876aa32d579090a884698df526a8ff5196a5f8fafb5be2638b8692c5f405',
      'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/',('api/file/','web/bootstrap/','web/security/','web/session/'),24,
      {'ServiceCredentialId':'WBS-P003-07','WebBrokerContexts':'WBS-P005-02','WebNativeCodecs':'WBS-P018-06',
       'WebNativeRuntime':'WBS-P018-06','WebManagementServer':'WBS-P018-06','ApiSessionInvalidHandler':'WBS-P015-06',
       'LocalLogoutHandler':'WBS-P015-04','EncryptedSessionRequestCache':'WBS-P015-02','EncryptedSessionSecurityContextRepository':'WBS-P015-02',
       'SessionOperationToken':'WBS-P015-03','MqLoginSuccessHandler':'WBS-P007-06','WebErrorDispatchFilter':'WBS-P016-24'},
      source_path_mutator=other_module,source_mutator_vectors=2)
