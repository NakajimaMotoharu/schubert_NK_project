# 620 当40ef：真正通常親・owned停止・native8（部分受入）

Program NK-OPS-001／MorningProcessMain、RootServiceLauncher、API/Web各ProcessMain、Caddy／Bootstrap／固定全scope。関連RD OPS009/TST004、UI251、SS341/342/343 SSC233/354/451、619。対象Production source40ef6e894573d2ffab1d1732124960f9c98d5f97、PG932 BOMb75e8bd5…・187/schema028。実source/operator/run/hashはmanifestへ一意対応、正式PT-WEB-20260925-24／1964PT／53scopeは不変更。

| Test ID | 目的・入力／独立期待値 | 実結果・証跡 |
|---|---|---|
| PT-DEP-957001 | 署名default noargs、実before全18/full24/full32、Production生成fresh tuple。一回予約先行、旧Rootへresumeしない | new eeae/091663ce/0bb4/213904、一回start0。619/954/957 |
| PT-DEP-960001 | SS343元1800内、PID1 start/DONEとRoot完全DONEの同run/activation/cutoff。GC/inactiveだけで成功にしない | 960 actual0、1547.000884s、endMono202927375873、before4e6f32d9…/complete899a4a76… |
| PT-DEP-961001 | Current独立golden A01、同Root→ordinary/API/Web親・socket/info・Caddy TLS200。DIF001 titleだけ | 961 actual0、baselineSHA df68edfb…不変、PASS artifact、cookie/token export0。他CHR/fullgate未実行 |
| PT-DEP-963001 | 現実proof960と所有四actorへ固定、M-A/専用DB/tenRef/保持FD/30秒pulse/全新scope正常、逆順TERM | freeze965 compile-Xlint-Werror/oracle0→966 stage0/stop0、29.749215s。旧143を正常化0 |
| PT-DEP-968001 | 独立停止前imageから全24不変/全32/署名187/tenkernel-actor-clientDB-advisory-flock0/原本Backup/metadata不変 | 968 actual0、2.663822s、八terminal receipts、native71physical安定、追加start-stop-reload-SQLwrite0 |
| PT-DEP-969001 | 単一module XMLとwhole-host/nativeを分離、同source/byte/run/session/window四counter、旧stream除外 | v1 actual1 BUG999（粒度混同）。修正43513768b共通template614、972-v2 actual0、八stream/classByteMismatch0。旧v1未完・失敗保持 |
| PT-DEP-973001～003 | 独立literal local/aggregate一行・一method差、全四counter変異拒否、source/hash/newslot | 973三case0、974の八subject十五case0・private log/hash保存。975transitive二case0、977再保存。Production PT加算0 |

正常/同日ALREADY/境界/例外/null/並行/再送は619・960Rootとhost926の独立PTへ対応。業務Cleanup SKIPPED（同日ALREADY）をframework skipped合格に読み替えない。Production未実装のprototype初回TDD失敗、960初回untracked-CHR clean-tree停止、969v1不一致を成功へ加算しない。

## Coverage：二baselineを区別

926 actual3560PT/523suite/FESFlakyNotRun0/static六0・module-local原XML（host残3799L630M40C1106B）を固定。全六execが共通classを実行したwhole-host baselineは3798L629M40C1106Bであり、1L/1Mはcross-module probe差、native実績ではない。このbaselineへ当八nativeだけを加え、追加2868L451M28C372B、残930L178M12C734B。全module-local/XML厳密一致・native全single session/time-window/byte mismatch0を確認。四counter100未達、全体正式受入ではない。

## 再現・環境・証跡

toolchain JDK25.0.4／既VM bootcc9／branchdev-foundation、各実時刻/command/source/exit/hashは公開manifest。OS versionは当操作でfresh測定しておらずnullとし推測しない。commands：961（A01）→960（actualgenuine）→965（freeze）→966 stage/stop（一回）→968（全post）→972（native-v2）。既起動/停止/公開を再実行しない。秘密原データ/execはWorkPG379とguest0700に保持しGitへ出さない。

公開manifest `evidence/provisional/PG954-975-current-genuine-native-v2/manifest.json`、private native hash043e7c88400840fd945512548c70a2d8dda2e53a6d9e2f6b5b5855bd0bab3d8b、974 hash9656747d5e9bd4bba006081cc14c37737e700795fc5d27124dc43dd40a435e21。関連BUG998/999・YKT767/768。次は当source Bootstrap existingADMIN/Inspectorの実native、Log/CHR（QA051最終L01保留）・全体四100/正式/引継ぎ。IT/ST合格宣言0。
