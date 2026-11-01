# Inbox保存値四Source 独立単体テスト仕様

NK-MSG-002/DAT009、PG-D1123、SS324§3.2/6・SS352§11.2、UI241242。群18170は事前0.5/2/5pp cap10固定、primaryF03/元owner参照費0、Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備・HEAD4d486929dd463b149973c4abb627f5d77170d157。PG責務は維持、当Mainの製造追加0/既値契約の不足PTを補完する。

Fingerprint25/Verification8/EncryptedResponseSnapshot36/BoundInboxExecution21行の全Source/全calleeを読取、四Source四physical。実HMAC/AES/キー読取/keyring/ResponseSnapshotCodec/DB/ファイル/Root/VM/native/時計/worker/API業務実行は一切なし。公開配列0x33/0x55、version label、固定UUID(0,77)と既InboxExecution.inProgressのOptional.emptyだけ。実ciphertext/鍵/credential/tokenを使用・保存しない。字句上のsecurity語で除外せず、実動作が配列clone・構文・長さ・nonnull・enumだけであることからPT_DEFAULTとした。保留BoundInboxExecutionTestのBeforeAll実DB/暗号fixture/methodを抽出・改作0、元Codec/HMAC wholeの代替受入0。

後続2957/2958は既InboxExecution等の別Source/HMAC成功を参照、当四Mainは現registry18158の全Source未登録であり同成功を再演・流用0。新StoredMetadataContractTest六件一suiteは独立に作成し普通5786の消化へ算入しない。

|ID（method末尾番号）|入力・操作と期待値/独立根拠|
|---|---|
|STORED-METADATA001|version一文字英数字/通常/16文字、公開32byteをconstructor後とgetter後に変更。保持digestは全0x33、getterは別配列、version保持/固定redaction。32=SHA256の256bit/8、hash計算は行わない|
|002|version/digest各null、空/不正先頭/空白/slash/LF/Unicode/17字、digest0/31/33をNPE/固定IAEで拒否。16字上限はSS352のkey-id・許容syntaxは既内部値契約|
|003|合成byte長29/30/1049999/1050000、両端0x33/55を元/返却変更後も保持、version16字/通常とredaction。1.05MBはSS324、29は内部格納metadataの最小構文guard（暗号包絡の完全性/最小envelope/復号可能性の保証ではない）|
|004|null/version上記不正と長0/28/1050001を固定IAE/NPEで拒否。実暗号の正誤をこの形式検査で認定しない|
|005|固定Message UUIDとinProgress objectの同一参照、null各拒否/固定redaction。保存messageと戻り値の値だけでowner/Inbox NEW/実行許可/DB replayを認定しない|
|006|MATCH/MISMATCH/KEY_UNAVAILABLE三enum名・順序・valueOf/未知/null。実key欠落・HMAC照合成功ではなく閉じたcatalog契約|

期待値は手書き配列/byte/長さ・仕様/独立文字列、Production getterをexpected算出に呼ばない。正常/境界/異常/null/防御copy/固定redaction、可変共有状態/通信がないため並行/再送非該当、実業務試験を免除しない。literal bytesは非秘密の合成値でありraw認証/session/tokenではない。

正常14216/static14224/JDK25.0.4・全Main hashを再利用、成功全回帰/署名の再演0。新18170一exec→18172全closure counter（branch自然0は別）→18174独立oracle/metadata否定→18178/18180 registry→18182/18184 WBS二面→18185 source/run結合→3467。真正exit/FESabort0/OS-JDK/command/branchHEAD/input/test/class/XML/exec/session/CRC/hashを元manifestへ。未達は除外せず記録、code/coverage/正式/費用の別domain保持。正式1964/53・歴史17/190/新WBS受入0/工数null・全HOLD/QA051final/G07G13F03/451維持。
