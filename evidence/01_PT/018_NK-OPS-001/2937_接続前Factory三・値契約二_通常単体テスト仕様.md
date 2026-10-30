# 接続前Factory三・値契約二：通常単体テスト仕様

PG15502 / PG-D944。Production `6b53efeec87f3ec36a840dd8e7759656cb4aee5c`、normal14216固定。群3320、P005-04主担当、P007-03/P006-02/P007-01は参照のみ・追加費用0。開始見積り0.75/2.5/6週次共有枠ppは固定。今回の5件は既存Test IDの当source資格確認であり、新機能・新設計Test・正式受入ではない。

対象は原ArtemisConnectionFactoryProviderTest全3、EnumValueCatalogCompatibilityTest全1、ExceptionValueContractTest全1。Main/Testとhelperの全文、元1299/1526/1916、最新followup索引・現registry非重複を確認。原suiteを抽出・改作しない。Main provider全1Source/2Code（ConsumerProfile含む）を通常Jar/現在source/snapshotと照合し、単一fresh JVM/exec/session/XMLで四counterを測る。既資格helperのcounterを新対象へ合算しない。

関連NK-MSG-001、SS321§6、SS314/331/352、PT-JMS-011/PT-F03-ENUM-API001/PT-F03-EXC002、BUG1478/1482・YKT1237。期待値は本番method生成でなく承認済み設定と原Testのliteral：call2000/failure10000/TTL30000/initial3/reconnect-1/retry1000/multiplier2/max30000/durable true/preAck false/topology false、window1048576/0/65536、connector127.0.0.1/port61616/timeout3000。URL境界1/61616/65535、0/65536/leading0/localhost/0.0.0.0/query/vm/空の拒否、null契約を含む。enum名・address・threshold5/10・serialization fields0/SUID0、閉じた例外reason/resultCode・固定message/cause nullも独立literal。

実行は自所有の未接続factoryの生成/get/set/closeのみ。createConnection/createContext/broker/listener/資格情報読取・保持/実認証/実DB/VM/Root/Graph faultは実行しない。正常設定中のcatch/retainUnknown/未確認close経路は未網羅のまま保持し、100%へ読み替えない。JDK通常の浅い例外値assertionはGraph探索ではない。禁止四境界とnative六prefixは同じexecの受動readerで確認するが、全HOLD解除を意味しない。

command：`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15502_credentialfree_factory_values_five_pt.py`。開始前に専用post15504の対象・開示を固定。F/E/S/flaky/not-runを合格に算入しない。終了・source/XML/exec/CRC/実JVM環境・不足counter・独立期待値・manifest hashは2938へ記録。正式1964PT/53scope、歴史17/190、工数null、QA051final及び全既存HOLDは不変。
