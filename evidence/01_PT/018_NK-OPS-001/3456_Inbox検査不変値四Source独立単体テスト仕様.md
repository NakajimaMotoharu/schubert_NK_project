# Inbox検査不変値四Source・独立単体テスト仕様

群18070/開始3715、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、HEADa2b02d9f310dae51b0b8503958befc80b1d7d1ea/dev-foundation。固定1.5/4/8pp cap10・共有used83/rem17/reset1793774153。F03主費/元owner P004-04参照追加費0、原DB Test/fixtureの抽出・改作0。

正本origin/main8b91944d SS324§12.6/12.7・SS331§3.8・SS341§7.3、NK-DAT001/DAT009/MQ008/OPS009、UI212241251/QA046/SSC049、PG-D122128130/PT033～040・081～088・097～104/新PG-D1118。2087は古source constructor静的レビューのみ/実PT成功でない。今回InspectionRun25行/Step29/Progress46/Execution55全本文を確認、全calleeはObjects/Optional/UUID/Instant/enum/固定診断のみ、SQL/実検査実行器/process gateを呼ばない。

|Test ID/method suffix|入力/操作|独立期待値・根拠|
|---|---|---|
|INSPECTION-VALUE001/RunRetainsExactMicrosecondBoundsAndRedactsIdentity|UTC0001最小/9999最大/固定µs|id/cutoffを同identity保持・固定redaction。既Run日時契約|
|002/RunRejectsNullAndEveryTimestampViolation|null各component/範囲前後/1ns精度|NPE invariant又は固定IAE、正常化catch0|
|003/StepHasExactEndCursorEquivalenceAndRedaction|DELETED/PROTECTED＋cursor、END＋empty|指定outcome/cursor保持・IDを表示しない。SS32412.5|
|004/StepRejectsNullAndBothInconsistentCursorDirections|null/END present/nonEND empty|固定IAE/NPE|
|005/ProgressRetainsExactCountsAtZeroAndLongMaxWithoutOverflow|0/全削除/全保護/MAX両端/complete両値|count/flag/固定件数表示・ID/cutoff/cursor非表示、SS32412.6算術式は独立表|
|006/ProgressRejectsEachIndependentCountAndCursorViolation|負inspected/deleted/protected、deleted>inspected、差不整合、zero-cursor二方向/null|各独立前提で固定IAE/NPE、overflowを加算で作らない|
|007/ExecutionUsesOnlyLiteralExitEquivalentAndLastConfirmedValues|SUCCESS END保護0/WARNING END保護1/三failure empty・途中progress|exit相当0/10/50 literal・元lastConfirmed保持/未取得を0へ変換0。実process gateの証明でない|
|008/ExecutionRejectsNullMissingOrInconsistentCompletion|null/完了statusでmissing/incomplete・保護数とstatus逆|固定IAE/NPE、SS32412.7|

期待値をProduction methodで生成せず、上位SSのliteral/手書きcount表/固定message/0,10,50を使用。toStringのstatus部分は既enum名の表示契約だけ、処理結果をexpected生成に使用しない。日時は固定parseだけ/now0、UUIDは公開固定0,77で鍵/sessionでない。並行/再送は不変値自体に状態変更無し・実DBの同run再開や50の実Unit確認は別HOLD、当DTOだけで省略しない。

八件/一suite/一exec、全四Source六Code（Execution.Status/Step.Outcome含む）を公式filter不変更/除外0で測定。全branchを実測し未達は未達のまま、enum自動生成メソッド/record自動methodは公式適用だけを保持し安易な除外設定を追加しない。null境界とconstructor invariant・既normal14216/静的14224でNPE正常化0を維持。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg18070_inspection_values_eight_pt.py。Java25.0.4、同normalJar/source/snapshot/wholeclosure/CRC/session/XML/FES/独立oracle/全counterを照合し3457/manifestへ環境・command・時刻・終了code・input/class/Test/source/exec hash/BUGを保存。実DB/JMS/IO/crypto/Root/native/鍵/credential/Thread/時計0、JDK内部初期化効果null。新quality八は普通5786へ加算せず別域、既Production初測定/新製造0、正式1964/53・歴史17/190・新WBS受入0/工数null/QA051final/451/全HOLD維持。
