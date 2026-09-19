# NK-DAT-001 検査resource寿命 実行結果

2026-09-20 最新確定: dev-foundation/source 1d5b44ad26736366950936653914f67e7e096fe2、正式PT-WEB-20260920-03（02:01:07～02:16:34 JST、Maven15:26/exit0）、全1463件（Protocol80/Storage74/API660/Web241/Batch367/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3method限定静的レビュー・coverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと48負canary成功。DB29部品266＋Batch25部品281＋OPS15部品126＝69部分成果673 PT（全1463の内数）。今回9月19日再開比+48 PT/+4部分成果、PG184のroot検証・全4file照合からDB両step原子確定caller8PTを追加認定しSSC067限定完了。PG178～183のSQL資源905複合は既存Test ID内で新件数増算0。BUG195/206・YKT154/162・SSC063の別境界分類は継続。PG185試験並列化/PG186・SSC068 private子生成は仕様のみ。実archive/7世代/親実子制御/全cleanup/通常Question/Web/Logout/QA045/実NK互換gateは未完了、固定加重約4割（35～50%、456）を維持。利用枠残76%で継続、元dev-web3file保全、IT/ST完了ではない。以下は履歴。

正式coverageはSettings class1/method4/line19/branch12、Application class1/method3/line21/branch2、各missed0。共有Process/credential/reader/providerも同scope全counter missed0。SQL後条件END0/0/0と再開、破損暗号END1/0/1、backup欠落/接続不成立の非成功・進捗0、最後のroot close失敗時の結果非返却と確定済みDB再開、開始割込IO0・実FileChannel途中割込、64並行の独立全FD解放を確認。BUG134/135/YKT105/106は正式38で再試験完了。Current baseline/V001～016不変、既知秘密pattern scan0hit、検証sourceからsrc/pom/characterization/tools差分0。

再現は421の固定環境で`sh /home/mini/codex/project1/work/pgpt_foundation_verify.sh PT-WEB-20260909-38`（同ID上書き不可、再実行時は新ID）→終了0確認→017/019負canary→018全scope収集の順。完全command/OS/tool/commit/各Test ID期待・実際/source hashはmanifest/results.xmlに記録。main/unit/親OS/実backup gate・実root credential配布・実NK CHR・IT/ST・PGPT全工程の合格は含まない。以下は履歴であり、旧未確定表示を現在値と混同しない。

## 探索履歴（正式合格に算入しない）

2026-09-09/JDK25.0.4+7/Maven3.9.12/PG18.6、dev-foundationの未commit source。`/tmp/pgpt-inspector-application-explore-N.log`はlocal診断だけでrawログをGitへ転記しない。

| 探索 | 結果 |
|---|---|
| 1 | 18:01:23 JST終了1、22.426秒、新12件中11成功/1 error。開始割込が先行password IOで設定例外になったためBUG134/YKT105を修正前登録、SS343 §6.7補足 |
| 2 | 18:04:38 JST終了0、53.950秒、新12＋既存Process12/executor8/DB接続7＝API39件PASS、failure/error/skipped0。開始割込IO0・読取途中割込の実FileChannel失敗/closeも確認。依存Protocol5/Storage7は別集計 |
| 3 | 18:06:50 JST終了0、14.303秒、新12件全PASS、failure/error/skipped0。存在しない隔離DBへの実接続失敗も追加しSTORAGE_FAILURE/全root解放/進捗0を確認 |
| 4 | 18:17:09 JST終了0、18.595秒、新12件全PASS、failure/error/skipped0。明示Set.copyOf accessorでも入力/返却不変契約を維持。別途API単独SpotBugs診断はreactor内artifact未installの依存解決で終了1、解析未実施。診断は-amを付けて再実行し、正式合格と区別する |

対象2classは探索coverageのline/method/class/branchすべてmissed0（Settings18/3/1/12、Application21/3/1/2）。正式全体回帰と32scope/10collectorの照合前には合格認定しない。017の1件と019の10件の独立負canaryは成功、Java件数へ加算しない。

## 正式37・不合格

PT-WEB-20260909-37/sourcefb515378、2026-09-09 18:08:51～18:14:31 JST、exit1。API606 PTと4coverage100%は成功したが、SpotBugs EI_EXPOSE_REPがInspectorSettingsの自動集合accessorを1件指摘。Web/Batch未実行、collector未開始、工程合格へ算入しない。BUG135/YKT106を修正前登録し、明示accessorのSet.copyOfで外部境界を確立する。実変造成功ではなくhelper内部の不変化が解析に直接見えない問題であり、既存PT209の入力/返却変更拒否は不変更。

静的解析単独診断の再現注意: root aggregatorではspotbugs prefixを解決しない。固定完全座標でもlifecycleを通さない直接goalはreactorのstorage artifactを解決しないため、`-pl src/schubert-nk-api -am compile com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`とcompile段階を含める。先行した依存解決/prefix未解決はAPI解析結果ではない。正式gateは従来のroot clean verifyのままであり、解析対象や要求を変更しない。

18:19:45 JST、上記compile＋完全座標の診断は23.785秒/exit0、Protocol/Storage/APIのSpotBugs bug/error0。新sourceの実解析でEI_EXPOSE_REP解消を確認。YKT106検索ではSessionAttributes/ScenarioDetailSnapshot/CanonicalRequest/ProtocolのPayloadValues・TypedPayloadValues・LayoutFieldsはconstructorで直接copyOf、他返却点も直接copyOf、InspectorProcessは集合を返さない。全対象の最終回帰は正式38で再確認する。
