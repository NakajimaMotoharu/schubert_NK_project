# 1044 当batch未網羅method・既PT対応調査仕様

NK-OPS-001/NK-BAT-001、WBS-N15.06のcurrent source/byte/未採取範囲確認subset。currentSource a2ecc/PG4980・元3791/553/1650/六static0、公開PG5112 manifest60dadc92に固定。Production/Test/期待値/Currentbaselineへ変更せず、実VM操作/試験再実行/coverage除外を追加しない。

`pg5118_batch_residual_map.py`は元public manifest hash/source/countとbatch XMLhashを先行資格。METHOD/CLASS/BRANCHは全class合計、LINEはsourcefile一意nr/mi/ciから独立集計→source宣言→report rootへ照合する。class LINEは同一source行の重複があるため別合計/差を保存し、許容誤差で黙認しない。残739LINE/147METHOD/9CLASS/434BRANCHを、JVM class/method descriptor/起点line・sourcefile/SHAと既test中の候補文字参照へ展開する。branchの真偽・例外原因をXMLのmiss数から推定せずUNKNOWN、source/test文字参照を実行証明/意味的trace完了/新PT数へ変換しない。個別SS/TestID/合法native/独立fixtureは当結果から別に確認する。

PT-OPS-MAP-5118-001～003管理3成功：手作り一class/一methodの独立XML counter（L2/M1/C1/B2/line10/desc()V）とUNKNOWN保持、counter合計/重複class・method/負値/不正sourcepath/二重counter拒否、miss0でも新試験/受入と呼ばない。`python3 -B -m unittest pg5118_batch_residual_map_test`。実commandは固定/push後`python3 -B tools/quality/pg5118_batch_residual_map.py`一回、出力provisional/PG5118-batch-residual-map-v1/report.jsonのhash/HEAD/source/XMLhashへ対応付ける。

元DB/Backup/鍵/native88/全成功失敗/stash7保全。実行結果のaffected class/method数はcounter miss件数と区別し、指標重複加算0。正式1964PT/53scope・17/190/工数率null、F03/QA051final/四全100/CHR/451/意味的trace/引継ぎは別未完。原/v3/v4/各開始見積固定、当調査開始見積低.05/標準.2/高.7週次共有ppは実費・完成率でなく、個別専有費/N/T不明はnull。

初回実inventoryは集約照合でexit1/出力作成前拒否（operator4a33e2bbd）。root LINEcovered16356とclass occurrences16368（重複12）を混同したBUG1409/YKT1173を修正前起票。元coverage/root/正式の値変更0・全3791/署名/VM操作再演0、初回raw logファイルは未保存で欠測を0/成功へ補填しない。是正後PT-OPS-MAP-5118-004は二class同source同一行のliteral oracle、partial ci/miとcovered扱い・宣言不一致・重複line拒否を追加し管理4件0。未実行の再試験を合格とせず、固定/push後の当host reportだけ再実行する。

再試験operatorcd0a446c8も出力前exit1、四counter数値は一致していたがnative dictの資格metadata二field（classByteMismatch/formal）も全dict比較したBUG1410/YKT1174を先行起票。counter四種を明示projectionし、metadataは型/0/false/余剰を別に強資格する。PT-OPS-MAP-5118-005の独立六field fixture/不正metadata/bool/欠落/余剰/counter型を追加し管理5件0。現原値から90class/360影響methodと全90source対応をread-only診断確認、まだ正式report未作成・意味的trace未完/branchoutcome不明のまま。Main/Test/元Jacoco/3791/署名/VMに変更無し。

実最終元1371 actual0/operator88e200eae、report SHAa6ef6a04c4e0cff9cfa618d86cb3021f5bc98d133024b3cf041bfdc7142ef3c9、90影響class/360影響method（全未実行method counter147とは別）・source対応90/90、元source/class集約・metadata強資格0。JaCoCo XML class要素562は元4970のbatch物理Main562と一致、CLASS counter337（miss9/covered328）とは別指標。全元値L739/M147/C9/B434、LINE source739/16356/class739/16368/covered重複12をそのまま記録。全methodのbranch outcome/意味的traceは未解決のまま、coverage除外/新実行PT/VM操作/受入Leaf加点0。BUG1409/1410・YKT1173/1174限定close、初期失敗・欠測は保全。次はRoot ELF digestの固定SHA-256失敗/読取数同値検査から、SS306の内部testabilityを設計分類して独立PT・製造へ進む。
