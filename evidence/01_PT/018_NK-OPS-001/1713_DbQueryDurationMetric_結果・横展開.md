# 1713 DB query duration metric 結果・横展開

元API実行結果中のDBTIME001～009は `DbQueryDurationMetricRecorderTest` に限定する。現行の一意IDと各元XMLは[対応表](evidence/PG45500-dbtime-suite-identities-and-oracles/manifest.json)へ記録した。

1712/DBTIME001..008/PG-D568/group1934（開始event1934、手戻り1935）。当資格source `1540267d33d2cbe93b7d7ec9f917df78a54ac3be`。製造新8＋必要既API130を当138/17で実行し、別sourceの成功/coverageを算術合算しない。

| provisional原run | 真正結果 | manifest SHA256 |
|---|---|---|
| PG7830-api-query-duration-host-v1 | 元a2d/138中6failure・verify1、合格非算入 | 65f9a7feb8657d3e677864c8632034e105e30a628821fadc1dcd4fe5570800ee |
| PG7834-api-query-duration-six-compile-v1 | 元a2d正常六compile0/PT0 | 3b74904c55ab910160c2e5a7a593ca440374827321abc111b446939f33a6061f |
| PG7844-api-query-duration-host-v2 | 9e579/138中6failure・verify1、golden CDF通過後の補助label fixture失敗 | 34c9bfcb52e3810fc0e9a93e237b461c8b3114ec1467d91447fc93c31939cea0 |
| PG7848-api-query-duration-six-compile-v2 | 同9e正常六compile0/PT0 | 8cc2475224121bd4aa700724842baa4d4d0d398c9342e00f08b91b2aa9b2eaa3 |
| PG7858-api-query-duration-host-v3 | 当138/17・F/E/S/flaky/rerun0、verify0 | ba96519a4b8455d0d376a2a4929e1e0c5bd8fbcd9a556425b8a302a98cc2ea3e |
| PG7864-api-query-duration-post-v4 | 当34Java/実28＋metadata1・単一session/CRC0、L504 M95 C28 B241全miss0、SB-CS0/raw既16-新0 | e03a785b0e5c4ebcd047a4f52327b3616aeb4e018b3ae4f3f9f0657a53f03f2c |
| PG7862-api-query-duration-six-compile-v3 | 当正常六Main/Test compile-package/NullAway0、PT0/UNRUN | 59a8bc8de04e6199389bcbe090b9947c22d0310c8ebf054f98c53eb57935c5b0 |
| PG7850-api-query-duration-six-post-v2 | 全1777/元1669debug不変・当API29/歴史Batch65-Web14、三POM/SDK/五rule0 | 8e2a05cd0a1394594c4e6e8f6164f488bdd17190ed6882a2fed613ed9ffb3198 |
| PG7852-api-query-duration-trace-v3 | 全123delta-108追加physical、旧121不変2新、当28のみcurrent、元Step歴史転用0 | 1190a6b099334bcd2bd30c4cd199e27d97e00227b65efc64f2d1b51071843b28 |
| PG7854-api-query-duration-review-v3 | 生成既41＋新Query/Outcome4=45当ordinary/javap、全16raw個別理由/五domain負例 | c2748ccf8b1a824c21f67da3a9f7cf9b960e3511a8bd1f3f6f4135f81a149179 |
| PG7866-api-query-import-contract-v1 | 六現行工具AST/二負例/歴史誤参照拒否、ProductPT0 | 35b4ff6af54ae89d3d107c40375fcc78e91b4a2c01dc864571b1b10145151618 |
| PG7868-api-query-component-qualification-v1 | 当source/run/環境/spec/限定品質を統合、whole451更新0 | e43c00c7ef75189291f59a907728da7af80b284185b43f2fe38f3735bdc79c1b |

sessions3907/42903（v2失敗/compile0）・65946/81681（v3普通/compile0）・68069（独立post0）・12226（physical0）を元jobから回収、重複起動0。最初7830/7834は中断前の保存manifest・真正exit/XMLから回収し再演0。OS/JDK25.0.4/Maven3.9.12/SDK1.17.1/JaCoCo0.8.15/branch/開始実日時/全command/input/archive/XML/exec/counter/CRC/hashは各原manifest・7868へ結合する。必要な変更後回帰は同じ固定sourceごとに実行し、compile-only/metadata/レビューを普通PTへ加算しない。

二query×二outcomeのprimary Summary4と、SDK補助Gauge24（五le＋phi .95各6）を全量確認。独立0/1ns/0.5s/1.5s→count4/sum2.000000001s・CDF2/2/2/3/4、別fresh registryのMAX ns二回→sum1.8446744073709553E10 finiteを維持。null/負/MIN/STD未記録/閉enum、factory第2失敗のprimary1＋補助6・元Throwable同一/borrowed registry、record前後失敗とpartial増分、独立64vector/別owner・foreign Counterを検証した。期待値をproduction呼出しから生成しない。

BUG1676/YKT1427: fixed-boundary SDKが小数秒をceil→longにするMain選択不備をpublishPercentiles(.95)によるdouble histogram選択で是正。独立小数CDFは不変更、補助meter分母とSDK整数le「1」のfixture表現だけ別是正。修正Main9e579a97a/最終Test1540267d3、原a2d/9e失敗はGit b3c8e7449/6605c3a98へ保持。src全DistributionSummary/publishPercentileHistogram/publishPercentiles検索で当Main/Testだけが該当し全対象修正・再発防止済。他既Counter/Gaugeはdouble histogram非使用として非該当。p95の設定要求を、実exporterのp95精度/公開受入とはしない。

BUG1677/YKT1428: 7860は7846内の誤module参照（_v2欠落）によりimport時点exit1、post SLOT/manifest/JUnitなし。元工具d7a8fdfedへ保持。新7864は正しい7832.configureを直接呼び、既成功138/normal compileを再演せず結果検証。現行六工具のASTで全project import現物を照合、import/fromの二負例と歴史7846欠落を拒否。旧7846/7860は失敗履歴のみ・再使用対象外。新source/plain test成功を失敗原因調査や拒否再試行へ利用していない。

既32Java/26physicalとraw16全位置・属性は不変、前7700の全個別適用性理由を当普通138へ再結合し、未分類/適用違反0・抑制0を確認。生成既41は当既suite/同byte/同公式filter、Query/Outcome新4はDBTIME003のtyped値/配列分離/valueOf既知・未知・nullと非初期化javapへ結合し、四counterへ算術加算0。protocol176全byteも当正常Jarと実PTの固定依存が一致、旧M2stale/歴史coverage転用0。元1669内RepositoryStepを追加108へ二重計上せず、当APIのcurrent実行資格にしない。

開始3/5/9pp上限10、fresh8→8残92/reset1793382075。同窓丸め観測差0は無料ではなく専有N/T・工数null。旧markerlast27区間/共有累積null/元90再基底化0・原/v4/v5凍結値を維持。usage2194ce7（06:00:14JST、explicit0/観測完全性未証明）。製造新8・変更後必要回帰130、二回の試験手戻り/工具一回を区別し費用の新群付替え0。

当部品だけの限定閉鎖。実SQL/DB/時計/全業務query namespace/exporter/backend/実VM/Root/配備は未実行・HOLD、正式1964/53・原190新受入0/QA051final/PTALT0/whole451-native-CHR未受入。全src coverage100/PGPT工程完了とはしない。次はSS351の未結線を既artifactから一経路に限定し許可済み普通PG/PTへ継続する。
