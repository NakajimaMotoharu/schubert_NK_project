"""Close measured public boundary gaps using independent null/type fixtures; leave Main and old tests intact."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';pkg=r/'program/characterization/tests/java/dev/codex/schubert/characterization';e=b/'evidence/PG30758-common94-independent-boundary-source-v1';assert not e.exists();e.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
post=json.loads((b/'evidence/PG30756-common91-v4-independent-whole-source-post-v1/manifest.json').read_text());assert post['originalMavenExit']==1 and post['tests']==91 and post['positiveMainCrc']==10 and not post['wholeScopeFour100']
spec=r/'evidence/01_PT/020_NK-CHR-001/027_common実測六分岐不足・初全九十四仕様.md';assert not spec.exists()
spec.write_text('''# Common実測不足6branch/1lineの必要PT

PG30752/56 Sourcecf868の元91/FES0・Maven真正1/coverage不足を保持し再確認目的で再演しない。全5Main/10physicalは変更せず、元仕様027ではなく024～026と開始.85/2.55/5.1、改訂1/3/6cap6を保持する。以下は同群normal.4/1.2/2.4内の不足消化、内訳.02/.06/.12（専有実費ではない）、新gross0・上限変更0。

PT-CHR-HASH-NULL-001: GateCli.sha256(null)はIO前にIllegalArgumentException/固定hash source is required。
PT-CHR-BASE-NULL-002: GateContractValidator.sha256(null)、validateBaselineMetadata(null,{}), ({},null), (null,null)はそれぞれ固定hash source is required又はbaseline metadata document is required。NPEをcatchしない。
PT-CHR-DEF-012: contract.browser.browserRevisionのnull/text/2^31は、同値coercionやwrapを許さずBROWSER_REVISIONを含む診断。BigInteger2147483648/text1187は独立literal、productionでexpected生成しない。元resource変更0。

追加wholeJUnit3、GateCli13/Contract9/Definition12、他class7は同じ全件。全10class94を同source/一exec/全静的/四counter/実Code差/CRC-init/XML/owned終端で検証。実施前にsource固定、新v5専用namespace一回用・元v4変更0。新製品Main0/旧source成功合算0/正式1964-53/元190加算0。実経路・native・DB・Root・Actual4・aru等HOLD不変。PG30756の既定method166対実Code202の差も引き継ぎ、global451は承認しない。
''')
snippets={
'GateCliTest':'''  @Test
  void hashRejectsNullSourceBeforeIoWithFixedDiagnostic() {
    IllegalArgumentException failure =
        assertThrows(IllegalArgumentException.class, () -> GateCli.sha256(null));
    assertEquals("hash source is required", failure.getMessage());
  }

''',
'GateContractTest':'''  @Test
  void baselineMetadataAndHashRejectNullBeforeIoWithFixedDiagnostics() {
    IllegalArgumentException hashFailure =
        assertThrows(IllegalArgumentException.class, () -> GateContractValidator.sha256(null));
    assertEquals("hash source is required", hashFailure.getMessage());
    for (JsonNode[] input :
        List.of(
            new JsonNode[] {null, JSON.createObjectNode()},
            new JsonNode[] {JSON.createObjectNode(), null},
            new JsonNode[] {null, null})) {
      IllegalArgumentException failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> GateContractValidator.validateBaselineMetadata(input[0], input[1]));
      assertEquals("baseline metadata document is required", failure.getMessage());
    }
  }

''',
'GateDefinitionDocumentsTest':'''  @Test
  void expectedBrowserRevisionRejectsMissingTypeAndIntegerOverflow() throws Exception {
    for (JsonNode invalid :
        List.of(
            JSON.nullNode(),
            JSON.getNodeFactory().textNode("1187"),
            JSON.getNodeFactory().numberNode(new BigInteger("2147483648")))) {
      List<JsonNode> input = fixture();
      ObjectNode expectedBrowser = (ObjectNode) object(input, CONTRACT).path("browser");
      expectedBrowser.set("browserRevision", invalid);
      assertContains(input, "BROWSER_REVISION");
    }
  }

'''}
tc=r.parent/'toolchain';fmt=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];proof=[]
for name,snippet in snippets.items():
 p=pkg/(name+'.java');old=p.read_text();assert old==subprocess.check_output(['git','show','cf868540e7e461dc1809e4f0b7a677ccddeed168:'+str(p.relative_to(r))],text=True);(e/(name+'.before.java.txt')).write_text(old)
 assert snippet.split('void ')[1].split('(')[0] not in old
 p.write_text(old.replace('  @Test\n',snippet+'  @Test\n',1));subprocess.run([*fmt,'--replace',str(p)],check=True,capture_output=True,timeout=30)
 current=p.read_text();assert snippet in current;assert current.replace(snippet,'',1)==old
 proof.append(dict(path=str(p.relative_to(r)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=sha(p),allOldTestsByteInverse=True,newJUnitDefinitions=1))
closure=json.loads((b/'evidence/PG30718-common91-whole-source-closure-and-independent-inverses-v1/manifest.json').read_text())
for name in closure['allSelectedMainPaths']+[closure['fullTestHelperPath']]:assert subprocess.check_output(['git','show','cf868540e7e461dc1809e4f0b7a677ccddeed168:'+name])==(r/name).read_bytes()
paths=[str(pkg/(name+'.java')) for name in snippets];commands=[]
for label,args in [('format-source',fmt+['--dry-run','--set-exit-if-changed',*paths]),('checkstyle-source',[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(e/'checkstyle.xml'),*paths])]:
 with (e/(label+'.stdout')).open('xb') as out,(e/(label+'.stderr')).open('xb') as err:code=subprocess.run(args,stdout=out,stderr=err,timeout=60).returncode
 commands.append(dict(label=label,command=args,actualExit=code));assert code==0
closure.update(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),previousSource='cf868540e7e461dc1809e4f0b7a677ccddeed168',proof=proof,normalCases=94,newJUnitDefinitions=3,allOldTestsByteInverse=True,main5AndWholeHelperUnchanged=True,sourceOnlyCommands=commands,normal94NotExecuted=True,formalAccepted=False)
(e/'manifest.json').write_text(json.dumps(closure,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newJUnitDefinitions=3,expectedWhole94=True,main5Unchanged=True,oldTestsByteInverse=True)))
