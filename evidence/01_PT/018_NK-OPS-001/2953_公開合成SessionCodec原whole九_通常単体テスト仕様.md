# 公開合成SessionCodec原whole九：通常単体テスト仕様

PG15566/PG-D948、Production6b53/normal14216固定、基点a76fe3bb4b8e21a93636e2f8381a1d9e2176dd14、群3328開始0.5/2.5/6共有枠pp固定。原SessionPayloadCodecTest全9（WEB016～023＋TOKV206）を一fresh JVMで実施。全Test/対象Main/Identity/Encrypted/既例外、呼出される既JSON Test helperの全静的fixture/初期化を事前確認。target3Source3Codeは現registry未登録、既例外二CodeとJSON codec一Codeの旧資格は再受入しない。Main正担当P01501、原Testは既ownerから推定せずUNKNOWN維持。

NK-WEB-001/NK-AUT-001/FUN001/AUT001～004/UI226242/SS314§7.2.2/331§9.1/352§11.2/SSC039/QA049。目的は独立JCA/lengthprefix golden/copy、current-previous-unknown、旧JSON v1読戻し/current v2、包絡/全七AAD/row/tag変造、認証済みだがschema不正JSON/UTF8/最大16384、null/版名/鍵長/微秒、close/borrower同期・再起動previous、100nonce/自JVM provider故障復元。expectedは原手組みJSONと独立JCAで、本番encodeをexpected生成へ使わない。

公開key0..31/previous32..63/noncea0..ab、UUID00112233-4455-6677-8899-aabbccddeeff、sessionIdHash a×64、Instant2026-09-08T00:00:00.123456Z。AADはweb-session/table schubert_web_session.web_http_sessions/UUID16byte/hash64/time12/format1/versionv2の七big-endian長prefix。平文はv2の匿名/合成principal reader-ADMIN/context b×64/CSRF c×64/savedRequest /logs?q=日本語/公開QSB token0001/issuedAt2026-09-08T00:00:00Z。これは実cookie/session/token発行やauthorizationではない。Node/Pythonで両JSON・AAD・GCMを別実装し、原JCEの全parameterと照合予定。

原SessionAttributeCodecTestは既資格の未変更全source（SHA54c9a088）を静的helperとしてcompileするが、その既7methodは選択・再実行しない。Fixture抽出/改作0、Junit選択はSessionPayloadCodecTest9だけ。全normal/現在/snapshot/hash/3Code CRC/一exec-session/XML/FES/flaky-notrun/元JVM環境と四counterを検証、専用post15568と独立15570へ結合。不足は保持し除外や人工呼出しをしない。

crypto/publicSyntheticKeys/自JVM JCA復元true、actual key/credential/実session-cookie-auth発行/DB/file/service/VM/Root/Graph/鍵退役0。helperはメモリJSONだけ。元baseline/旧成功/正式1964/53・歴史17/190・工数null/QA051final/全HOLDを保持。実行はpg11123_checked_python_entry.py経由pg15566_public_session_codec_nine_pt.py、source/環境/command/実結果/hash/BUGは2954へ。
