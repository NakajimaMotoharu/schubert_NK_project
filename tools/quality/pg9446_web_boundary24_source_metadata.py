"""1918 exact Web boundary24 source labels; no HTTP, DB, key, native or test runtime."""
from pathlib import Path
import explicit_primary_source_metadata as metadata

PREFIX='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/'
TABLE={
 'api/file/WebBrokerContextsCredentialTest.java':'WBS-P005-02',
 'api/file/WebNativeCodecsCredentialTest.java':'WBS-P018-06',
 'api/file/WebNativeRuntimeCredentialFixture.java':'WBS-P003-07',
 'web/bootstrap/WebAdmissionRemainderTest.java':'WBS-P018-06',
 'web/bootstrap/WebManagementDeadlineTest.java':'WBS-P018-06',
 'web/bootstrap/WebNativeRuntimeOwnedComponentTest.java':'WBS-P018-06',
 'web/bootstrap/WebNativeRuntimePartialTest.java':'WBS-P018-06',
 'web/bootstrap/WebRuntimeRemainderTest.java':'WBS-P018-06',
 'web/bootstrap/WebUnstartedManagementTest.java':'WBS-P018-06',
 'web/security/WebAuthorizationFilterTest.java':'WBS-P015-02',
 'web/security/WebRequestIdentityConsistencyTest.java':'WBS-P015-02',
 'web/session/ApiSessionInvalidTest.java':'WBS-P015-06',
 'web/session/EmbeddedWebSecurityTest.java':'WBS-P015-02',
 'web/session/ErrorMvcTest.java':'WBS-P016-24',
 'web/session/LogoutControllerTest.java':'WBS-P015-04',
 'web/session/SessionAccessFailureTest.java':'WBS-P015-02',
 'web/session/SessionFormLoginTest.java':'WBS-P015-02',
 'web/session/SessionLoginHandlerTest.java':'WBS-P007-06',
 'web/session/SessionOperationTokenV2Test.java':'WBS-P015-03',
 'web/session/SessionSavedRequestTest.java':'WBS-P015-02',
 'web/session/SessionSecurityContextTest.java':'WBS-P015-02',
 'web/session/WebCsrfIntegrationTest.java':'WBS-P015-02',
 'web/session/WebRequestSecurityTest.java':'WBS-P015-02',
 'web/session/WebSecurityChainTest.java':'WBS-P015-02'}
PRIMARY={PREFIX+path:owner for path,owner in TABLE.items()}

if __name__=='__main__':
    assert len(PRIMARY)==24
    metadata.run(Path(__file__),metadata.BASE/'PG9446-web-boundary24-source-metadata-v1',metadata.ROOT.parent/'pgpt-runs/PG379/pg9446-web-boundary24-source-metadata-v1',
      PRIMARY,'PG9438-api-jms20-source-join-v1/manifest.json','0eb6d96826969b6f605e4001e738c0f4ab802ce3f6cfbe734f2811ecdf41fd88',False)
