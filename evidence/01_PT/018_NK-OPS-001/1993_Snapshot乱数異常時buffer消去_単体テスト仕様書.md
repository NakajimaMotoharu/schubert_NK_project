# Snapshot乱数異常時buffer消去・単体テスト仕様

2026-10-26、NK-MSG-002/ResponseSnapshotCodec.encrypt、WBS-P006-01/群2248、開始1/3/8pp cap10。RD DAT-009/MQ-008/OPS-009、UI241/242、SS324§6/15・352§11.2、Program006既PT-IDEM007/008/独立JCE、PG-D674/BUG1771/YKT1522。旧8ba82083/normal9812を修正前witnessに使用する。元full4222/別source codec成功・BUG1453成功は新sourceへ移植しない。

全て自己所有有限host JVM・公開合成32byte key/固定入力だけの通常PT_DEFAULT。実鍵file/環境credential/私有raw/DB/JMS/HTTP/VM/Root/native保全物/permit/intent/配備操作0。SecureRandomの既package constructor seamで、nonceを合成値で埋めた後に固定例外を投げる。providerが受けた自所有nonce arrayはfixtureだけが参照を保持し、private reflection/暗号key読取り/メソッド変換/Graph9操作なし。JDK通常圧縮は原method、危険な実OOM/乱数providerの全体交換は行わない。

|Test ID|class/method|入力・操作|独立期待・根拠|
|---|---|---|---|
|PT-IDEM-RNGSCOPE001|ResponseSnapshotNonceFailureTest.rngscope001RuntimeFailureClearsOwnedNonceAndPreservesIdentity|公開合成key、固定identity/非秘密plaintext、nonceを合成byteで埋めて固定IllegalStateException|同一例外instance、provider一回/12byte、参照nonceがliteral zero12、caller plaintext/key不変。expectedは固定zero配列と入力cloneでありProductionから生成しない|
|PT-IDEM-RNGSCOPE002|ResponseSnapshotNonceFailureTest.rngscope002ErrorClearsOwnedNonceAndPreservesIdentity|同fixtureのAssertionError|001と同じbuffer/借用入力後条件、Errorをcatch正常化/別例外化しない|

元plain witnessは上記二条件をold Jarへ実行し、消去不足を真正exit1として保存する。これは新未実装TDDではなく実装済み所有境界の障害確認、通常PASSへ加算0。修正はnextBytesを既try先頭へ移すだけ。新source固定後は既ResponseSnapshotCodecTest全7（独立JCE/最大/旧鍵・AAD/tag/不正圧縮/null/lifecycle/AES unavailable/既scope frame）＋新2の全9/2suiteを一つのrunで実行し、全codec Code/CRC/sessionと四counter、Main/Test静的・正常compile/NullAway、全Main byte差分を独立照合する。漏れ/未到達があれば100化せず追加仕様を先に確定する。

YKTは他七nextBytesの字句scope/所有をsourceで確認する。既有効finallyを原hash/非該当根拠で残し、対象外業務の確認再演を増やさない。fixtureのbuffer後条件とcompressed/AADの同finally支配は実class/sourceの順序でも照合し、JVM/JCA内部copyの物理消去は保証外と明記する。allocation失敗一般や全暗号ライフサイクル/本番JDK providerの正常性をこの二件だけで証明しない。

command/JDK25.0.4/OS/source/branch/開始終了/exit/全TestID/XML/coverage/hash/BUGを1994と公開manifestへ保存。秘密実体・nonce内容・raw sessionは保存しない。正式1964PT/53scope、個別17/190、QA051final、工数null、全actual/Graph9/G07/全WBS監査HOLDは別のまま。必要な同source全451を限定PTで代用しない。
