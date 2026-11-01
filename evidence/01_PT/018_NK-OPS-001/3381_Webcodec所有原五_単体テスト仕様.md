# Web codec所有原五 単体テスト仕様

PG17370/event3639/PG-D1086、source6b53/HEAD32e69effe31f7011636ec08644ab0df696ed5092/dev-foundation。事前2/5/9共有pp cap10、主F03/canonical owner保持。Program WebNativeCodecs create(KeySource)/session/log/revoke/close、RD AUT001/MON003/SYS004/UI226242253/SS314324343352/NK-WEB-002/PG367。
原whole WebNativeCodecsTest五件、Main全152行・Test全276行（実行manifestの原byte/hashを正とする）と各fixture/手書AADをレビュー。既current純粋child codecの15568(Session)/15552(WebLog)/15536(Revocation)証跡は対応Source四100として参照し、aggregate15536は他partial Sourceを含み全体四100ではない。元child試験は再演しない。

|Test ID|method|独立期待値・境界|
|---|---|---|
|PT-WEB-NKEY005|nkey005ThirdPurposeCopyNullFaultAndIndependentCipher|第3key copy/null/31byte/version/null-version/fatal失敗、先行二buffer消去。公開byte129..160固定keyで手書LP-AADとJCA独立復号、NKENC1 prefix/102byte/offset10 nonce12、22からcipher80、plaintext b64|
|001|nkey001CopiesErasedButBorrowedCodecsSurviveUntilOwnerClose|公開copy消去、owner保持中借用可、二重close、閉鎖後session/log/revoke/borrowed利用拒否|
|002|nkey002NullMissingSecondCopyAndInvalidLengthFailClosed|null依存/初回・二回目取得失敗/各31byte、取得buffer消去|
|003|nkey003PurposeOrderAndVersionFailureNeverUseFallback|固定SESSION→LOG→REVOKE三目的順/version失敗、既取得buffer消去|
|004|nkey004ConcurrentBorrowAndCloseHaveOnlyOwnedOrClosedOutcome|自己pool2/submit一task/read最大100、close競合で借用成功又はclosed、5秒有限待ち、最後close|

PT_DEFAULT：public決定的key fixtureだけ、KeySource注入overloadだけを呼び、ServiceCredentialSet reader overload/実鍵file/権限/nativeは使わない。JCA AES-GCM/SecureRandom nonce・UUID.randomUUIDを使うのでcrypto=true/entropy=true、秘密key読取りfalse。自pool宣言最大2thread/1task（実生成数は未測定null）、OS/VM/DB/Root/外部session/HTTP操作0。API NativeCodecs6は別wholeで実credential FD/held codecsを使うためHOLD/部分抽出0。

command: python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17370_web_codec_owner_five_pt.py
原whole五だけfreshcompile/一JVM/session/exec、全Main三physical＝Code二/KeySource NoCode一（未実行reader wrapper $1も分母保持）。FESaborted0/actualOSJDK/XML/source/hash/終了・全分岐を独立post。合成入力で暗号を実行しても実credential/key rotation/native readiness/451成功とはしない。実行前なので結果/coverage未確定。case expectedを製造methodで生成しない（session roundtripは借用寿命用、binary暗号oracleは独立AAD/JCAと既child証跡へ分離）。
