# Revoke claim投影・固定失敗六Source 独立単体テスト仕様

PG-D1129/NK-WEB-002/NK-MSG-001/NK-OPS-001、AUT004/MQ008010、QA050/UI226231251・SS314§10/331/321§7/343§6/352。HEADd541892cb719d15119abf2a19a837c8b84cb181d/dev-foundation、Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備。群18270着手前1/3/6pp cap10、F03担当/元ownerP01505/P00604/P00502/P01801参照費0、Main製造0。

ClaimedRevocation/RevocationFailureCode/WebLogSendException/CommittedFatalReplyException/ServiceCredentialException/InspectorCredentialExceptionの六Main全bodyを読取済み。Claimedのcallee PendingRevocationRepository.microsecondsはnonnullとnano%1000だけ、三static fieldはcompile-time int・元normalJar bytecodeにclinitなしをdc31d8で確認。SQL/claim/read/retry methodは呼ばない。Identity/EncryptedPayload全bodyも純regex/clone/不変値、aad/crypto未実行。constructor例外を発生させるだけでcredential読取/実send/commit/隔離やリカバリを行わない。

公開固定UUID・Instant・版PUBLIC/OTHER・合成配列29byteのみ、真の暗号包絡は101..116byteであり29成功を真正ciphertextへ変換0。null payload/expiryは既technical表現として保持し、context捏造・実失効送信・既知期限への補完をしない。Claim leaseの所有権や安全な実処理の認証ではない。実DB/Graph/HTTP/JMS/鍵/file/native/VM/permit/worker/clock0、一般JDK初期化IO未知null。

|REVOKE-VALUE ID|入力/操作・独立期待|
|---|---|
|001|attempt0/payloadnull/expirynull・lease=requested+1秒、七accessorは元public値を保持/redaction固定。unknownを現在有効/無効へ補完しない|
|002|attempt100/同版payload/既知expiry=requested+1µs・lease+1秒を保持。expiryがleaseより前でも当値型は期限判定しない|
|003|payload版不一致、空白/空/17byte/null版を拒否、暗号を実行しない|
|004|attempt−1/101/整数両端拒否、0/100は001/002|
|005|lease時刻等値/過去/sub-microsecond/null・owner/identity各nullを拒否|
|006|known expiry等値/過去/sub-microsecond拒否、未知null/正順は001/002、leaseとexpiryを勝手に同一化しない|
|007|Failure enum七閉値・順/未知/null拒否、values配列変更でcatalog不変|
|008|WebLogSendException二constructorの公開message/null/cause保持、送信0|
|009|CommittedFatalReplyExceptionの固定messageと元cause/nullの保持、DLQ/commit/通知0|
|010|Service/Inspector credential例外の固定message/causeなし、実private file/鍵読取0|

Testは新RevokeProjectionValueContractTest十method一exec、元DB/Graph/authority Test method/fixtureの抽出・改作0。独立期待はSSのcount100/unknown保持、手書き時差/固定数/固定messageと明示enum表で作りProductionからexpected生成0。immutable値の共有更新/並行/再送は当単体では非該当、元retry worker/backoff/lease CAS/DB試験を免除しない。

18270 raw→18272同exec/Source closure/XML/session/CRC/counter→18274独立metadata否定・十oracle/TestCRC→18278/80 registry→18282/84 WBS二面→18285 binder、3481結果。normal14216/static14224/JDK25.0.4同byte再利用/成功全回帰と署名再演0、FESabort0/時刻/環境/branchHEAD/command/入力/Main/helper/Test/physical/XML/exec/hash/exitはmanifest。未実測は不明、自然B0を四100へ換算せずmanual除外0/公式filter維持。修正前BUG/YKT起票。正式1964/53/歴史17/190/工数null/QA051final/G07G13F03/451/全HOLD不変。
