# メモリ入力・CSRF二Test三境界命名

2026-10-28 / PG-D750 / BUG1988 / YKT1736。着手source2388535ba28c3dd359ea4075fea2785d2da066b0（Main/Test基点4749755f2）。群MEMORY_INPUT_CSRF_THREE_BOUNDARY_NAMING、低2/標準5/高8・上限10週次共有ppを着手前固定。主費WBS-F03、元artifact担当P018-01/P015-02は変更せず参照費0。実N/T・専有費・工数率null、原/v3/v4予測は不変更。

## 対象と独立期待値

- InspectorDbCredentialTest原4method全件：PT-DB-INBOX-193..196、NK-DAT-001、DAT009/OPS009/UI212241251/SS343§6.6/352§11.1。公開ASCII/Unicode（NFC強制なし）・0/65536/65537byte・LF/CRLF・不正UTF8/制御byte、独立文字配列、入力消去/コピー隔離/REDACTED/close競合を既literalで判定。ifの65536だけMAX_INPUT_BYTESへ移す。
- WebCsrfTokenTest原4method全件：PT-WEB-032..035、FUN001/AUT004/UI226/SS314§7.2.1/8.1/352§3。固定0..31byte→手書hex、全64..128長と先中後不一致・63/129/100000境界/null/不正文字、ProviderExceptionの非漏洩/消去、自己生成100件の独立性。ifの64/128だけMIN_TOKEN_LENGTH/MAX_TOKEN_LENGTHへ移す。expected側の数値・hex・wholemethod/controlを不変更。

PT_DEFAULT。両Main/Test全文とhelperを親が読取り、依存はJDKのmemory/UTF8/regex/MessageDigest/HexFormat/ReentrantLockと自己poolだけ。CSRFのSecureRandomはJDK標準CSPRNG、生成値は一時メモリだけでログ/Gitへ保存しない。実credential取得/DB/HTTP/Unit/Root/Graph9/FFM/VM/native/permit/intent/Backup操作なし。拒否/HOLDのTestを切り出した代替ではなく、別whole二Test。scopeを探る試し実行なし。通信先なし・権限変更なし。

## 実施と証拠

三typed定数/三if参照の独立token逆で全元期待値/全helperを保存、非同値負例を先行。新sourceを固定し六module正常compile（format/null/lint/Werror・PT0）→exact whole8を自己空CWD・固定ja-JP/JST・単一JaCoCoexecで一回→二TestPMD/Checkstyle→XML/終了/物理全Main1843byte/全Test/CRC/完全bootstrap117・web358分母と明示許可外probe0の独立post。原六Thread指摘は保持、抑制追加なし。固定pool12/10の各100callback/close競合、get5/20秒、invokeAll/TWR局所無期限と外側JVM240秒を区別する。

工具はchecked一file入口でlint後のみ実行、元source成功を新sourceへ合算せず失敗版は不変保存。全coverage不足はmissedをそのまま記録、Main不変更でも旧exec/旧native資格は転用しない。trace原983行は当二SHAだけ更新・原owner/予算/受入維持、全WBSの既HOLD1は成功へ変換しない。静的是正は原三IDだけ、全F03/451/正式1964-53/個別17-190/QA051finalは未変更。結果/環境/実command/exit/hash/BUGは2361と専用公開manifestへ記録する。
