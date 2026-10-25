# Snapshot乱数異常時buffer消去・実行結果

2026-10-26、1993/PG-D674/BUG1771/YKT1522、WBS-P006-01/群2248。修正source **21d7c30425e7aa9ce435e808035a94fa4d75c93b**、dev-foundation。**既Codec7＋新RNGSCOPE2の全9件/2suite成功、F/E/S/aborted/flaky/not-run0。全ResponseSnapshotCodecのL154/M14/C1/B70は各100%。** 新2件は乱数providerのRuntimeException/Error後の自所有nonce消去・同一例外・caller入力不変を独立固定期待で確認した。全PGPT/同source全scope/実native/CHR/正式完了ではない。

## 実装・修正前との区別

元source8ba82083/normal9812の9864-witnessは真正exit1、RTE/Error両方でnonce消去false、例外identity/caller入力不変は真。通常PASSへ加算0。修正はsecureRandom.nextBytesを既tryの先頭へ移す一箇所＋comment、新Test一source二method。乱数順序・正常ciphertext/圧縮/nonce長/AAD/鍵世代/例外型・外部wire/DB/retryを変更していない。既7の固定nonce独立JCE/圧縮/AAD・最大/旧鍵/tag/不正圧縮/null/lifecycle/AES unavailable/質問scope frameは当新sourceで必要回帰として実施し、旧sourceの成功を転記しない。

9876は元9812との全六Jar展開entryを比較し、Main1843中Codec一classだけ変更・他1842/五module全entry同byte、旧1916Test class全byte不変＋新2（計1918）を確認した。Main source差分はprovider呼出しのtry内移動だけで、他method/source契約を変更していない。現在Java1796/Main965/Test831。新sourceとTest追加の担当登録は後続G13で行い、旧8baの1793/1795測定を現数へ推定更新しない。

## 品質・横展開

新sourceのnormal六module compile/package/NullAway・lint・format等の既build gateは成功、PT実行0として区別した。Codec全unit SpotBugs指摘/処理error0。変更Main/TestのCheckstyle0、新Test PMD0。**PMD raw3/実exit1を保持**し、次の当source適用性を独立class/JDK/sourceで確認した。raw0や全F03合格とは報告しない。

- HardCodedCryptoKey一件（constructor line57）：実keyはconstructorのbyte[]入力を検証/cloneする。文字列currentKeyは診断labelで鍵本体ではない。既1108の限定理由を当sourceの実statement/validateKeyへ再照合した。
- CloseResource二件（compress/decompress）：scratch配列がnative Deflater/Inflater constructorより先、各native取得後の処理はfinallyでend()を実行し、normal/exception両endを当bytecodeで確認した。JDK25.0.4の両close()はend()を呼ぶ。既BUG1453是正後のmethod sourceは今回変更0。PMDのclose呼出し検出不足に該当するが、旧1132の修正前gap/未完を消去せず区別した。

YKT1522のProduction nextBytes全8を字句的try/catch/finallyとArrays.fill対象の組で確認。該当はSnapshot Codec一件。AuthContextCodec、AuthSessionService、WebLogPayloadCodec、RevocationPayloadCodec、SessionPayloadCodec、WebSessionId、WebCsrfTokenの七件は既にprovider呼出しと同じ自所有bufferの消去finally内で非該当。原path/hash/呼出・try/finally行/buffer名をrng-scope-review.jsonへ保存し、検索だけで完了としない。new Codecは当JDK bytecodeのprovider PCをany handlerが保護することと、同finallyでcompressed/nonce/AADを消去するsourceを照合した。新2の実failure後条件を再発防止にする。

実鍵/credential/DB/HTTP/JMS/VM/Root/permit/intent/配備/私有raw/native保全物/Graph9操作0。固定公開合成key/nonce入力を使い、公開resultは消去/同一性等のboolean・件数だけ。JVM/JCA内部copyの物理消去や、全heap allocation Error一般の保証はしない。

## 証跡・command

Linux amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4 platform1.13.4/JaCoCo0.8.15/ASM9.10.1。各manifestに実command・開始終了時刻/環境/source/全hash/exitを保持。以下は本Program evidence/provisional配下で、commandは同名tools/quality Python entryをfull PYTHONPATHで実行する。

