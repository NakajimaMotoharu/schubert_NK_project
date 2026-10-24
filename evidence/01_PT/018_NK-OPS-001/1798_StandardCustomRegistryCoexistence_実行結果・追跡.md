# 標準SDK/custom同registry共存 実行結果・追跡

1797/group2024、NK-OPS-001/RD171/UI252/SS311351/411451。Production **e81adb96849e4067beb12f212350ab4fbd4b1998**/全src/POM変更0、正常8608原4033792bの全input byteを確認し再build0。新APICOEX/WEBCOEX/BATCHCOEX各001～002＝6/3だけをtools-side fixtureで実行、旧26/API13/4222の確認再演なし。

|元証拠（evidence/provisional配下manifest.json）|真正結果|SHA256|
|---|---|---|
|PG8620-metric-coexist-host-v1|新6/3 F-E-S0、一exec、独立full-wire golden/各role実registry/SDK|00b9ad51fb25eca782aa0b1c17cc75431e8cc49d84bce8a66dfa9aff076b7479|
|PG8622-metric-coexist-post-v1|同source/全input-tool-deps/全XML/原log/exec・実session1/実env/七metadata反例|9d708e66c780c5ec893764518649908f02ba4d327b6c15f7977161b6f3d6c4d6|

標準→custom、custom→標準の両順で、APIは同ExactDuration registry/Webは同OverflowSafeHttp registry/Batchは同Simple registryを使用。custom gauge7.5/counter2.5、更新後9.5/3.5の全文literalが一致し、JVM-GC-CPU-FD標準metricが業務custom電文へ混入しない。STANDARD空/DEBUG値、GC handle一個/標準JVM gauge/独立Runtime CPUcount、借用registry未closeを確認。期待をproduction formatterや前回scrapeから生成しない。GCはcallerがregistryより先にclose、BundleとreachabilityFenceで供給arrayの寿命を確保。

実JVM出力: **25.0.4+7-1-26.04-Ubuntu / Linux / amd64 / 7.0.0-38-generic**。元command/環境/branch/source/時刻/exit/fixture/全hash/XML/exec/logは原manifest、postのactualEnvironmentとredactedJvmOutputにも実worker値を結合。許可list以外の三SLF4J初期化warning行は公開抜粋から除外し、元全log hash/省略行数を保持。warningを失敗の隠蔽や正式logging受入に使わない。

JaCoCo0.8.15の固定core（前8612のreaderLibraryHashesと同byte）で原execをmetadata読取、実session **PG8620-METRIC-COEXIST一件**を確認。readerのforeign session期待は終了1で拒否し、同exec hash不変。これはmetadata工具反例で製品PTへ加算0。Probe classpathは自身とcoreだけでtarget Main初期化0。own88100/77768は真正終端0/回収、新BUG/再試行0。

新Main0/変更Main0、coverageQualified=false/staticQualificationAdded=false、既counterの別source/exec union0。全physical1823/既src owner203の前群資格は別証拠として保全し当6の全体coverageへ流用しない。新fixture ownerはtoolsのrole固有三classで、431/1797/原testSourceHashesに対応する。原本/DB/Backup/鍵/VM/Root/旧process/network/service/配備/intent/permit操作0、Batch BACKUP_DBはラベルだけ。

開始fresh38残62/1-2-5pp/cap10→終了fresh38残62/reset1793382075、共有丸め差0は無料/専有費0ではない。前群の最終観測37→当開始38の間隔は共有不明費で後付け割当0。usage55044c1d/20:13:47JST/明示0/完全性未証明・N/T/専有費/工数null。1759以降技術371Test/Main22は異source集計で正式/coverageへ合算0。元-v4-v5/欠測/formal1964-53/原190新受入0/QA051final/PTALT0/whole451/CHR/F03Root11/全actualHOLD維持。

次はC07の現artifactと残る実装/接続を限定棚卸しし、普通の起動/Root/VM/endpoint HOLDに依存しない具体PG/PTを選ぶ。成果受入と着手可否を分離し、未確認provider供給/standard text/実endpoint/IT-STを受入済みにしない。通常小区切り/報告で停止しない。
