# 2427 Systemd Test 重複literal21件・製造静的確認仕様

## 着手前固定

2026-10-28、保存HEAD4c21935ffde59458d97ccff7df7dc8533763da06/origin一致、Production source80ba5f783432c84b6facd83bcd3a80774f4e4665。共有used5/残95/reset1793774153、secondaryなし。低位1/基準3/高位6pp、群上限10pp（専有消費はnull）。次定期点検used10、残10以下/取得不能では新規着手停止。原/v3/v4/v5見積を変更しない。

群SYSTEMD_TEST_LITERAL21_PG_ONLY_V1、費用主担当WBS-P018-03、変更目的F03。親F03へ費用を重複計上しない。旧原診断PG10690、現Test SHA a3cef94ea182a9764cb6ee1f97ba7315d2b3cbaebdde5c7d7d42c7a4f7891037一致、全文1058行を読取済み。関連SS/要求/TestIDの既存根拠は1096/1476、既source責務registry PG13184（3335e707da5300809d267d79177a3969fe83043fdfa07f504c07f4c21e4ce4ee）。元owner/cost P01803を維持。

## 対象・独立期待

`src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSessionTest.java` の既存40 raw中AvoidDuplicateLiterals21件だけを修正する。元字句値・呼出順・assert・例外・Arena所有・lambda・全Test methodを不変とし、Test内のprivate static final Stringへ抽出する。Production定数を期待値に参照しない。新Test ID/新論理artifact/新physical追加なし。SS/RD/UI/業務変更なし。

期待：元21指摘のみ消滅、他19指摘はlineを除き原診断と同一、Checkstyle0。元全文を先に公開原本として保存し、全source tokenを定数展開・宣言削除で元全文へ逆変換できること。21定数値の各非同値変異とassert/比較/終端欠落を拒否する。固定後sourceで六module正常build（format/型/null/依存/Werror、PT0）、六SpotBugs、全1843Main byte不変、旧1974Test keyset不変・変化は当SourceFile範囲だけ、全method形状不変とprivate ConstantValue文字列をjavap metadataで独立照合する。

## 実行許可・未実施

PGの定数抽出、hostコンパイル/PMD/Checkstyle/SpotBugs、class/JAR/javap metadata読取のみ。targetをload/instantiate/invokeしない。既native wholeには実library load/FFM/所有/実資源があり動的PTはNOT_EXECUTED_HOLD。新harnessでの切出し・native fixture再演なし。coverage NOT_MEASURED、PT免除/代替承認/真正経路の成功へ変換しない。旧sourceの成功は移植しない。

## 受入・証跡

BUG2035/YKT1783を修正前起票。限定PG/静的成果だけを2428とPG13190以降へ保存し、動的再試験HOLDのまま台帳に残す。全WBS/正式1964PT-53scope/17-190/工数null/QA051finalを維持。registry995行の当Test SHA一だけ変更・元費用/旧runtime/unknown二を保全。raw8459→8438、Test6957→6936、原是正966→987は21件消滅を実証した場合だけ計上し、全体static0やF03完了にはしない。保留二工具を内容アクセス前に除外。
