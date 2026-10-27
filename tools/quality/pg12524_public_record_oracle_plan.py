"""Prior independent SS canary/null golden and two new pure Tests; no Main changes."""
import difflib
from pathlib import Path
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12524-public-record-oracle-plan-v1'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java'
GOLDEN={'configurationDiagnostic':'EffectiveConfigurations[non-secret=<redacted>]','journalDiagnostic':'BrokerJournalSummary[redacted]','missingConfigurationFields':['apiSha256','webSha256','roots','apiYaml','webYaml'],'missingContentsFields':['commonYaml','serviceYaml']}
ADDITION='''
  @Test
  void obsdata003ConfigurationAndJournalDiagnosticsHideIndependentPublicCanaries() {
    for (String marker :
        List.of("PUBLIC-RECORD-CANARY-ALPHA", "PUBLIC-RECORD-CANARY-BETA")) {
      String apiDigest = "a".repeat(64);
      String webDigest = "b".repeat(64);
      String journalDigest = "c".repeat(64);
      String commonYaml = marker + " COMMON-YAML-CANARY";
      String serviceYaml = marker + " SERVICE-YAML-CANARY";
      var contents = new ServiceConfigFiles.Contents(commonYaml, serviceYaml);
      var configurations =
          new RootReleaseAdmission.EffectiveConfigurations(
              apiDigest, webDigest, diagnosticRoots(marker), contents, contents);
      String configurationText = configurations.toString();
      String journalText = new BrokerJournalEvidence.Summary(5, journalDigest).toString();
      assertEquals("EffectiveConfigurations[non-secret=<redacted>]", configurationText);
      assertEquals("BrokerJournalSummary[redacted]", journalText);
      for (String forbidden :
          List.of(marker, apiDigest, webDigest, journalDigest, commonYaml, serviceYaml)) {
        assertFalse(configurationText.contains(forbidden));
        assertFalse(journalText.contains(forbidden));
      }
      for (String leaf : List.of("asset", "transfer", "backup", "log", "artemis", "staging")) {
        String absolutePath = "/public-diagnostic/" + marker + "/" + leaf;
        assertFalse(configurationText.contains(absolutePath));
        assertFalse(journalText.contains(absolutePath));
      }
    }
  }

  @Test
  void obsdata004NonNullConfigurationValuesRejectEachMissingFieldBeforeOwnership() {
    String apiDigest = "a".repeat(64);
    String webDigest = "b".repeat(64);
    var roots = diagnosticRoots("PUBLIC-NULL-FIELD-CANARY");
    String commonYaml = "PUBLIC-NULL-COMMON";
    String serviceYaml = "PUBLIC-NULL-SERVICE";
    var contents = new ServiceConfigFiles.Contents(commonYaml, serviceYaml);
    for (int missing = 0; missing < 5; missing++) {
      int field = missing;
      assertThrows(
          NullPointerException.class,
          () ->
              new RootReleaseAdmission.EffectiveConfigurations(
                  field == 0 ? null : apiDigest,
                  field == 1 ? null : webDigest,
                  field == 2 ? null : roots,
                  field == 3 ? null : contents,
                  field == 4 ? null : contents));
    }
    assertThrows(NullPointerException.class, () -> new ServiceConfigFiles.Contents(null, serviceYaml));
    assertThrows(NullPointerException.class, () -> new ServiceConfigFiles.Contents(commonYaml, null));
  }

  private static StorageRootLayout diagnosticRoots(String marker) {
    String prefix = "/public-diagnostic/" + marker + "/";
    return new StorageRootLayout(
        Path.of(prefix + "asset"),
        Path.of(prefix + "transfer"),
        Path.of(prefix + "backup"),
        Path.of(prefix + "log"),
        Path.of(prefix + "artemis"),
        Path.of(prefix + "staging"));
  }
'''


def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def inputs():
    normal=data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    before=(snapshot/TEST).read_text();assert data.sha(before.encode())==normal['begin']['inputHashes'][TEST]
    return normal,before


def intended(before):
    assert before.endswith('}\n') and before.count('@Test')==2
    after=before.replace('import static org.junit.jupiter.api.Assertions.assertEquals;','import static org.junit.jupiter.api.Assertions.assertEquals;\nimport static org.junit.jupiter.api.Assertions.assertFalse;',1)
    after=after.replace('import java.util.Map;','import java.util.List;\nimport java.util.Map;',1)
    after=after.replace('PT-OPS-OBSDATA-001/002:','PT-OPS-OBSDATA-001..004:')
    return after[:-2]+ADDITION+'}\n'


def emit():
    _,before=inputs();assert (data.ROOT/TEST).read_text()==before
    after=intended(before)
    return '*** Begin Patch\n*** Update File: '+str(data.ROOT/TEST)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n*** End Patch\n'


def main():
    invocation=capture(__file__);assert not OUT.exists();normal,before=inputs()
    after=(data.ROOT/TEST).read_text();assert raw(after)==raw(intended(before))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=TEST)
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2346_公開値診断・null契約二追加_単体テスト仕様書.md'
    assert all(v in spec.read_text() for k,v in GOLDEN.items() if isinstance(v,str))
    verify(invocation);OUT.mkdir();data.write(OUT/'golden.json',GOLDEN)
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=[dict(path=TEST,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()))],originalMethods=2,newMethods=2,expectedMethods=4,newTestIds=['PT-OPS-OBSDATA-003','PT-OPS-OBSDATA-004'],independentGoldenSha256=data.sha((OUT/'golden.json').read_bytes()),specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),goldenBasis='PRIOR_2346_PGD745_INTERNAL_FIXED_DIAGNOSTICS_PLUS_SS351_10_2_CANARY_NONDISCLOSURE_AND_352_12; NO_PRODUCTION_METHOD_EXPECTED_GENERATION',newMissingFieldVectors=7,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,actualSecretCount=None,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
