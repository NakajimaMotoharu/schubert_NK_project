# 2542 MorningBackup引継ぎ・完了memory全8 通常PT仕様

2026-10-29/PG-D836予定/event2925/F03主・P01706費用参照のみ追加0、開始0.5/2/4cap10。source0061/normal13832/静的13838・Main/Test変更なし。

元MorningBackupPreparationTest全六/MorningBackupCompletionTest全二をクラスごと選択する。両Test全body/MainとBackupWorkerRequestの値constructor/static formatter、既BackupStepFixture.manifest・ExpiryReceiptFixture・MorningProcessMain.archive/completeObservedBackupの全到達calleeと初期化を確認。DB Access、固定Clock、Publisher/Continuation/Archiveはすべて手書memory、receiptは固定ASCII/gateだけ。初期化にDB/nativeなし、BatchDatabaseFixtureはcompile/signatureだけ。原Backup/原本/実DB/Root/VM/鍵/permit/intentへ到達しない。Testがnewする自己所有threadはresult.recheckの先頭thread-id拒否だけで待機/I/O/保持経路なし、元joinは有限処理の帰還を待つ・全host実行180秒制限。新mock抽出0。

|既Test ID|入力・独立期待値|
|---|---|
|MBPREP001～006（六）|両begin→publish→continuationの固定順、run/time/recovery同一、九種bad handle/DB失敗/nullでpublish0、publish失敗でworker0。completed/part重複/zero/cutoff前/年境界を拒否、null resultはpublish後NPEで正常扱い0。手書events/41・42/時刻・identityから算出。|
|ISSCOMP004/005（二）|固定0/1/30/255でarchive0or1/DB failure0or1・read1、SUCCESS/FAILEDのliteral結果、同receiptのexitCode・固定morning/ownthreadだけ再確認可。foreign marker/target/outcome/期限/null/IO/runtimeの元identityと後続read0。mutable rows変化/別threadを拒否、固定public canaryをtoStringへ出さない。|

OPS009/BAK001/UI251/SS331§8.3/341§6/343§6.15/SSC092094104134。expectedは手書record/List/counter/identityでProductionから生成0、fixture source/helper SHAと元canonical ownerは13936/13938・13846に保存。実再送/実永続化/実アーカイブは未受入HOLD。

command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13936_morning_backup_handoff_whole_eight_pt.py`。固定JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15・六Jar/SDK/cleanENV/新javac-Werror、二suite8/一session/appendfalse、resource fixture map空。13938で原XML/退出・全source/Jar/helper/CRC・八結果反例と二完全source四physical（二executable/二abstract）を照合し、counter未達は保持する。旧exec/source成功転用・人工除外0。2543へ時刻/command/期待actual/環境/hash/実counterと障害を保存する。

ApiConsumerRemainder/ApiConsumerCloseOwnershipは部分読取で既TemporaryInfrastructureException.preserveFatalへ到達するwitnessを確認、当whole未実行HOLD、残pure部分を抽出0。正式1964/53・17/190・工数null/QA051finalと全原本保全物・二held工具は維持。通常小群停止なし。
