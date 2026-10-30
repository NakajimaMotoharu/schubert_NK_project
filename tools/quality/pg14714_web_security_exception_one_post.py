"""Independent full two-Source scope; singleton metadata uses qualifiedv2, not a Login test."""
import reviewed_whole_pure_source_post_v2 as core
import pg14712_web_security_exception_one_pt as original

PROFILE={
    'rawFolder':'PG14712-web-security-exception-one-pt-v1',
    'rawSha256':'ec4f2db27e4b62c8ea0fc6de39d2776c1db28a69e968f4a2e3b95f83d0357d0f',
    'postFolder':'PG14714-web-security-exception-one-post-v1',
    'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',
    'originalTestsAlreadyCounted':False,
    'sources':{}
}
for name,pin in [
    ('MqLoginExchangeException','4f36806cd08ce5c3eb29d15694392b326da736f7e8f5e371552fe24988cd9684'),
    ('MqLoginLockedException','badfaf084badf1923f112e49a89aa2b7ce61712ae8d66e4e181231dd856b1c1b')]:
    internal='dev/codex/schubert/nk/web/security/'+name
    PROFILE['sources'][internal]=dict(path='src/schubert-nk-web/src/main/java/'+internal+'.java',sha256=pin,module='web',closure=[internal,internal+'$Reason'] if name=='MqLoginExchangeException' else [internal],owner='WBS-P015-02')

if __name__=='__main__':core.verify_profile(original,PROFILE)
