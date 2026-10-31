# 固定公開署名vector原whole八・単体テスト仕様

2026-10-31、Production6b53/normal14216/dev-foundation/HEAD70459982024f9b20196927386b41c4bbf9bd80e8、PG-D1032。NK-OPS-001/SYS002004/OPS009/DAT009/UI212251253/SS343§11.1/SSC096、先行153のSIGN001～008。主費WBS-F03/canonical責任は485規約・参照追加0、着手見積1/3/6共有pp cap10固定・実専有費/N/T/工数率null。

原ReleaseSignatureVerifierTest全171行8method/Main78を全文確認。期待はRFC8032§7.1 TEST1/2の固定公開key/message/signatureだけで、公式原典 https://www.rfc-editor.org/rfc/rfc8032.html#section-7.1 を2026-10-31閲覧し公開部分を照合した。RFCのprivate seed部分は使わず、原典全文やprivate部分をGitへ保存しない。Production signer/verifyをexpected生成に使わず公開tupleの独立hashでoracle出所を結ぶ。

正常二vector（空/1byte message）、message/signature/別公開key改変、DER44byte/固定prefix/0・43・45/null、signature0・63・64・65/manifest1MiB・1MiB+1、元入力copy/所有copyfinally消去、既知GeneralSecurityExceptionの固定IOException/cause無し、未知Runtime/Error identityと消去、自己所有四task・5秒有限待ち/良否八call・不正point/signatureを原wholeで確認する。JDK/JCA内部copyの物理消去は保証外。

通常JVM/JCAで固定public keyをdecodeしてverifyする実crypto処理は実行するためcryptoInvoked=true/publicKeysDecoded=trueを明記。秘密/運用key・credential file/KeyStore・keypair生成・sign・運用署名/承認発行・実release/配備・Root/VM/DB/JMS/permit/intent/回収/退役/Graph9/私有raw操作は0。TestのNativeProviderという名称はJDK署名検証であり実VM/native所有手順ではない。安全HOLDの解除・保留whole抽出・未知操作probeは行わない。

全1Source3physical（outer/NativeCrypto Code二、Crypto interface真正NoCode一）を残して単一exec/session/CRC/四counterを測る。Source/Test変更・新ID0、前source結果転用/coverage除外・union0。current2252にcase/対象Source参照無し。checked16524→受動16526→独立16528→registry/WBSの予定。F/E/S/flaky/not-run0、command/環境/時刻/source/archive/終了/XML/hash/coverage/BUGを公開manifestへ保存。四held/六native/Root回収27は受動probe検査。原八再演0、正式1964/53/歴史17/190/QA051final/451/工数null/HOLD不変更。
