# 検索form二Test・十三fixture同値化PG/PT仕様

Program NK-WEB-002、群2495 WEB_FORM_TWO_LITERAL_PGPT_V1、WBS-F03/関連P01507（費用重複なし）、着手前3/6/10pp cap10、fresh使用22/残78/reset1793599188。BUG1884/YKT1635/PG-D688。基点sourcef24d、仕様はRD FUN003008/UI222223225234235/SS313352/SSC072073、元PT-WEB214～221・278～285を維持する。

対象LogSearchFormTestの八duplicateとScenarioSearchFormTestの五。元10690 raw17（duplicate13/THREAD4）・現byteが10892固定inputと一致していることを先に確認する。同値private String定数以外の全tokenを独立逆展開で保持。formの正常/空/欠落/未知/多重/null/Unicode-NFC/byte長/enum/整数境界/日付・31日・うるう年/redaction/immutable snapshot/並行入力の元期待値は固定literal・JDK日時演算でありProduction expected生成へ変更しない。

|Test ID|目的/入力/操作|独立期待・証拠|
|---|---|---|
|PT-FORM-FIX001|原十三warningのsource/位置・literal参照を同値定数へ|逆展開後全token一致、誤値/定数欠落/@Disabledを拒否、Main/他input不変|
|PT-WEB214..221|既Scenario原八method・固定UTF8境界/enum/null/64task|元sourceの全assertionを保持、元Test ID・件数を新設しない|
|PT-WEB278..285|既Log原八method・固定日時/範囲/enum/null/64task|元sourceの全assertionを保持、JST→UTC固定値・期間境界不変|
|PT-FORM-FIX002|変更二Testの元PMD/Checkstyle規則|duplicate13消滅、CS/processing0、残THREAD4は有限自己所有executor/TWR/Future10sとstandalone構成の具体文脈へ結合、抑制0|
|PT-FORM-FIX003|一新sourceの正常six compile→必要16PT→独立XML/exec/全Webartifact|F/E/S/aborted0のみ成功。LINE/METHOD/CLASS/BRANCHは全Mainとpackage-info扱いを含め実測し、未達を100%としない|

PT_DEFAULT：対象Test/Main全文のreadで純粋form/typed request/JDK値処理のみ、他のTest helperなし・Before/After/Extension/TempDir/反射/実HTTP/DB/JMS/Root/VMなし。固定8worker/64task・Future10s/TWR、専用JVMに外側240s期限。副作用は工具所有の新SLOT/正常snapshot/XML/execのみ。closed method catalogで16だけを選択しautodetection/parallel/package discovery無効、保留Test抽出なし。

工具は10946 plan/10948 inverse→変更sourceをcommit固定→10950六module正常compile/package（skipPTはPASS算入しない）→10952 static/10954既16method通常PT→10956独立元結果/完全coverage/全Main・他Test不変。実command/OS/JDK/tool/source/branch/時刻/終了/入力・expected・actual・BUGをmanifestへ保存し111結果からhashで参照する。静的残/coverage未達/未実行を正式合格へ混ぜず、所定451全体は別。Currentbaseline/実原本/鍵/native/保留二工具は不変更・読取実行なし。
