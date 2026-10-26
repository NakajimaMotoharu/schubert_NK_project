# 非秘密位置値・独立期待値是正仕様

2026-10-26、BUG1798/YKT1549、原070/071/SS342343/SYS002004/UI243253/451。主G03.01・原P00307関連追加費0、群2305開始.5/1.5/4 cap10、used30残70/reset1793513544。

既ServiceCredentialLocationTest.opsCredloc005ConcurrentFreshMapsDoNotChangeSnapshot/PT-OPS-CREDLOC-005のexpectedをServiceCredentialLocation.read(...).directory()からJDK Path.of(Test内公開固定ROOT)へ置換。Test-local KEY/ROOT、既8thread×32fresh Map、他四method/全固定期待値/負例を保持。Main/上位仕様/実credentialは変更しない。新Test IDなし。

当source全五method/PT-OPS-CREDLOC-001～005を一回の閉じたcatalogで必要再試験し、001～004は関連回帰四と区別する。独立期待は固定公開Path/redacted文字列/4096長/固定不正message/明示null拒否、Production出力から生成しない。

副作用は自己JUnit JVMのmethod所有executor八threadと新XML/exec/工具receiptのみ。Production closureはMap/Pathの構文検査、Objects invariant、非秘密immutable Path返却・固定toString。Files/実OS環境/credential byte/ACL/inode/FFM/JMS/DB/Root/VM/service/permit/intent/native資格/鍵/witnessへアクセスなし。`Path.of`は文字列構築でfile IOではない。拒否された鍵close等の再試行ではない。

変更Test静的→source固定/正常六compile/PT0/NullAway-Werror→全五method宣言/当class/現在source入力/呼出しclosure preflight→一JUnit/一exec/session→独立XML/CRC/complete ServiceCredentialLocation物理class全四counter/当static/全Main1843・選択外Test保持を検証する。到達しなかったbranchを成功/除外扱いしない。元d17の成功を新sourceへ転用せず、既全回帰の確認再演もなし。全451/native/正式認定は別残件。

command/環境/source/終了/FES/coverage/path/hash/BUGと再試験は2033へ記録。新refusalは再試行せず保全、全HOLD/QA051final/正式1964-53/17-190/工数null保持。通常小群/commitで停止しない。
