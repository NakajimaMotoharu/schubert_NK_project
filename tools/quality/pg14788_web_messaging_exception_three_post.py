"""Whole three exception Sources, no JMS; prior Jms proof is not replaced or unioned."""
import reviewed_whole_pure_source_post_v2 as core
import pg14786_web_messaging_exception_three_pt as original

PROFILE={
 'rawFolder':'PG14786-web-messaging-exception-three-pt-v1',
 'rawSha256':'52064da3d915470dd5f002e8d4fe5c0f7cac959492b66b77641556f91819b9a2',
 'postFolder':'PG14788-web-messaging-exception-three-post-v1',
 'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',
 'originalTestsAlreadyCounted':False,
 'sources':{}}
for name,pin,owner in [
 ('JmsRequestReplyException','11ffd0f90e7064a7f42bef1029c65fc37e5cadbfe2b49a4b7bd3d775d9dd164b','WBS-P005-02'),
 ('ProtectedReadWireException','f22edac4ccb7f971a0123045be353b5cfe1eed0aadb496aabca520f69dce0879','WBS-P005-02'),
 ('ScenarioWireException','370b7d197c2c7f3808db4fda3d41c7f8cb55a74642459e598fd5eae276079de3','WBS-P016-07')]:
    internal='dev/codex/schubert/nk/web/messaging/'+name
    PROFILE['sources'][internal]=dict(path='src/schubert-nk-web/src/main/java/'+internal+'.java',sha256=pin,module='web',closure=[internal,internal+'$Reason'],owner=owner)

if __name__=='__main__':core.verify_profile(original,PROFILE)
