# 1044 当batch未網羅method・既PT対応調査仕様

NK-OPS-001/NK-BAT-001、WBS-N15.06のcurrent source/byte/未採取範囲確認subset。currentSource a2ecc/PG4980・元3791/553/1650/六static0、公開PG5112 manifest60dadc92に固定。Production/Test/期待値/Currentbaselineへ変更せず、実VM操作/試験再実行/coverage除外を追加しない。

`pg5118_batch_residual_map.py`は元public manifest hash/source/countとbatch XMLhashを先行資格し、全classの四counter合計をreport rootへ照合。残739LINE/147METHOD/9CLASS/434BRANCHを、JVM class/method descriptor/起点line・sourcefile/SHAと既test中の候補文字参照へ展開する。branchの真偽・例外原因をXMLのmiss数から推定せずUNKNOWN、source/test文字参照を実行証明/意味的trace完了/新PT数へ変換しない。個別SS/TestID/合法native/独立fixtureは当結果から別に確認する。

PT-OPS-MAP-5118-001～003管理3成功：手作り一class/一methodの独立XML counter（L2/M1/C1/B2/line10/desc()V）とUNKNOWN保持、counter合計/重複class・method/負値/不正sourcepath/二重counter拒否、miss0でも新試験/受入と呼ばない。`python3 -B -m unittest pg5118_batch_residual_map_test`。実commandは固定/push後`python3 -B tools/quality/pg5118_batch_residual_map.py`一回、出力provisional/PG5118-batch-residual-map-v1/report.jsonのhash/HEAD/source/XMLhashへ対応付ける。

元DB/Backup/鍵/native88/全成功失敗/stash7保全。実行結果のaffected class/method数はcounter miss件数と区別し、指標重複加算0。正式1964PT/53scope・17/190/工数率null、F03/QA051final/四全100/CHR/451/意味的trace/引継ぎは別未完。原/v3/v4/各開始見積固定、当調査開始見積低.05/標準.2/高.7週次共有ppは実費・完成率でなく、個別専有費/N/T不明はnull。
