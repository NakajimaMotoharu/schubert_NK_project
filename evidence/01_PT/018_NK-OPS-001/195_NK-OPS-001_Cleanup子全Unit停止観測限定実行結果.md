# 195 NK-OPS-001 Cleanup子全Unit停止観測・限定実行結果

実行日: 2026-09-28 JST。Branch `dev-foundation`、Production source commit `a1898417f`。対象は194のMTERM009、NCLEAN002～005、既存Root/Process/Preflight回帰。SSC-104/PG335、BUG-313/YKT-246を含む。ProductionのCleanup成功、実Unit配備、DELETE、親Morning、外部Web/API起動、実NK Characterizationは未受入。

| 検証 | 結果 |
|---|---|
| Batch限定 | `RootStartupContextTest`9、`MaintenanceUnitTerminationTest`9、`CleanupProcessMainTest`4、`CleanupPreflightTest`5、`CleanupNativePreflightTest`4＝31件 F/E/S0。Batch SpotBugs 0。全Unit観測factoryのJaCoCo line/method/class/branch missed 0。Native preflightはcovered line9/52・branch4/6・method3/13で未達。 |
| Production6 `clean verify` | exit1。Protocol80/Storage149/Bootstrap175はF/E/S0だが、Bootstrap bundle JaCoCo line/method/branch約90%で100% gate不合格。API/Web/Batchはこのcommandでは未実行。成功へ読み替えない。 |
| Production6限定全回帰 | 同一sourceで `clean test com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check org.jacoco:jacoco-maven-plugin:0.8.15:report` exit0。Protocol80、Storage149、Bootstrap175、API742、Web555、Batch626＝2,327PT/342suite、F/E/S0。6 module SpotBugs各0。これは`verify` gateの代替ではない。 |
| Bundle JaCoCo未達 | Protocol/Storageは4指標missed0。Bootstrap branch37/line11/method4、API1/19/3、Web1/19/3、Batch2/90/31（順にbranch/line/method）。全module class missed0。除外や期待値緩和なし。 |
| 実VM read-only観測（BUG-314訂正） | Ubuntu隔離VMの固定8対象はCaddy/Backup/Artemisのみloaded・inactive/PID0、Web/API/Cleanup/Inspector/Expiryはnot-found。別actorの正規`schubert-nk-morning-controller.service`はloaded・inactive/PID0だが、PG323のtest-only probe用oneshotでありProduction Morning候補ではない。当初の「Morning controller not-found」は短縮名を誤照会したため撤回する。既存Unitを変更せず、全8終端・Cleanup実起動・R2成功へ加算しない。 |

選択証跡 `evidence/provisional/PG335-selected/manifest.json` SHA-256 `8e047649303546dcf1c822fea2014b4c4c2b4f4c50d0b545539729521c1590a9`。全6限定回帰証跡 `evidence/provisional/PG335-six-security/manifest.json` SHA-256 `6683e402334adabb81b32fa78bf09d4f2af16af3062ad7b5f86883a861ad14dc`。後者はJUnitのsuite/case metadataだけ342 XML、coverage1、static6、要約1の350fileをhash再照合し、原始logはGit外のpath/hashだけをmanifestに保存。固定secret pattern scan hit0。環境JDK25.0.4/Maven3.9.12/Node24.19.0、実行command、終了code、source hash、期待/実際、coverage、BUG/SSCは各manifestに記載。

独立期待は194とSS341/343の固定WEB→API順・loaded/quiescent必須・既知停止異常の固定安全失敗30から導出。現行コードの返却値をexpected生成へ使用しない。194の入力・境界・異常・null・未知値を実施した一方、真正root・両Unit loaded/終了、親M/A、cleanup結果0/10、並行起動防止、後段DELETE直前fresh再検査は未実行であり正式PT完了に算入しない。