|証跡|実結果|manifest SHA-256|
|---|---|---|
|PG9864-snapshot-nonce-scope-witness-v1|元source真正1/二障害再現、PASSではない|7d46a9f0deebcb1e600c7803ca807d6149cb4b2ad93a5f5c97afaefd08ba848d|
|PG9866-snapshot-nonce-six-compile-v1|六compile0/PT0|2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535|
|PG9867-snapshot-nonce-preflight-v2|9method/2suite/5Testclass/全source固定0|be7c2e31d2dc9074dd35eb50d59b27ffe694ef8c3f28418e27258cfc889e630e|
|PG9868-snapshot-nonce-host-v1|単一run9/2成功/真正0|5bdde82ac463edabe892c872e0081344cdc176738decca475f51bf7b39d8b0e6|
|PG9870-snapshot-nonce-post-v1|全XML/実session/CRC4acb372a60384dd1/全unit四100/0|12f63783cc61bdf8e0605c2644da90e860d26bcf867e7a3add9882e8f559e23f|
|PG9872-snapshot-codec-static-v1|Codec SpotBugs0/処理error0/真正0|f2d3fcafd1525f8f8a75c9421cc221918982f670eba47d9af45919425770e8ae|
|PG9874-snapshot-changed-source-static-v1|PMD raw3/処理error0/CS0/真正1を保持|a97e2167ec9e923dc3de12e84ae4f32f43bbe195f5379d8a9017ded1a1a41723|
|PG9876-snapshot-nonce-quality-source-post-v1|全byte差分/八scope/PMD3適用性/件数六反例/真正0|00eb2fb3eb8d9cb763e7a2a91eb0aa0352eff63ba17725b5f305d75a7e939f48|

9870の公開XML二件・coverage.txt/manifestをTestID対応の結果とする。raw execは固定host runに保持、旧source execと合算0。対象source/runが違う成功は歴史参照だけ。

## 工具手戻り・既記録訂正

BUG1772/YKT1523は旧Cleanup9814v2のbegin20/4と実4/1の不一致。元3aba4944を上書きせず9876のlegacy-cleanup-begin-correction.jsonへ4/1の追記訂正を保存した。元4件成功/coverage/旧費用は不変・再演0、新結果へ加算0。現nonceはprepare/begin/launcher/XML/post全層9/2、旧4/1・20/4、suite誤り、not-run、bool/string値の六反例を拒否した。

BUG1773/YKT1524は9867v1がthrows Exception付き宣言のjavap表示を誤拒否したpreflight1（元sha3baa9ceb）。JUnit前/OUT前で元metadata stdout未保存を明記。別V2は既検証済みbinary decoderでname/descriptor()V/Codeを照合し、例外宣言の表示依存を除いた。旧throwsなしCleanupは非該当、当throws有無を含む全9の実descriptorと実JUnit9を照合、ビルド/JDK試験の確認再演0。

BUG1774/YKT1525は9876初回事前pyflakesが未使用copyを拒否（entry前1、元source sha cfa599f3ac79a58cabedb5d1fae7d5755ec4699efd8286abcba4b08a4e903edb）。除去後静的0、entry前レビューでJar→snapshot親indexを正しい3へ是正し、全source/hash/nameを確認した。元preflight/hostは明示snapshotで非該当。実製品PT再演0。いずれも通常工具不備でplatform拒否ではない。

BUG1771/YKT1522は修正commit21d7c3042・元二再現/新9全成功・八対象/当静的適用性・全byte差分で**UNIT_SCOPE_CLOSED**。工具1772～1774/1523～1525は検証済み保存commit待ち。未較正の原/v3/v4/v5・開始1/3/8ppは固定、共有消費/実token/工数を混同しない。正式1964PT/53scope、個別17/190、QA051final、工数null、Graph9動的/全actualHOLD/G074493/全WBS監査HOLDは不変。次は当新Test/変更Mainの原owner P00601でtrace補足・通常PG/PTを継続する。
