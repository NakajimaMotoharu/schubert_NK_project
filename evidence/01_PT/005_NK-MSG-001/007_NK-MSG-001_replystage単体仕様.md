# NK-MSG-001 返信stage callback単体仕様

対象ReplySender.send/constructor、Test ReplySenderStageContractTest四method/PT-JMS-STAGE001～004。RD MQ003/008、UI212/231/232/233 IF001、SS312§3/321§7～8、668原0.5/1.5/3pp/cap10。Main6b53不変更、先factory資格PG18602は別componentとして再利用し、その旧Testを確認目的で再演しない。

669で固定Artemis2.56 Queue(String)→Destination(TYPE.QUEUE,null session)→SimpleString/JNDIStorable Object constructor/固定文字列の分岐を実bytecodeで確認。FQQNに?が無いためURI設定parserへ進まず、URISupport.containsQuery(SimpleString)はString/byte検索だけ。接続factory/session/broker/network/native/鍵操作をしない。localpublisher SHA1/正常classpathから実artifactがartemis-jakarta-clientであることを確認した。SDK値getterは送信先固定値を検証するためだけで、SDK自体のcoverageや接続資格には使わない。

STAGE001正常一vector：UI232 literaloffsetから独立login error wire688byte/共通256+data432/0100を構築、実認証なし。期待=mode確認→message作成/属性→producer取得→persistent2→TTL10000→固定FQQN nk.sync.reply.web::nk.sync.reply.web.qへ一send、created message identity一致。borrowed contextのcommit/ack/close/rollback/未列挙操作はproxyで即失敗する。STAGE002 null context/body＋mode1/2/3/-1計六vectorは取得前拒否、nullではmode read0、mode不一致ではmode一回だけ。STAGE003 mode/producer/persistent/TTL/sendの各RTE/Errorを計十vector、全同一Throwableと独立literal ORDERのprefixだけ、後続/再試行0。STAGE004 message構築中writeのchecked JMSException一vectorは同一例外でproducer未取得。計18vector/四Test ID。Fixture/wire/Throwableは全assert前に構築し、expectedをproductionから生成しない。

既存JDK25 javac→固定JUnitConsoleで当wholeclassのみ/parallel-autoextension false/180秒、JaCoCo新単一session appendfalse/fullphysical ReplySenderと原CRCを独立照合。四counter未達・原例外/未知/失敗を0へ補完しない。PMD/Checkstyle/formatterも同sourceに実施する。真の実JMS/ACK/TTL/commit/DB/Root/nativeは未実行のままであり、実compatibility/親WBS/全451/正式/IT-ST/V成功を主張しない。結果・source/branch/command/OS-JDK/tool/hash/期待-実際/BUGは008/public manifestへ保存する。
