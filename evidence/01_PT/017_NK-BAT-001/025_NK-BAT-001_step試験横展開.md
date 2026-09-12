# step試験横展開

PG163/BUG176～178/YKT137～139、先行6a44bb8d。Production仕様違反ではなく新PT oracle/probeの不足で、先行登録後にtestだけ是正した。正式認定は全回帰後まで保留する。

| 対象・原因 | 修正/非該当根拠・再発防止 |
|---|---|
| BUG176/BAT138時刻 | schubert_batchのrole初期timezoneはAsia/Tokyo。fixture locked()でUTCを明示し、日時の独立SQL期待はUTCのまま維持。Production bindは既存OffsetDateTime UTC不変 |
| BUG176/BAT139・152 boolean | getString(bool)はt/f、bool::textはtrue/false。単独bool queryをSQL ::textへ明示し文字期待を変えない。bool連結の既存queryとtyped getBoolean/getObjectは別契約で非該当 |
| YKT137/BAT146/PG160・162 | 歴史UTC0001/1582/1900/1970/9999とJST日付3timezoneを維持し回帰。既存時刻literal/checksum/期待値を書換えない |
| BUG177/BAT149 duplicateId | 2行目だけ固定id1だとsequence実IDと重複しない。両行を固定合成id1、attempt1/2へ統一し必ずPK重複を作る。列集合/全case名を明示し拒否を確認 |
| YKT138その他history合成 | duplicateAttemptは番号1/1、doubleSuccessは別id/attemptでSUCCESS2、100行はid/attempt1..100の完全独立集合。欠落/未知/負値/時刻/statement/rows/INSERT・REPLAY多行も個別試験。SQL位置faultは独立mapと発火数を照合しており別原因 |
| BUG178/BAT153 migration | Flywayはschema作成1行を管理する。version非NULLかつtype SQL/成功だけ19を数え、SCHEMA/versionNULL成功1を別assert。19期待を20へ変える修正ではない |
| YKT139既存13class | BUG175/004061の全inventoryはversion非NULL/type等でversion集合を照合し、旧checksum/resource19と区別済み。新BAT153のみ対象。正式全moduleで全対象の後条件回帰を確認 |

探索1: 2026-09-13 04:49:31 JST終了/15.716秒、24件中5failure（BUG176の3、177の1、178の1）。raw /tmp/pgpt-step-explore1.log。探索2: 04:51:17終了/12.112秒、new24＋Storage8成功、failed/error/skipped0。全7新class/31method/235line/160branch missed0（探索集計、正式clean認定は別）。raw /tmp/pgpt-step-explore2.log。

BAT150の独立JDBC inventoryはsource前の023どおり57/70/70/80/50/72=399位置、各位置1発火・borrowed所有維持・rollback後条件と6複合close2発火を確認。観測mapをexpectedに流用しない。2実traceを020/019の独立literalへ照合する。branch/source/日時/tool/command/exit/実input・期待/実際/coverage/hashは024/manifestへ正式実行後記録する。
