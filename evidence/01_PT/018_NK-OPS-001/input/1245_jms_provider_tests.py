"""Add independent provider fault contracts; retain original whole seven cases in each class."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';out=B/'evidence/PG26474-jms-provider-tests-manufacture-v1';assert not out.exists();out.mkdir()
before=json.loads((B/'evidence/PG26470-jms-provider-classification-before-v1/manifest.json').read_text());records=[]
sites='''
      {"getBodyLength", ""}, {"getBody", ""}, {"getJMSDestination", ""},
      {"getJMSReplyTo", ""}, {"getJMSMessageID", ""}, {"getJMSCorrelationID", ""},
      {"getJMSExpiration", ""}, {"getJMSDeliveryMode", ""},
      {"propertyExists", "JMSXDeliveryCount"}, {"getIntProperty", "JMSXDeliveryCount"},
      {"propertyExists", "NKMessageID"}, {"getStringProperty", "NKMessageID"},
      {"propertyExists", "NKLayoutID"}, {"getStringProperty", "NKLayoutID"},
      {"propertyExists", "NKProtocolVersion"}, {"getStringProperty", "NKProtocolVersion"}
'''
for side,path in zip(['web','api'],before['wholeSafeCandidateTests']):
 p=R/path;old=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==before['beforeSnapshots'][path]['sha256']
 fixture='validReply()' if side=='web' else 'validRequest()';call='DECODER.decode(message)' if side=='web' else 'GUARD.read(message, REQUEST_ROUTE)'
 method='''
  @Test
  void providerFailuresRetainExactIdentityAndEarlierValidationStopsLaterReads() {
    // BUG2659/YKT2339; SS321 sections 7-8 / SSC332, PT-JMS-PROVIDER-SIDE-001.
    // Provider failure proves no malformed value: the oracle is original object identity.
    String[][] sites = {SITES};
    for (String[] site : sites) {
      Throwable[] failures = {
        new IllegalArgumentException("synthetic provider failure"),
        new NullPointerException("synthetic provider failure"),
        new AssertionError("synthetic provider failure"),
        new jakarta.jms.JMSException("synthetic provider failure")
      };
      for (Throwable failure : failures) {
        BytesMessage message = faultingMessage(FIXTURE, site[0], site[1], failure);
        Throwable actual = assertThrows(failure.getClass(), () -> CALL);
        assertSame(failure, actual, site[0] + ":" + site[1]);
      }
    }
    // Preserve left-to-right acquisition/validation: these later failures must not replace
    // an earlier malformed UUID/layout. Values/diagnostics are literal independent oracles.
    String[][] earlier = {{CORRELATION_FIELD, "getJMSExpiration", ""},
        {"NKLayoutID", "getStringProperty", "NKProtocolVersion"}};
    for (String[] entry : earlier) {
      BytesMessage message = faultingMessage(with(FIXTURE, entry[0], "bad"),
          entry[1], entry[2], new AssertionError("later getter must not run"));
      PermanentProtocolException actual =
          assertThrows(PermanentProtocolException.class, () -> CALL);
      assertEquals("DIAGNOSTIC", actual.getMessage());
      assertTrue(actual.getCause() instanceof IllegalArgumentException);
    }
  }

  private static BytesMessage faultingMessage(
      Map<String, Object> values, String getter, String property, Throwable failure) {
    BytesMessage delegate = bytesMessage(values);
    return (BytesMessage) Proxy.newProxyInstance(BytesMessage.class.getClassLoader(),
        new Class<?>[] {BytesMessage.class}, (ignored, method, arguments) -> {
          if (method.getName().equals(getter)
              && (property.isEmpty() || property.equals(arguments[0]))) {
            throw failure;
          }
          return method.invoke(delegate, arguments);
        });
  }

'''.replace('SITES',sites).replace('SIDE',side.upper()).replace('FIXTURE',fixture).replace('CALL',call).replace('DIAGNOSTIC','reply transport identity is malformed' if side=='web' else 'transport identity property is malformed')
 anchor='  private static Map<String, Object> validReply()' if side=='web' else '  private static Map<String, Object> validRequest()';assert old.count(anchor)==1
 addedImport='import static org.junit.jupiter.api.Assertions.assertSame;\n';new=old.replace('import static org.junit.jupiter.api.Assertions.assertThrows;',addedImport+'import static org.junit.jupiter.api.Assertions.assertThrows;').replace(anchor,method+anchor)
 assert new.replace(method,'').replace(addedImport,'')==old
 fmt=TC/'google-java-format-1.36.1-all-deps.jar'
 if not fmt.exists():
  matches=list(TC.rglob('google-java-format-1.36.1-all-deps.jar'));assert len(matches)==1;fmt=matches[0]
 formatted=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(fmt),'-'],input=new,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert formatted.returncode==0,formatted.stderr
 p.write_text(formatted.stdout);records.append(dict(path=path,beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalCasesRetained=7,newCases=1,plannedGetterSites=16,plannedProviderKinds=4,plannedEarlyValidationCases=2,wholeRuntime='JMS_API_PROXY_AND_ARTEMIS_DESTINATION_VALUE_OBJECT_ONLY'))
(out/'manifest.json').write_text(json.dumps(dict(actualExit=0,records=records,productTestsExecuted=0,productionMainChanged=False,heldOperations=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newDefinitions=2,originalCasesRetained=14,productTestsExecuted=0)))
