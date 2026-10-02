# NK-OPS-001 API管理ready・所有寿命（PG421、未認定）

2026-10-02。Program NK-OPS-001/MSG-001/ASY-001。対象ApiProcessMain.startNative、ApiProcessLifetime、ApiManagementServer、ServiceStartupAdmission.Ready/ReadyOnce、StartupReleaseManifest.publicInformation。RD SYS002/004/OPS009/MQ003/006/010、UI212213251253、SS312321342 §5.2/343、SSC158、PG-D334。正式run24/48.3%を変更しない。

| Test ID | class/method・入力/操作/fixture | 独立期待値・根拠 | 観点/実行状態 |
|---|---|---|---|
| PT-OPS-API-READY001 | ApiManagementServerTest.ready001・独立5値literal、loopback実HTTP/ephemeral port、promote前後health/metric/info | DOWN503→release callback終了後UP200→health不良DOWN503、infoは5値literalのJSONだけ、未知route404/POST405、cache no-store。SS342固定契約 | 正常/境界/非公開route/idempotent close、未正式 |
| READY002 | ready002・開始前health不良/解放IOException/解放中stop | release回数0/1/1、全てDOWN、再promote不可。A解放だけでUPを作らない | 異常/競合/再送、未正式 |
| READY003 | ready003・null map/health/value、欠落/未知key/不正commit/version、実port二重bind | factory前拒否、IOException collision、正常serverに影響しない、secret露出0 | null/欠落/未知/境界/例外、未正式 |
| READY004 | ApiProcessLifetimeTest.ready004・独立header/event/actual count4、3borroweddelegate/stop | 元event/metadata identity、呼出3、stop後新処理0/Temporaryでrollback対象、借用providerをcloseしない | 正常/停止guard/null、未正式 |
| READY005 | ready005・健康喪失/interrupt/通常stop/同owner shutdown | fatal IOException非成功・interrupt保持、通常stopだけ正常、自己joinなし | 例外/停止/health境界、未正式 |
| READY006 | ready006・別thread hook/interrupt/outer close＋実Runtime hook install/remove | outer close前hook復帰0、後終了・interrupt復元、close冪等。Native admitを人工生成しない | 並行/資源所有、未正式 |
| READY007 / RELEASE009 | StartupReleaseManifestTest.release009・独立JSON/BOMfixture/独立JCE SHA256、保持FD reader/期待digest差/改変release/構文異常 | 5値Map literal/immutable、hash同一のみ、他release/不正JSON拒否、全FD close。expectedをProduction readerから生成しない（不正fixture拒否用digestのみ読取） | 正常/異常/差替/例外、未正式 |
| READY008 / STARTADMIT009 | ServiceStartupAdmissionTest.startadmit009・independent proof fixture、情報読取/解放/escape/IO故障/legacy情報port | proofの同hashだけ委譲、handoff前のみ可、handoff後/borrow寿命外拒否、情報欠落でもrelease0/全close | null契約/寿命/例外、未正式 |

Production APIは固定8091だけ。component ephemeral portとfixture proofはnative ready/Root acceptanceとして加算しない。Native対象は正規signedSource→Morning→Root→同PID ordinary API6consumer/本人8091/解放後UP→TERM→全kernel終端/whole cleanup marker、まだ未実行。外部mainの網羅を人工呼出しや除外で閉じない。

実行: Java25.0.4/Maven3.9.12/Node24.19.0/固定offline m2、選択Protocol/Storage/Bootstrap/API、MessageCodecTest/LinuxInodeSecurityTest/ApiNonSecretConfigTest/StartupReleaseManifestTest/ServiceStartupAdmissionTest/ApiManagementServerTest/ApiProcessLifetimeTest/ApiProcessMainTest、spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report。Work PG379/pg421-api-ready-selected-v1/v2.log。v1 Bootstrap compile失敗/API0PTはBUG494、合格へ加算しない。全coverage/静的/current-byte/source/hash/実行結果は成功後manifestへ記録する。incremental旧XML/旧execは正式evidenceへ混ぜない。

結合選択v8（2026-10-02 12:32:42 JST、PG379/pg421-combined-selected-v8.log）は4module 111PT（API68）/FES0/static4zero。READY003は実vendor started/setExecutor失敗→同port再bind/DOWN。BUG507の旧fixtureは移譲前例外による試験資源漏れで、初期診断をactual stack/JDK bytecodeで訂正した。READY006は実子JVMへOS TERM→終了143→whole-owner-returnedのliteral2行を確認し、test-only遅延captureで実Lifetime countersを保持する（BUG501502）。current-byte未網羅B/L/M/CはLifetime0/0/0/0、Management1/0/0/0。selectedは全scope受入ではない。Source固定後の全6fresh結果を別manifestへ保存する。

不足: native TERM143/cleanup receipt、普通generation socket観測、Morning同held原本complete、完成後restart/最終M不確定、全Source回帰/4coverage100/実CHR/正式collector。未検証は完了扱いにしない。
