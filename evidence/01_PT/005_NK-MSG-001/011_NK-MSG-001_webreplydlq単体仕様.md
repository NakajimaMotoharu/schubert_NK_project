# NK-MSG-001 Web返信DLQ Sender独立単体仕様

対象ArtemisReplyDlqSender constructor/send/private診断helper全Source、Test ArtemisReplyDlqSenderContractTest八method/PT-JMS-WDLQ001～008。RD MQ008/010、UI231/251、SS321§7/10/11・PG-D018。682原見積0.5/1.5/4pp/cap10の既通常群。683で八method/126vectorを実行前に凍結。API側の八Test/135vectorは異なるtargetで、再実行やAPIのPASS/coverage転用はしない。Source/Git6bと新Web Testは独立資格を取る。

Web SourceはClock/JMS/protocol/fixedSDKQueueだけで、WebStartupException/Temp/credential/session/DB/Rootへ進まない。元receiverのwhole held Test/fixtureを抽出・呼出しせず、Web/protocol jar＋JMS/JUnit/固定SDKのown interface callbackだけで確認する。PG-D018の十property・本文/JMS subtype保持・Password/body/hash非複製と、固定origin nk.sync.reply.web(.q)/WEB_REPLY/errorPROTOCOL_INVALID/DLQ/persistent2/TTL0を独立literal oracleとする。任意property markerは公開合成値だけ。本文/deserialization/ACK/borrowed context commit-rollback-closeや未知APIはproxyが即失敗する。

WDLQ001正常一vector（元TextMessage identity/全十property/order、caller所有を保持）。002transport十一（null/空/blank/ASCII両境界/127128129/非ASCII）。003UUID二欄各十で20。004layout九＋JMS int count八で17。005constructor clock/context/messageの三nullと非transacted mode一で四、取得前拒否。006Message二十API段階×checkedJMS/IllegalArgument/Error＋Context/Producer五段階×runtime/Errorで70。007Clock.instantのRTE/Error二は同一Throwable・一call、DetectedAt setter/producer前停止。008 Clock providerがnullを返す契約違反一は一call後failclosed、送信成功/UNAVAILABLEへ正常化しない。計126vector、実Test IDは八件。fixture/clock/fault/入力はassert前に生成、expectedはSource methodから作らない。

DIagnostic128ASCII/36canonicalUUID/8formatLayout/UNAVAILABLEとcount下限の固定表は675でSS/PG判断と元独立Writer oracleから拘束した期待データを共用、別targetのruntime結果とは区別。既SDK669/18606値構築の静的根拠を再利用する。ClockはownfixedInstantまたはownfaultで実時刻/外部資源/鍵を読まない。本文自体は未読でありcodec/業務wire/実JMS rollback/ACK/TTL/role/native/CHR/親WBS/全451/F03/正式/V/IT-STを証明しない。

JDK25 javac/既存Console whole新classのみ・並列/autoextension false/180秒・新singleJaCoCo appendfalse・全physical Sender class/CRC/同Sourceを独立照合。四counter100とF/E/S/aborted0を要求し、不足/未実行は未完に残す。PMD/Checkstyle/formatも同sourceで確認、指摘は抑制しない。実command/環境/branch/commit/終了/coverage/hash/原失敗は012結果と公開manifestへ保存する。
