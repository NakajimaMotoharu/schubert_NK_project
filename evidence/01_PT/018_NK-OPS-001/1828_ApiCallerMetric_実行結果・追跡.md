# API caller metric context PG・独立単体テスト結果

1827/PG-D622/group2057、Production `0f065c63fe1667e014fa4b985579d4146c3d91c5`（未配備）。新Main0・変更Main2/API Unit2。新APIPOOLB011～015/APIMHTTP021=6、必要既30、actual36/2全F0-E0-S0、normal skipTests六Jar成功。ApiProcessMain.main/run/default/start/DB/nativeは実行しない。

|工程（公開provisional配下）|SHA256|
|---|---|
|PG8854-api-caller-metric-six-compile-v1/manifest.json|7aa656748674bd692a4d6132bff0c60e3470f70435f556b750eb67fc64aa0ba1|
|PG8856-api-caller-metric-host-v1/manifest.json|bc2fc81f9242c82740c860550d7f1cde6587f728e9190c6f5b472ba26f51d5c7|
|PG8857-api-caller-metric-context-v1/manifest.json|ed206b2c857cd2af485487d3f81e0e4a7ec46ac57d35bb4026c12b3d3d43564b|
|PG8858-api-caller-metric-post-v1/manifest.json|05b78b6b1236e1383aa4ae6bc5a9212cb818eb4c73f959f531446133a9a2dc23|
|PG8859-api-caller-metric-static-v1/manifest.json|d230ac886953afcfa82fc3b6c78c766263d52d731e4d3c71cef0027d128b358a|
|PG8862-api-caller-metric-fixed-trace-v1/manifest.json|0ec61b72ac1bbdf7935050b8e15aee69de5f13c95112df58ee87af79734f6e39|

環境Linux/JDK25.0.4/Maven3.9.12/offline/dev-foundation。開始終了UTC、OS/JDK実値、command/exit、archive/source、全inputs/六Jar/SDK/fixture/tool/XML/log/exec hashは元manifest。8856 own JVM元XML36を照合、fixture outer ObservationTestはcompile-onlyで既8@Testを実行・加算しない。旧source/exec/4222確認再演なし。

## 独立期待・同source実測

STDはsupplier未読、固定ready literal/空bindings。null/未知modeは境界で拒否。DEBUGではcaller捕捉後pool→config各一回、initialize時getter未読、renderで四値3/5/2/8→0/0/4/8、再取得なし。両supplierのRuntime/Error/nullは元identity又はnull契約拒否、後段getters/自動再init/偽成功なし、partial SDKはcaller close。HTTP memory二GETは200/ready1/active3→0/max8、UTF8独立byte長/content-type/no-store/exchange close一回を確認。期待はliteral/明示順序・例外identity/HTTP定数で独立、productionをexpected生成に使わない。

当Binding/collector/HTTP三Mainでline58/58・method11/11・class3/3・branch8/8、全100%。CRC不一致0、session一つPG8856-API-CALLER-METRIC、Checkstyle0/SpotBugs0/processing0。collector既raw PMD三rowは保持し7372原cf76bd87のsource/rules同byte理由とcurrentPOOLB005/006/010 XMLを結合、未分類0/適用違反0、suppression/coverage union/除外追加0。8858の三Mainだけの資格であり、全1834/Context全体/callerのcoverageではない。

## caller PGと未実施動的品質

ResourceScope明示型でresource-free contextを先に捕捉し、initialize後に既managementへ借用供給。既management start/consumer/promote/await/finally lifetime.stop/groupsfalseの本文と全startup diagnostics、readiness/fatal tailは旧sourceとtoken同一。releaseは既ownedRelease(true)、managementが終了未確認なら既nonreturning keeperに留まりcontext/外側資源の解放へ進めない。Hikari7.1.0実M2 public署名と既PoolFactory返却型をread-only確認し、supplierは既DataSourceのtyped bean参照のみ。型castのactual startup/stop/deadlineは未実行・coverage null/UNRUN_HOLD、PT免除を申請・計上していない。

caller8859は**静的exit1**、Checkstyle0/SpotBugs0、PMD raw2/processing0。line90 main・line321 fatalのDoNotUseThreads（J2EE前提）で、当groupでは未分類2として保持し、合格やglobal F03解決へ読み替えない。実dynamic/manager raw40・必要契約19 currentXMLjoin/実pool取得・全catalog/全451/CHR/nativeは別未完。

8862は全1834physical中API Binding/caller二つだけ変更、旧1832同byte、原1669中1666同byte（歴史原本の二manager＋今回callerは異なる）。旧owner227を保持しcaller初登録一行で228、変更四source/当scopeの実bytesを結合、五architecture edge0、旧Binding10/HTTP20本文不変。caller四＋factory三のprotocol反例とowner欠落/重複二反例を拒否した。metadata検証は製品PT追加0、dynamic成功ではない。

## BUG1720/YKT1471と計測

元8860は旧owner集合にcallerも含まれると誤認しdelta包含assertで終了1、公開PG8860-api-caller-metric-trace-failed-v1/manifest.jsonと原toolを保持。修正前起票後8862で既登録更新と新規一行を区別、全228行の一意/実hash/欠落反例・1834物理/二差分/旧試験本文保持・五edgeを検証した。Main/期待/36XML/coverageを変更・再演せず、既8848はADDED集合が明示され非該当・成功確認再演なし。修正commitは本1828と同commit、完了2026-10-25、tool限定CLOSED。

開始3/6/10pp cap10、fresh46残54→終了fresh46残54/reset1793382075（共有丸め0≠専有0）。usage6f8e71a3060d13124aba1e4e8f55e3211d8bcb6c1728d6d57e4e349090d6f2bb/02:02:03→02:32:25JST、explicit新record0・完全性未証明、N/T/専有費/工数null。原/v4/v5/開始値・PG追加依存/工具手戻り1720を分離する。技術新606→612TestIDs/新Main33不変は異source部品累積、原190新受入0/歴史17/正式1964-53/QA051final/PTALT0は不変。

own22409/99129/32145/58552は各0、49315は静的1の元終端回収済、trace8860は元1/後段UNRUN。次8864公開scan/保存push→同Web callerの許可PG/通常metadataPT。実VM/Root/cohort/native/DB/Backup/鍵/intent/permit/配備・拒否未特定操作はHOLD、stash7/原Scenario3/Currentbaseline/原本等不変更。通常小区切りで停止せず継続する。
