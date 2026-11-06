# FormCsrfTokenRequestHandler メモリ境界 実行結果

2026-11-06T13:07:58.652074+09:00 NK-WEB-001/WBS-P015-02、仕様052/PT-WEB-CSRFPORT001..009全9method成功/FESabort0。MainD8不変更、Test/source db61a3f8097203bdad92d772af34f50e7f931b8b、branch dev-foundation。PG20408/strictpost0、LINE19/19・METHOD3/3・CLASS1/1・BRANCH12/12全miss0/physical1・normalCRC/単一session一致・除外/旧exec合成0。manifest evidence/01_PT/015_NK-WEB-001/evidence/PG20408-form-csrf-request-nine-v1/manifest.json SHA256 f14f5f83428bfbd75ef3c2611d45c292c0d934ec61e436e9a62c707bf0342eecへ実command/時刻/input/dependency/元XML/exit/counter/hash、environment.safe.jsonへ元XML hash/OS-JDK許可property exact結合（Linux/Java25.0.4）。shared012/profile070、compile20404=0、static20406 rawPMD6/CS0/parser0/個別適用違反0/抑制0。正常20112/SB20114 exact1844指摘0は確認再演0。

全9はmemory Servlet属性/固定placeholderのみ。handleは_csrf/class-name二属性の同じlazy wrapperでsupplier未読、getter参照時に固定値を供給、nullableAPI五境界を拒否。resolveは渡したCsrfToken getterを読まず、64/128/schemaalphabetとnull/多値/null要素/不正短長を独立literalで照合。queryの正確_csrf/percent decode/壊れescapeはbody読取前null、別case/unknownqueryはbody値を保持（parameter名case-sensitive契約）。deferred null/failureをvalid値へ変換せず、body内IllegalArgのnull化とquery取得外側例外/fatal/非対象例外の透過を区別する。共有handler2worker8request・10秒joinで各属性/値非混在を実測。

Source app初期化handler/WebCsrfToken/新Testだけ、Cipher/SecurityContextHolder/storage/bootstrap/Artemis/Netty/Hikari/Micrometer無し・held4 probes0。WebCsrfTokenはparse/schemaだけ、generation/matches/実token/鍵/実session/store/CSRF認可/HTTP/DB/VM/Root無し。SpringSecurity7.1.1委譲bytecodeはlazy属性/supplier参照のみと事前確認、SDK/JVM metadata/native数は未測定null。出力は要約とhashだけでraw actual token/credentialを保存しない。

BUG2330/YKT2075はProxy getParameterValues4literalの一規約指摘を修正前起票、METHOD_PARAMETERS定数化のみ/inverse byte（format前）一致/期待値不変。原20402 raw7保持、最新20406 raw6はconfined Map1・JDK defining-loader2・Proxy identity equals1・自己所有pool2を各非該当確認、同rule0/CS0/抑制追加0。是正Test commit db61a3f8097203bdad92d772af34f50e7f931b8b push0・全9/四100/post0で有限CLOSED、旧staticをPASSに正常化しない。

4003/4004訂正→4005原0.5/2/4pp cap6、真正終端後fresh共有1pp/ordinary25-all32/S7残3/第一V同HOLD、専有N/Tnull。各source技術55→56、元282交差36→37/残245、partial80結合17/残63不変。直近十二対象137unique=Java111+HTML26。正式1964/53・歴史17/190・新leaf0・工数null/全451/実CSRF・session/native/CHR/Root未受入、詳細969/970。後続独立PGPTへ継続。
