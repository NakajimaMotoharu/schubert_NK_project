# 公開CanonicalField・AAD二Source 独立八 単体テスト仕様

2026-10-31 / PG-D987 / 群PG16082 / 主・費用WBS-P006-01 / 開始1/3/7共有pp・cap10。Production6b53/normal14216/HEAD49b003571固定、正式1964/53・歴史17/190・工数null/QA051final/451/HOLD不変更。先行index CanonicalField十五件と2957/58の元whole15を参照、成功確認の再演はしない。

NK-MSG-002、RD DAT009/MQ006～010、UI241242、SS324§3/6/15・SS352§11.2、PT-IDEM001002007008。Main全CanonicalField（byteコピー/NFC/decimal/消去）及びResponseSnapshotIdentity（型/owner境界/非秘密AAD組立）を全文確認した。後者はJDK UUID/ByteBuffer/ASCIIのみで、ResponseSnapshotCodec/FingerprintKeyRing/Graph9へ呼出しを持たない。new quality fixtureはnormal856Test/5786普通宣言とは別domain。保留suiteの部分抽出・差替えではなく独立に設計した値型unit試験で、元Production期待を変更しない。

| Test ID / method suffix | 入力・独立期待 |
| --- | --- |
| PT-IDEM-PUBLIC-001 metadata | name1/64・type1/32正常、null/空/上限超/未知字句拒否。metadata固定例外message |
| 002 buffers | nullと空の区別、元配列/返却配列を変えても内部コピー不変、close後は元長さのzero、再close安全 |
| 003 encodings | 合成e＋combining acuteと日本語のNFC UTF8 literal c3a9e697a5e69cac、Long.MIN/MAX/0/-1の明示ASCII。null text拒否 |
| 004 diagnostic | 合成PUBLIC_ONLY等のbyteを表示せずname/typeとredacted固定文字列 |
| 005 identityBounds | 四null境界、layout8/version3 ASCII、owner1/999999999999正常・0/-1/1000000000000拒否 |
| 006 factories | UUID00112233-4455-6677-8899-aabbccddeeff、匿名owner空/認証owner1、四getterと固定redacted診断 |
| 007 aadGolden | format1、version label v1、QSSRSP01/001、匿名102byte/owner min及びmax110byte。八U32BE-length fieldを独立Python struct/UUIDから作成した固定hexとの全byte比較・null keyVersion拒否・返却byte独立 |
| 008 parallel | 自所有4thread32taskだけで固定owner1の同110byteと比較、共有mutable bufferなし |

AAD期待は八field（purpose api-inbox-response/table schubert.request_inbox/UUID16/format1/非秘密keyVersion label/layout8/version3/owner0or8）を手書きの別言語structで連結。匿名SHA aa254ef50c8b472f45bf20df64280cb9c7e27616cb53b8e480d247965677c182、min f4c7c5aff1ec570202391be9185e76a242a59a300f3081c843a94abf8b61a16b、max 6e5da3f1e7791da91ada81bd2d71ea0304fe3a672754f41fcf5cc72b88a80dbc。production methodでexpectedを生成しない。暗号・HMAC・実鍵・認証許可・外部I/Oは実行0、AAD bytesの一致を暗号完全性やreplayの合格にしない。

新一JVMの全八XML/真正終了/FES0/同exec-session-CRCから二Source全物理classのline/method/class/branchを測る。既部分proofは同分母で新execへ置換し履歴保存、旧成功・execの合算0。独立post/negative/oracleとregistry/WBS局所整合を実施し、未達は除外せず残す。recordのJDK生成equals/hashCode/accessorは固定JaCoCo公式filterを変更せず区別、手書きmethod/全branchの追加除外0。getterを明示assertする。

commandはchecked entry経由pg16082_public_canonical_aad_eight_pt.py。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/現normal-null静的六module資格を参照し、生産コード変更なし。実source/branch/環境/時刻/終了code/XML/coverage/hashはmanifestと3087へ。未実行・中断・metadata負例をPASSや原Test数へ加算しない。
