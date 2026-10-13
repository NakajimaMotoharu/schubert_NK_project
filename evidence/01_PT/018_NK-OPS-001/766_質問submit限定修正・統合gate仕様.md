# 質問submit限定修正・統合gate

Program NK-WEB-001 SCR018、UI222§8/UI224/SS313352、BUG1222/YKT988、PT-QST-JS001-A～H／PT-WEB-DISPLAY-QSB-DISABLED。事前独立2265で3b7fのvalid送信disabled欠落を確認、期待値はUI222で固定。

候補44aa51e79fdcf8bb154f26a51a40d1d087babc32からquestion-input-validation.jsと対応Node fixtureだけ統合、他15Production file・title oracle・副担当新Java等は取り込まない。既CSP外部script、CSRF/operation_token/Question input name/value/byte制約を不変更。valid→button disabled、invalid→preventDefault/reportValidity/非disabled、欠落button fail-closed、keyboard submitとinput無し再検証・NFC/UTF8/制御文字の独立literalを八caseで検査。

Node24.19.0 `--check` exit0、`--test --experimental-test-coverage --test-coverage-{lines,functions,branches}=100 --test-coverage-include=<absolute script> <test>` 八成功/F/skip/cancel/todo0、Production script実在と三counter100。2264独立canary0。実Browser/HTTP/DB/JMS/security/session/CHR/正式451は限定DOM doubleで代用しない。元3b7fのnative／正式1964/53を新sourceへ合算0。

次trigger：新二JDBC PTと承認済み一JS resource変更をまとめ、fresh全六3637PT/540suite/1643Main・静的六0／XML/同archive/source・JS三100を所定独立qualifierで照合する。既成功3635を新source試験の全合格へ流用しない。新sourceの署名BOM・実HTTP/NK/CHR/native・四100/trace/終了依存は後続、同source全回帰を工具/文書変更だけで反復しない。

開始見積りJS群.25/.75/2pp固定event0619、source固定と全回帰K01費は別、共通費重複0。修正commit/hash・fresh全回帰結果は実終了後追記。Current baseline/原本Backup・旧失敗0fdnative38・七stash保全。
