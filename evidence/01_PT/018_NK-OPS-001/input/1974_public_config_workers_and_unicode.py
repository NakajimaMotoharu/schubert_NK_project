"""Before-compile two allowed Test worker fixes and a distinct independent UTF16 case; no Main edit."""
from pathlib import Path
import hashlib,json,re
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG28044-public-config-workers-unicode-before-style-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();triage=ld(B/'evidence/PG28038-ykt2387-first4-source-triage-v1/manifest.json');rows=[x for x in triage['reviewed'] if x['status'].startswith('ELIGIBLE')];assert len(rows)==2;pre=B/'evidence/PG28046-public-config-pre-style-before-v1/manifest.json';s=ld(pre);assert s['checkstyleFindings']==1 and len(s['rawFindings'])==3 and all(Path(x['path']).name=='PublicCanonicalAadValueTest.java' and x['rule']=='AvoidDuplicateLiterals' for x in s['rawFindings']);l=R/'documents/900_OTHER/910_台帳/915_障害表.md';h=l.with_name('916_横展開管理台帳.md');assert max(map(int,re.findall(r'BUG-(\d+)',l.read_text())))==2736;assert max(map(int,re.findall(r'YKT-(\d+)',h.read_text())))==2388
l.write_text(l.read_text()+'\n\n## BUG-2737（PT、2026-11-13、既PublicCanonicalAadValueTest通常style、修正前）\n\n対象PT-IDEM-PUBLIC001..008、重要度低/優先高。期待normal GJF/適用style/CS0、実際PG28046の既fixture GJF1・重複literal label/QSSRSP01/001三件・Assertions.* CS1。同六source中他Main四とWebConfigTestはprestyle/GJF/CS0で非該当。元全byte/hashをPG28046保全・Main/Test compile未実行。原因旧architecture fixtureとnormal規約境界。BUG2736 workerと新PUBLIC009を別mutationとして保持し、定数展開＋明示同classassertion import＋書式のみで前段全token一致/異値反例を条件に是正予定。YKT2389、費用は開始.375/1.125/2.25内数・追加枠0、Main/期待値を変えずfullRoot静的/通常16/独立postまでOPEN。\n');h.write_text(h.read_text()+'\n\n## YKT-2389（2026-11-13、元BUG2737、今回四Main＋二Testのprecompile style）\n\nPG28046 fullCS/二既style/GJFの全六source、PublicAAD三literal/star/書式だけ該当・他五は非該当。元六byte/hash保存、元Public8を含むworker是正後9の全tokenは三定数展開・同Assertions明示import除去で保持、異値反例を拒否する。WebConfig7はworker変更のみで元assertion保持。Main一切不変更、最終fullPMD/NullAway/SB/CS-GJF/全16/CRCまでOPEN、抑制・HOLDfixture部分抽出無し。\n')
extra=r'''
  @Test
  void public009MalformedUtf16AndFactoryMetadataFailuresKeepIndependentContracts() {
    for (String raw : List.of("\uD800", "\uDC00", "a\uDBFF", "\uDFFFz")) {
      var failure = assertThrows(IllegalArgumentException.class,
          () -> CanonicalField.text("label", raw));
      assertEquals("canonical text contains malformed UTF-16", failure.getMessage());
    }
    var textMetadata = assertThrows(IllegalArgumentException.class,
        () -> CanonicalField.text("/", "PUBLIC"));
    assertEquals("canonical field metadata is invalid", textMetadata.getMessage());
    var numberMetadata = assertThrows(IllegalArgumentException.class,
        () -> CanonicalField.number("/", -1));
    assertEquals("canonical field metadata is invalid", numberMetadata.getMessage());
    try (var field = CanonicalField.text("label", "😀")) {
      assertArrayEquals(HexFormat.of().parseHex("f09f9880"), field.value());
    }
  }
'''
O.mkdir();proof=[]
for row in rows:
 p=R/row['path'];assert sha(p)==row['sha256'];old=p.read_text();public=p.name=='PublicCanonicalAadValueTest.java';var='pool' if public else 'executor';workers=4 if public else 8;before='    try (var '+var+' = Executors.newFixedThreadPool('+str(workers)+')) {\n';after='    var '+var+' = Executors.newFixedThreadPool('+str(workers)+');\n    try {\n';assert old.count(before)==1;new=old.replace(before,after);imp='import java.util.concurrent.TimeUnit;\n';anchor='import java.util.concurrent.Executors;\n';assert old.count(anchor)==1 and imp not in old;new=new.replace(anchor,anchor+imp)
 if public:
  a='pool.invokeAll(tasks)';z='pool.invokeAll(tasks, 10, TimeUnit.SECONDS)';g='result.get()';g2='result.get(5, TimeUnit.SECONDS)';ending='        previous = actual;\n      }\n    }';fixed='        previous = actual;\n      }\n    } finally {\n      pool.shutdownNow();\n      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));\n    }'
 else:
  a=g='job.get()';z=g2='job.get(5, TimeUnit.SECONDS)';ending='      for (var job : jobs) assertEquals(config.canonicalSha256(), job.get());\n    }';fixed='      for (var job : jobs) assertEquals(config.canonicalSha256(), job.get(5, TimeUnit.SECONDS));\n    } finally {\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n    }'
 assert new.count(a)==1 and new.count(ending)==1
 if public:new=new.replace(a,z).replace(g,g2).replace(ending,fixed)
 else:new=new.replace(ending,fixed)
 inverse=new.replace(fixed,ending).replace(after,before).replace(imp,'')
 if public:inverse=inverse.replace(z,a).replace(g2,g)
 assert inverse==old
 if public:assert new.endswith('}\n');new=new[:-2]+extra+'}\n'
 assert len(re.findall(r'@Test\b',new))==(9 if public else 7);p.write_text(new);(O/(p.stem+'-before.txt')).write_text(old);proof.append(dict(path=row['path'],beforeSha256=row['sha256'],afterSha256=sha(p),workerSourceInverseExactBeforeAddedCase=True,allFormerAssertionsPreserved=True,futureGetSeconds=5,invokeAllSeconds=10 if public else None,finallyShutdownNow=True,awaitTerminationSeconds=10,wholeTests=9 if public else 7,newDefinitions=1 if public else 0))
assert all(sha(R/p)==x for p,x in triage['safeMainSourceClosure'].items());v=dict(actualExit=0,proof=proof,MainChanged=False,MainCompiled=False,allFormerAssertionsPreserved=True,newTestDefinitions=1,wholeExpectedTests=16,addedCaseIndependentInputs=['isolatedhighsurrogate','isolatedlowsurrogate','mixedmalformedtext','invalidnamefactorymetadata','independentUTF8emojiHex'],beforeStyle=ref(pre),inputHashes={x['path']:x['afterSha256'] for x in proof},productTestsExecuted=0,heldTestSourcesModified=False,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,workersFixed=2,wholeTests=16,newDefinitions=1,MainChanged=False,manifest=ref(O/'manifest.json'))))
