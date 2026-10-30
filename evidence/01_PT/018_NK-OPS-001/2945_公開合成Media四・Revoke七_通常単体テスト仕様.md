# 公開合成Media四・Revoke七：通常単体テスト仕様

PG15534/PG-D946、Production6b53/normal14216固定、基点05192f3bce060f28a3bf6d94d6589f77c0dd749d、群3324開始0.75/3.5/8共有枠pp固定。原MediaResponseDecoderTest全4/PT-MED037～040とRevocationPayloadCodecTest全7/RERUN003a～gを一fresh JVMで実施。原Test/期待値を改作・抽出せず、現cohort未登録を先行確認。旧2150/1190/1189の別source5fce/7be成功は歴史参照だけで新sourceへ合算0。正担当P00904（media二Source）/P01505（revoke四Source）、群主費用はP01505一回、関連追加0/配賦実費null。

全Main/Test/helperを事前読了。六Source十Codeを通常Jar/現在/snapshotのbyte/CRCと照合する。media decoderはBinding/Result、二例外はReason enumを含む。未呼出decodeVerified/retryAfter等は未達のまま、例外型/innerclassを除外しない。原11とXML/FES/flaky/not-run/単一session/exec/元JVM環境を検証、独立postでは元Product再演0。

関連NK-MED-001/NK-WEB-002/AUT004/MQ004020/FIL006007、UI226/231/232/234/235/237、SS314/331/333§8/352§11.2、QA050/SSC171/PG-D359。media期待値はUI232の256header、UI235 MEDIA1024/VID1808 byte offset、七format/MIME/path、size1/999999999999、成功0000/0200、十error code、全異常header/認証context/length/NFC/UTF8/mismatch/100有限並行の明示literal。実fileを開く処理は呼ばない。

revokeは既公開固定key0..31/previous32..63、noncea0..ab、公開UUID001122...、Instant2026-09-08T00:00:00.123456Z/context0123456789abcdef×4のみ。expectedは本番encryptを使わず原独立JCA/lengthprefixで構成。purpose web-revoke/table schubert_web_session.pending_context_revocations、UUID16byte、epoch1788825600+nanos123456000の12byte、format1、versionを六個のbig-endian32bit lengthprefixでAAD化。NKENC1/format1/version長1..16/nonce12/cipher64/tag16、envelope101..116。新独立Node/OpenSSL public goldenを同parameter/Python AADと照合し、本番captureとは称しない。

current/previous/未知/各AAD改変/session目的不一致/全envelopeヘッダ長nonce-tag-平文変造/null/版名/鍵長/微秒/close-借用同期/100freshnonce/復元を原wholeで確認。自所有の一時JVMだけSunJCEをremoveしfinally同位置へ復元、実provider設定やtargetprocessへ作用しない。crypto/publicSyntheticTestKeysはtrue、actual secret/credential/auth発行/DB/VM/service/files/Root/Graph/鍵退役0。shallow getCause/getSuppressed確認はGraph探索ではない。専用post15536を実行前に固定、反例/限定effect/不足/環境/command/hash/BUGは2946へ。正式1964/53・歴史17/190・工数null/QA051final/全HOLD不変。
