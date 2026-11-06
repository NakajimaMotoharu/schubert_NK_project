# 質問受付Requestのpure contract 単体仕様

NK-QST-001/WBS-P011-01、RD QST001/ASY001・UI224236・SS312/323§9.6/324、QuestionSubmitRequest全public methodとdecode/ensureOpen/constructor。MainD8不変更。元原TestにはFingerprintKeyRing/HMACがあるため呼び出し/抽出せず、新Testを公開メソッドだけで独立作成する。

UI236 golden payload: [0,4096)質問本文UTF8+SP右pad、[4096,4132)syntheticUUID36ASCII、[4132,4144)SP12。ヘッダはsynthetic immutable値、認証されたとは扱わない。独立expectはliteral Body/UTF8、canonical owner/layout001/target QUESTION:NEW/一field question-X1、Production hash/encoderから生成しない。null、1/4096byte/Unicode境界、nonNFC/control/UTF8/length/reserved/token/未知layoutの拒否、callerコピーとcanonical field各所有、終端後全access拒否、metadata除外/actor-body包含、自己所有2worker8copy＋latchでcopy→close順を制御して10秒joinを検証する。Rawwire/context/token/key実体は証跡へ出力しない。

PT_DEFAULT、PMO961/event3995原1/3/6pp cap8。shared012/profile064 prepare/static→Git固定→全8を単一run、正常D8 JAR CRC/全physical一source/四counter100/strictpost。アプリ初期化はprotocolと当Request/CanonicalField/CanonicalRequest/Actor/Role/testだけ、held4 probes0を検証する。HMAC・FingerprintKeyRing・鍵・認証実処理・Inbox・DB/VM/Root/JMS/HTTPは起動しない。Main正常20112/SB20114再利用、既成功再演0。再送/保持上限/実認可/受付DBの受入と分離、全451/正式1964/53/歴史17/190/工数null不変。結果014/manifestへ環境・command/source/exit/XML/counters/BUG/hashを保存。fresh群末は実終端後APIをend_fieldsへ結合。

|Test ID|method|
|---|---|
|PT-QST-PORT001|literalOffsetsAndCanonicalFields|
|PT-QST-PORT002|independentByteAndUnicodeBoundaries|
|PT-QST-PORT003|reservedTokenAndUnsupportedLayoutReject|
|PT-QST-PORT004|nullBoundariesRejectWithoutCloseLeak|
|PT-QST-PORT005|sourceAndReturnedBuffersHaveSeparateOwners|
|PT-QST-PORT006|closeIsTerminalAndReturnedCanonicalStaysOwned|
|PT-QST-PORT007|traceMetadataExcludedAndActorBodyIncluded|
|PT-QST-PORT008|parallelCopiesAndControlledCloseKeepIndependentOwnership|
