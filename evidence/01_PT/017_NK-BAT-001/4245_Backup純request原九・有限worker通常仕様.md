# Backup純request 原九・有限worker通常PT仕様

NK-BAT-001/NK-OPS-001、BAK/BKO/UI251/SS3416.1/343SSC092116/354、BUG2862/YKT2387。費用F03追加 .3/.9/1.8pp（有限worker製造 .1/.3/.6、通常資格 .2/.6/1.2）、cap3。既S/V・元費・全体正式認定不変更。

対象は公開BackupWorkerRequestとVerificationの純値/byte codec、全source1/物理2。既wholeBackupWorkerRequestTest全9は抽出/選択method実行せず一クラス。実native/DB/Backup・credential・ファイル・Root・Unit・intent/permit/権限操作は含まない。新Test定義0。原byte・日時・canonical文字列・arraywipeの全期待値を保持し、32taskの待機をsubmit/Future.get5秒/finally shutdownNow-await10/assertへ限定変更する。旧invokeAll/get/TWRcloseの無期限待機は用いない。

下表の2862接頭Test IDは今回sourceの一意追跡aliasで、既BREQ001..008の歴史IDを再割当せず、新試験定義数へ加算しない。BUG2862の初期009記述はmethod名が正本で、現alias009の並行methodへ接続する。

|Test ID|method|独立期待値|
|---|---|---|
|PT-OPS-BREQ2862-001|genuineVerificationProfileLiteralAndClosedInvariants|手書きNKBACKUPVERIFY1/run/started/manifest_sha256/dump_size/dump_sha256/最終LF、abc固定SHA ba7816...15ad、3byte。新規profileとの相互混同/field差替/符号先頭0/overflow/nullを拒否、全byte消去。|
|002|literalCanonicalAndIndependentDirectory|手書きNKBACKUP1/run/started/LF、固定JST directory 20260927-235959-UUID、全owned byte消去。|
|003|dateAndMicroBoundaries|JST年0001開始は歴史LMTでUTC0000-12-31T14:41:01Z、上限9999-12-31T14:59:59.999999Z、各外1µs/Instant上下/1nano拒否。|
|004|everyNullAndValueInvariant|run/time/owned null拒否、zeroUUID拒否、失敗owned全消去。|
|005|missingExtraAndFixedFieldOrder|magic/keys/順序/余剰欠落/terminalLF変更拒否。|
|006|asciiAndBoundedBytes|0/160/161/401byte不正fixture、0/TAB/CR/control/DEL/nonASCII拒否と消去。|
|007|uuidAndTimestampNoncanonical|UUIDalias/大文字/不正、時刻offset/余剰µs/nano/年10000を拒否。expectedをproduction encodeで生成しない。|
|008|ownedByteMutationDoesNotMutateRecord|consume後入力は所有解放済み、後変更が不変値へ伝播0、返却encode配列間も非共有。|
|009|concurrentIndependentConsumption|独立32入力/同じ手書きgolden/全消去・true、各Future5秒、finally全所有worker shutdownNow-await10/assert。|

JDK/JSpecify/JUnitだけの閉scopeを先に証明し、旧9の全golden・入力・assertをコード逆変換で保持する。prestyle→Java25 RootNullAway/lintWerror→全PMD/CS/SB実物理2→preflight→Git固定→一whole9→独立post（全XML/FES0/単一exec/CRC/初期化/四counter）を実施。既定JaCoCo指標と実JVM Code method数を別記し、生成code方針/全F03/451・実Backup/親所有の認定を代行しない。未網羅/未実行/失敗を合格にしない。
