# ApiPolicy閉鎖fixture所有・承認catalog接続 製造単体結果

2026-10-28 / dev-foundation / source `2baca5740741adb7c676cb85a83f15d19de01083` / PG-D758・759 / BUG2000・YKT1748 / 原2379・是正2381 / RD・UI・SS351参照は原Test IDの対応を継承。主費F03、両Test canonical owner/cost P018-09。原2/5/8pp・cap10は不変、追加発見一と必要source再認証を分離、旧639の成功を移植しない。新Test ID・個別受入増分0。

変更はApiMetricScrapeTest.apipol008の同一Compatible TWR外囲み一件だけ。最初のclose、閉鎖後STD未読・空、DEBUG拒否、reads0/isClosed、他全method/独立golden/oracleを元全token逆・非同値八で確認。Main/他Test/POM不変更。比較対象generic018は元finallyで同objectを閉鎖し非該当、ReadyFileInspector/native/actualTransferCleanup等のHOLDは対象外・未実行のまま。

| 証拠 | 真正結果・SHA-256 |
|---|---|
| PG12790 ownership plan | 0、八負例、0678f561228d431c3af13dc3a91939c13424969827d0ce0e98fe36045b3c7f56 |
| PG12792 normal | session65848、0、六jar、PT0・skippedはPASSではない、c1b8967f460264fae3194e799ed8f486711472c36b142ad28f0ae05dfd978d85 |
| PG12794 whole38/2 | session72446、0、F/E/S/aborted全0、一exec PG12794-APIAPPROVED-JP、87b3bb03310bcfa1b7b1b4d37912308c82553bf39e7df636e3ded69c10030d51 |
| PG12796 static | session2268、1、PMD raw3→2・processing0/CS0/六SpotBugs0、1dc9a5c49dea77b9801b3a8c3c1beffaf849d0c0d5e16f78f98ee14b73ae39e0 |
| PG12798 independent | session7109、0、b20fd41e7bbd0ca35b2bf110b65fb6a4918da18566d3d71a6e041a45c1ba7240 |
| PG12800 contexts | 0、Thread二歴史refの現source再束縛、新分類0、d434f64a0a860a9c5fc2ab11bcbbeb2dfc91783f468585d7a515776b1904c87f |
| PG12802 context post | 0、原XML位置/全method/所有/22反例、668d70434fc0b258dcbc13d9237d9e761943404acfdfa7e3c14a110519954153 |
| PG12804 trace | 0、原983の当Test一SHAだけ更新/他982同一、f595af6aa0bb60875d61573bc6de8ff0bef98e0d8dfb5b9ab7761fff4cc7f178 |
| PG12805 trace post | 0、六反例・全WBS前後同HOLD1、15dbc1310f348747cdfe604858b1b01f63feacadf66781d17d818b3138950278 |
| PG12806 delta | 0、原PMD-01968一件だけ是正、4dea940beb157c9538740ad41ee73ce66488ef0cab9e9d9c9a8ad8f270cf8aee |
| PG12808 delta post | 0、十一反例、603fac98230b398b7fecb2484ca70ebd974ee6bf57422f00d3d746d924621292 |

Manifestは `evidence/provisional/PG<上表番号>-*/manifest.json`。実commandは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg<番号>_<対応entry>.py`、完全argv/開始終端日時/JDK・SDK・工具hash/OS/source input/依存hashは元manifest。Linux/JDK25.0.4/Maven3.9.12/Jupiter5.13.4/JaCoCo0.8.15/PMD7.28/CS14.3。元639の12784・12786 actual38成功・12788 raw3/gate1は2380の別source中間証拠として保持し、新source38へ算術合算しない。

独立XML/summary/入力hash/全Main1843同byte・全Test1962のうち当Test outer/inner九physical差/他1953同byte、SourceFile・Code/debug reader三正常四異常、26既読Mainと二Testの外側28型唯一定義、許可外probe0/JDBC-Artemis load0を確認。新Main変更0、単一exec・空CWD、人工呼出し/手動除外/filter変更/旧exec union0。

ApiDurationMetricExporter四counterは **87L/10M/1C/48B、全miss0**。元未実行scrapeApproved5L1Mとcatalog-present1L1Bが同execで閉鎖した。全10method detailにもmiss0、branch0/0はNA。SDK/JDKの暗黙故障・全例外注入やfixture全分岐の証明とはしない。完全API467 artifactではcovered592L89M28C183B/missed12147L1753M337C4639B、Protocol176ではcovered182L27M7C40B/missed3298L716M152C974B、他Web358/Batch645/Storage80/Bootstrap117のcovered0を保持。旧source Context66・Alert14等の成功は合算しない。全artifact/451 coverage100は未達。

Thread二（PMD01969/01970）は自己JVMのBundle SDK registryと四worker/64有限callback。Futureごと10秒、TWR reverse close、元assert保持。TWR自体に局所絶対期限は無く外JVM240秒と区別、SDK memory以外の通信/業務process/VM/Root/DB/FFM/native/鍵/権限操作0。raw2/gate1を抑制せず、歴史refと現在method/実caseで適用性を記録した。閉鎖fixture01968は歴史ref/pendingにも存在したため現集合から一件だけ除き、原履歴は保全する。

現source導出 raw8472（Main1505/Test6967）、累計是正945、context refs3178/pending827/未参照5294、追加raw八保持。全静的解析の確認再演0・actualViolationCountはnull。BUG2000/YKT1748は当scopeの再発防止負例と正常38まで限定完了、全F03/451/正式1964PT・53scope/17受入・190総数/工数null/QA051final/HOLD不変。製品試験失敗0、実装工具不備0。trace patchの標準出力容量保護二回はapply前停止し、同じ生成patchをapply_patchへ直接渡して正常反映、製品試験再演なし。保存commit/pushは456に記録する。
