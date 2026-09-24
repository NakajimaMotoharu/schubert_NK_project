# NK-OPS-001 service credential material単体テスト仕様書

Program `NK-OPS-001`、PG282/SSC-081。対象はAPI `ServiceCredentialReader.readPassword/readKey/consumePassword/consumeKey`、共用済み `InspectorDbCredential.consume`・`InspectorAesCredential.consume`。RD SYS-002/004、UI243/253、SS343 §6.1/6.2/6.6、既存018/078の保持inode reader契約を参照する。秘密実体・運用DB/MQ接続は対象外。

実行環境はLinux/JDK25.0.4/Maven wrapper、隔離された一時directory・実file/保持channelと既存の明示的な合成ACL/UID metadata。合成材料は `public-pt-only-<固定ID> LF` および`NKKEY1 LF v LF`＋32 zero byteのcanonical Base64＋LFのみで、実credentialを使用しない。expectedはSS343の固定byte形式とTest内の固定literal/zero配列から独立算出し、Production parserで生成しない。前提として018/078の10固定ID・file admission PTを通す。

| Test ID | 目的・入力/操作 | 独立期待値・境界/異常/例外/null/並行観点 |
| --- | --- | --- |
| PT-OPS-CREDREAD-009 | APIの`db-api`/`mq-api`に固定literal UTF-8＋LFを配布し`readPassword`、返却copyを利用・消去・close。別のtest-owned raw arrayを`consumePassword` | terminal LFを除いた固定文字列と一致。copy/close後の再取得拒否、toString非秘密、raw全byte zero。既存Inspectorのstrict UTF-8/1～65536境界PTを横断利用 |
| PT-OPS-CREDREAD-010 | Web/APIのKEY6 IDに固定canonical 32-byte zero key vectorを配布し`readKey`、別のrawを`consumeKey` | 固定version `v`、32 zero byte、raw全byte zero、copy/closeとredaction。HMACも同じ32-byte搬送形式、用途鍵の相互代替は許可しない |
| PT-OPS-CREDREAD-011 | password/key種別違い、API readerへWeb ID、null ID、null owned byteを投入 | kind/service違いはopen0の固定redacted失敗。nullは境界でNPE、I/Oせず成功値を作らない |
| PT-OPS-CREDREAD-012 | NUL入りpassword、LF終端をCRへ変えたkey、実file経由の形式不正 | 固定redacted失敗。test-owned raw byteとreader内部bufferは失敗後zero。異常内容を例外cause/logへ出さない |

全分岐は新API分岐と既存Inspector parserの既存PTを組合せ、全reactor JaCoCo instruction/branch/line/method/class missed0で検証する。並行観点は018/078-008の32独立readと既存Inspector材料の同期copy/close PTで担保し、当Testで実secret並行運用を主張しない。`NullPointerException`を正常値としてcatchしない。実行commandは `sh tools/quality/030_run_pgpt_verify.sh <当日新規run ID>`、保存検査は `python3 -B tools/quality/018_collect_verified_evidence_set.py <run ID>` と `--validate-only`、103 collector負canary。対象commit、日時、終了code、coverage、BUG、証跡path/hashは対応する081結果と同Program `evidence/manifest.json` に記録する。failed/flaky/skipped/not-runは合格に算入しない。
