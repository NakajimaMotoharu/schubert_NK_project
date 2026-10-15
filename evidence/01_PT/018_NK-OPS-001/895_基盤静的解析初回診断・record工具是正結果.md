# 基盤静的解析初回診断・record工具是正結果

894/公開`evidence/provisional/PG3388-static-diagnostics/manifest.json`。**F03未合格、全体の正式認定不変更**。Production a9/PG2802/Main/resource/POM/設定変更0、成功済み3706全回帰・VM/業務操作の反復0。

PG3382真正observer0、2026-10-15 13:40:32.217602～13:40:52.231167Z。全849Javaはa9と3372input双方同hash、全六Jar1643Mainは元全3706のclass hashと一致し依存Jarまで固定。PMD実exit5/2220指摘/処理error1、Checkstyle実exit133/645指摘。これは合格ではない。規則categoryを広く診断したため、thread使用禁止等のEE向け規則、承認済みPOSIX octal、record field/accessor同名、固定電文TSV内tabなどが含まれる。2220/645をそのまま業務障害数とも、分類なしで0とも扱わない。各具体指摘の規約/承認契約への適用性・必要な是正は残作業。

## BUG1298/YKT1064 の有限是正

先行eac6bb103。PMD公式7.28.0 ruleの`ASTVariableId`から`ASTFieldDeclaration`祖先への無条件firstOrThrowが、record componentで失敗した。GateRecordはjavac25 `-Xlint:all -Werror`0で合法、公式PMD exit5/内部例外1を再現。正常Java25 constructorと異常catch/命名/空statement、通常mutable static fieldを別fixtureにし、Productionの期待値を使わず比較した。

修正はGit外の一rule class overlayだけ。公開modifier query `varId.isStatic()`で通常fieldとrecord componentを扱う。明示property checkNonStaticFieldsとその他rule logicは不変。overlay classはfinalとしてこの隔離tool内で派生を許さず、公式constructorの外部override可能性によるjavac25 this-escape warningを生じさせない。全category/ruleを有効のままにし、正式vendor Jarは書換えない。

PG3384 v1は新canary作成中のassertion失敗（正常fixtureのfield/accessor同名、負fixtureのignored名が空catch許容条件、PMD実rule名の誤認）、原report保全/成功加点0。v2 beforeはactual0、正常0/負PMD二指摘・Checkstyle二指摘/record error1/実singleton指摘1。v3 after actual0では全同fixture hash・同既指摘を維持しrecordだけerror0になった。初期overlay compileは全言語distribution classpathの他言語manifest古版参照warning、次に公式非final constructorのthis-escape warningで拒否しclass未生成。release8試行もwarningで拒否し不採用。最終は必要三Jar・final overlay・release25/full lint/Werrorで0。Production warning抑止なし、失敗attemptを成功扱いしない。

PG3386真正observer0、**PMD実exit4/2220指摘/処理error0**。全849source/全aux Jar/規則が前後同hashで、元2220のfile/rule/行/message tupleが全件完全一致。record以外の指摘を失ってerrorだけ隠す対策ではない。全sourceを再解析したため同構造recordも含めた対象集合に処理errorがなく、通常mutable fieldの再発防止canaryを維持した。BUG1298/YKT1064をこの有限工具scopeで閉鎖可能。2220指摘の分類・Checkstyle645・F03受入・正式451は未完。

## 固定toolchain・再現

JDK25.0.4+7 Ubuntu、既aru Linux7.0.0-38-generic/amd64。公式HTTPSから取得しGit外`work/toolchain/static-gates-20261015`に配置:

| 対象 | 版・SHA256 |
|---|---|
| PMD distribution | 7.28.0 / f974ba571f7bc01c73fffe11bade25fbc1f438698f9e9c00e416e8d65e9fbac2 |
| Checkstyle all Jar | 14.3.0 / 754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2 |
| 公式rule source | 8255ce3d51668fed128936e9ba6037c25b1988258d6b43dd105e938cae2ac314 |
| 修正rule source | 5758f89f86f3ebaab1b256023819fb21708eeaaf78808707468ea0a242e20c58 |
| 修正class | 91c6fb28937e0877e754e503cfe49e927470ffc130dbfc8b823bbcc5c96e0f15 |
| 一class overlay Jar | 4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c |

入手先はstatic/READMEの公式release、rule sourceは`https://raw.githubusercontent.com/pmd/pmd/pmd_releases/7.28.0/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule/multithreading/NonThreadSafeSingletonRule.java`。保存した公式source hash確認後、`patch -p1 -d <new-private-source-dir> < tools/quality/static/pmd-record-1298.patch`、修正source hashを確認する。固定JDK25 javacで`--release 25 -Xlint:all -Werror -cp <pmd-java-7.28.0.jar>:<pmd-core-7.28.0.jar>:<checker-qual-3.55.1.jar> -d <new-classes> <source>`。Jarは固定date `2026-10-15T00:00:00Z`で当一classだけを収容し、PMD実classpath先頭に置く。CLIのPATHは固定JDK/binを先頭へ（JAVA_HOMEだけの最初の版照会exit2は不採用）。公式Jarとoverlayのhash・由来を混同しない。

公開manifestに元/after manifest SHA、全Main source SHA、rule/tool/report SHA、canary実値、未認定、実private locationを格納。raw XML/log/compile artifactは私有場所に保持、master/秘密/実keyは公開しない。新JUnit/ProductionPT加点0、個別受入増分0、正式1964PT/53scope・工数null・QA051final保留を維持。
