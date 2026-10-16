# 配置前inspectの限定回収とset型工具資格

Program NK-OPS-001、SS343/353/355・SSC296～298、QA047、BUG1363～1366/YKT1129～1132。Production候補964e/PG4432/BOM93807abdと全3721/545suite/1644Mainは不変更、配備current7bb/PG3976/BOM0a409301/boot79a。全回帰・署名・旧成功post・旧Unit操作を再演していない。

## 仕様と独立期待値

| Test ID | 対象・入力/観点 | 期待値・独立根拠 | 結果/証拠 |
|---|---|---|---|
| PT-OPS-INSPECT-PAIR-IMAGE | 4480/4482、全Unit19属性・32設定・24表・Java101/Python4FD完全二読 | 既固定全像と全field比較。独立literal19、欠落19/重複/未知/異常・設定契約実辞書を検査。値の除外なし | 4482/45586 actual0、全原値/全FD同値 |
| PT-OPS-INSPECT-PAIR-HANDOFF | 4488/4490/4492、権限/子孫/FD全属性・DB両端・null/欠落/未知/境界/並行所有 | 固定実証像SHAと独立PID/ticks/argv/FD集合・loopback端点。全FD各target/metadata/fdinfo差は拒否。同/run二FDの歴史mtime/ctimeだけ単調・fresh時刻以下、境界内は全値同値 | v1 proof15588=1/全像保持、BUG1365先行→v2 proof29421=0/新十Ref正常。実旧二TERM、元20650actual143、旧scope UNKNOWNは不変更 |
| PT-OPS-INSPECT-POST-HANDOFF | 4494/4504/4510/4512/4514、起動中FD競合・元wait/例外・正常/異常子終了 | 未reap子のZ/FD0/cmdline空/PPid/rawwait0と独立post manifestを結合。新postの予約/固定source/親/新PID→元waitの実0/7を実関数ASTで検査。既保持owner全FDは削減しない | 元26012actual255/旧post7ab5cdc6とUNKNOWNを保持。新4514/96490actual0、metadata TERM1/子signal0/旧資源0、別freshpost0・全外側新十Ref正常 |
| PT-OPS-SET-FIELDS | 4498/4500/4516、sealed show・全19属性・同artifact inspect/place | 実sealed source SHA0dd9ded7から実show定義を抽出し、productionから独立したliteral19の正常二順/全欠落19/duplicate/foreign/malformedを入力。旧tupleは拒否、新callerはset19。negative試験は関数抽出失敗を合格へ算入しない | 3fixture0、現配備JAR compile4500/44998actual0・18role/全142file閉鎖・旧独立Java fixture維持。guest v5 inspect/placeは未実施 |

## 実行結果・不変条件

元4494は当Java827198→子Python827230だけ通常pidfd TERM、旧DB827228/advisory71419602/M-A消失、元inspect真正143/元hostgate自然継承。独立postは起動済みのまま正常0となったが、親の記録用fullFD列挙が子FD閉鎖と競合しUNKNOWNへ入ったため、親全体0としなかった。BUG1366を先行起票し、元controllerを変更せず、別SSC298でmetadata-only828676/4FDと子829193/Z/rawwait0を二読認証した。

新4512同artifact proof72371=0/a037dd78・設計only PR144/mainb65d1283eの後、4514/96490は16:37:20Z actual0。metadataだけ通常TERM1回、子はsignal0/自然reap、元4494の真正transport255は143へ推定補完せず保存。所有変更後の別fresh postは16:37:12Z actual0、新M/A/RODB/71419602/heartbeat/十Ref正常、全原値before=after **148a8d8a3a3284dbf4a72833ca808ca8a07cee84a85b5562f07356006ac91148**、全24/189/32/19Unit/原本Backup鍵/native58/startup37・全ordinary/kernel/DB/lock0を確認。最後の外側十Refも正常返却した。旧Root143と旧scope UNKNOWNは不変更。

工具の選択回帰は **28試験/終了0/F/E/S0**、実command/branch/HEAD・各元manifest path/SHA・source・実終了値は[manifest](evidence/output/PG4518/manifest.json)、[ログ](evidence/output/PG4518/tool-tests.log)。manifest SHA **39686c25eb137d5a92992146267430486789ea9309d8d284b71b4f48fede183d**。OS/JDK等は既toolchain記録と各compile/runの固定環境を維持、対象Production sourceは同964e/current7bbで混在加算なし。fixture入力は人工ID/固定公開ハッシュ・root私有像へのSHA参照に限定し、rawDB/credential/session/token/keyを公開しない。

## 未受入

新v5 guest inspect/unused・RO/有限公開・新通常Root1800/当source native/実Browser/CHR/F03/四coverage100/451/trace/引継ぎは別残件。工具28試験をProduction PTへ加算せず、正式1964/53・工数完成率null・QA051 final保留を維持。新nativeを旧sourceから合算せず、PG/PT/IT/ST全完了ではない。
