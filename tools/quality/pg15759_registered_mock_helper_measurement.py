"""Correct original Mock12 effects only; do not rerun Product or passive coverage."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15758_registered_mock_helper_measurement as previous
RAW=previous.RAW
RUN=previous.RUN
OUT=data.BASE/'PG15759-registered-mock-helper-measurement-post-v2'
OLD='843d77fda87ded57728d392717a6e454ba09a8a2f4f904f9e2818a2dcd0c85a7'
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(raw):previous.assess(raw)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old=data.read_checked(previous.OUT/'manifest.json',OLD)
    parent=data.read_checked(data.BASE/'PG14542-mock-servlet-security-whole-twelve-post-v1/manifest.json','b3e3509aab38e895675a59f93f6b8fe8c01d8614b799b840d10065bf1513f36c')
    require(old['actualExit']==parent['actualExit']==0 and old['source']==parent['source']==previous.original.SOURCE and old['cryptoOrKeyOperationsInvoked'] is False and 'cryptoOrKeyOperationsInvoked' not in parent,'observed new false versus old missing fields')
    raw=data.read_checked(data.BASE/'PG14540-mock-servlet-security-whole-twelve-pt-v1/manifest.json',RAW);assess(raw)
    test=previous.original.TESTS['ClosedServletSecurityFilterTest'];test_text=test.read_text()
    trace=data.ROOT/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestTrace.java';trace_text=trace.read_text()
    require(test_text.count('UUID::randomUUID')>=1 and 'new TestingAuthenticationToken("foreign", "secret", "ROLE_ADMIN")' in test_text,'original synthetic UUID/foreign token fixture')
    require('UUID requestId = WebRequestContext.identify(request, identifiers);' in trace_text and 'Objects.requireNonNull(identifiers.get(), "eventId")' in trace_text,'actual supplied public request/event IDs')
    require(not any(v in trace_text for v in ['MessageDigest','Mac.getInstance','Cipher.getInstance','KeyStore','KeyRing']),'trace does not introduce key/digest workflow')
    result=copy.deepcopy(old)
    correction=dict(oldPostSha256=OLD,oldCryptoInvoked=False,oldCryptoKind='NONE_IN_REVIEWED_DOMAIN_BODY',effectiveCryptoInvoked=True,effectiveCryptoKind='UUID_V4_PUBLIC_REQUEST_EVENT_IDENTIFIERS_ONLY',oldPublicSyntheticFixtureCredentialsUsed=False,effectivePublicSyntheticFixtureCredentialsUsed=True,actualDeployedCredentialsOrKeysUsed=False,sourceHashes={str(test.relative_to(data.ROOT)):data.sha(test.read_bytes()),str(trace.relative_to(data.ROOT)):data.sha(trace.read_bytes())},bug='BUG2146',originalParentEffectFields='MISSING_NOT_FALSE',newProductExecution=False)
    result.update(invocation=invocation,cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=correction['effectiveCryptoKind'],publicSyntheticFixtureCredentialsUsed=True,effectDisclosureCorrection=correction,effectDisclosureTimeDomain='ORIGINAL_REGISTERED_MOCK12_RUNTIME; THIS_TOOL_METADATA_ONLY',productMethodsInvokedByCorrection=0)
    changed={'invocation','cryptoOrKeyOperationsInvoked','cryptoOperationKind','publicSyntheticFixtureCredentialsUsed'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed),'every previous measured counter/result unchanged')
    require(result['actualSecretKeysLoaded'] is result['actualCredentialValuesUsed'] is result['actualAuthenticationOrSessionIssued'] is False,'actual deployed secrets and authority remain zero')
    verify(raw['begin']['invocation']);verify(old['invocation']);verify(parent['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
