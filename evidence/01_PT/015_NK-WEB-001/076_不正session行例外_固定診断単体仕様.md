# 不正session行例外 固定診断単体仕様

Program NK-WEB-001 InvalidSessionRowException暗黙constructor、RD FUN001/AUT001..004/UI226/SS314§7.2.4/331/352/SSC041、主WBS-P015-01。開始4090原.25/.5/1 cap2固定。現public manifest lookup/legacy空・followup0、同byte既whole証拠無しを確認。Mainと親SessionStoreException constructorを全文review、固定診断・型を実装済みで製品変更不要。

|Test ID|method|独立期待|
|---|---|---|
|PT-WEB-INVALIDROW001|invalidRowHasFixedPublicDiagnosticAndNoProviderCauseOrSuppressedData|messageはsession storage is unavailable、cause null/suppressed0、exact subtypeと固定toString・SessionStoreException境界で同一instanceを捕捉|
|PT-WEB-INVALIDROW002|eachFailureOwnsItsDiagnosticStateWithoutChangingAnotherFailure|失敗ごと別instance、片方の自己所有診断stackを空へ変更しても他方の元stack/cause/suppressed不変|

実データなしの例外object二種だけ、SQL/provider/DB/session行/鍵/認証/HTTP/VM/Root/held四/例外graphを読まない。Testのstack操作は自分が生成した例外だけで既存例外・実ログへ触れない。constructorに引数無しのためnull/境界入力・再送/並行資源の契約は非該当、空cause/suppressedとfresh診断state分離で固定診断・可変状態独立を確認。provider情報を渡さず、Throwable全APIの不変や外から任意causeを付加できない仕様を新設しない。親preserveFatalは呼ばずconstructorだけを元execで確認する。

input017 prepare/static/run <frozen source>/post、JDK25.0.4/JaCoCo0.8.15/通常Main4217-20990 CRC/six NullAway-SB20992同byte、CPは既web jar/JSpecify/JUnitだけ。新2/Main1physical、line/method/class100と自然branch0 N/A・ratio null（0/0実測100へ補完しない）、手動除外/旧exec合算/人工constructor反射無し。Main/Test PMD0CS0/SB20992同byte0・抑制追加無し。元XML/TestID/source/入力期待actual/command/終了code/日時/OS-JDK/CRC/session/hashをstrict/独立postへ。結果077、失敗障害は915/916先行。実DB不正行処理・model化/削除/認証/session運用・native/CHR/QA051final/451・新leaf/正式1964-53/個別17-190/工数nullは別未完。
