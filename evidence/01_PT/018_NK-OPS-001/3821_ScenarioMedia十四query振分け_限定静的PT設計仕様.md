# Scenario/Media 14query振分け・限定静的PT設計仕様

主P008-01・関連P009-01追加0。原1/3/7pp cap9。477常設静的PT設計方針、承認SS323§9.1/9.2・332§2/4/9を適用。両Requestの旧10件は成功・counter部分のまま参照し再演しない。query先repositoryはpreserveFatal→保留例外の経路を含み、当14枝の動的PTを開始しない。Main/既Testの置換・切出し・fixture作成・compile/JVM・実DB/Root/VM/native/鍵/署名/permit等は一切含まない。

事前固定575の14layout/DTO/振分け先/応答形とcanonical順序はSS323の手書き期待表。コードと独立したこの表を照合する。既canonicalの実測counterをquery実行済みへ転用しない。各IDはSTATIC-SCN/MED-DISPATCH-01..14、静的レビュー完了と動的NOT_EXECUTED_HOLDを併記し、PASS/実測coverage/PT免除に変換しない。

観点: 六Scenario/八Media各一つのdecode枝→同じ内部kindによるquery、actor/header/context非混同、DTO受渡し、通常一覧/descriptor不在/Scenario detailの形、三query引数のnull前置条件、借用Connectionの所有/commit/close/file/JMS無し、canonicalのfields順序とOptional欠落、例外を不在へ補完しない。実際のSQL/TX/DB結果/null/並行/再送/失敗graphは未実測のまま残す。独立postは誤layout/DTO/関数/形/field順序/実行PASS/DB証明/欠落/重複等を否定し、Source/authority pinとstatic範囲だけの整合を確認。
