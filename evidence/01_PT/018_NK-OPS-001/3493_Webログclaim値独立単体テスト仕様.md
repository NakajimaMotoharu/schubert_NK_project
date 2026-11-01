# Webログclaim値 独立単体テスト仕様

PG-D1135/NK-MSG-002/MON003/MQ008/UI242/SS324§9・331§9.3/352、対象ClaimedWebLog全constructor/requireWorker/getters/toString。HEADce284deb86508071d03cf913ce94344f2e49bc9a/dev-foundation・source6b53/normal14216/static14224同Mainbyte。群18380事前.75/2/4pp cap10、主F03/元ownerを485から保持。Source/WebLogPayloadIdentity/EncryptedWebLogPayload全本文と初期化を読了、AAD/暗号/鍵/DB/repository/再送/claim/worker権限獲得を呼ばない公開合成不変値のPT_DEFAULT。

新WebLogClaimValueContractTest WLGCLAIM001..006全六件一suite、既WebLogOutboxRepositoryやreplay whole/fixture/method抽出・改作0。入力はUUID(0,91)/(0,92)、public版PUBLIC、29byteの単なる合成配列、固定Instantだけで実暗号包絡/署名/lease所有証拠でない。constructorが持つN12 ID1..999999999999、attempt0..100、worker ASCII英数字/点/下線/hyphen長1..64/nonnull、全必須項目nonnull、固定redactionを独立literalから確認する。

001 正常上下限ID/attempt・全getterは元不変値/時刻/workerを保持、認証や現在claim成功とは認定0。
002 ID0/負/max+1→固定範囲例外、max許可を別正常caseで確認。
003 attempt負/101→固定範囲例外、0/100許可を別正常caseで確認。
004 worker一文字/64文字/点下線hyphen許可、空/65/空白/制御/非ASCII/slashは固定拒否、static helperは入力と同一Stringを返すだけ。
005 identity/payload/nextAttemptAt/createdAt/worker/leaseUntilの六nullを一つずつNPE拒否、正常扱いcatchを製品へ追加0。
006 固定toStringはid/UUID/合成配列/lease名を出さず、payloadへの入力配列変更は元Encrypted値へ波及しない。構造の共有更新/並行/再送は非該当、実worker数0。

期待は手書き範囲・固定message/literal・固定Instant/UUID/明示byteで、Production getterでexpected生成0。cloneはhelper構成/返却の実行true、crypto/provider/実token/session/credential/file/DB/JMS/HTTP/Graph/Root/native/VM0、一般JDK初期化IO未知null。Own javac/JUnit/JaCoCo/slot/XML/execのみ。normalJar全Source closure/CRC/一exec/四counterを18382で測定、18384独立oracle/metadata否定/TestCRC後にregistry/WBS/binderへ結合する。結果3494に実command・日時/環境/branch/source/hash/exit/counters/BUGを保存。未実行/例外不足や他sourceの成功を合格へ輸入0、公式filter/分母/上位期待変更0、正常全回帰/署名の確認再演0。正式1964/53・歴史17/190・工数null/QA051final/G07G13F03/451/全HOLD維持、新WBS受入/新製造0。
