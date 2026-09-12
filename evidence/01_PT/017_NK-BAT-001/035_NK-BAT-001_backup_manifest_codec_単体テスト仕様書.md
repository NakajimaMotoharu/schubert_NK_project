# NK-BAT-001 backup_manifest_codec単体テスト仕様書

## 実装前に固定した独立golden

BAT187最大正規byte長は独立field幅の総和1873（7token×128、2id×12、2attempt×2、3size×19、固定timestamp/UUID/hash/構造）。全3sizeを3074457345618258602/3074457345618258602/3074457345618258603へ置き、合計Long.MAX_VALUEを独立計算する。受信上限4096と正規最大1873を混同しない。実装/探索結果は036、BUG182/183・YKT143/144の全対象確認は037。正式認定待ち。

965 ASCII bytes（下記JSONの末尾にLF1つ）。SHA256=733939f4daa4dcb642e6b9a4433c92daf3d42e8ac73a15b0aee914b58571289e。SSのfield順と公開literalを手書きし、Production未実装時点で固定。directoryName=20260913-000002-12345678-9abc-def0-8123-456789abcdef、configurationBytes=712、totalBytes=713。申告hashであり実artifact検証済みとはしない。

```json
{"format":"NKBACKUP1","database":"schubert_nk","runId":"12345678-9abc-def0-8123-456789abcdef","cutoff":"2026-09-12T15:00:00.000000Z","startedAt":"2026-09-12T15:00:02.123456Z","contentFinishedAt":"2026-09-12T15:00:03.654321Z","databaseStep":{"id":90000,"attempt":1,"startedAt":"2026-09-12T15:00:00.000000Z"},"configurationStep":{"id":90001,"attempt":1,"startedAt":"2026-09-12T15:00:01.000000Z"},"versions":{"host":"nk-pt","app":"0.1.0-SNAPSHOT","schema":"020","os":"Ubuntu-26.04.1","jdk":"25.0.4","postgresql":"18.6","artemis":"2.56.0","age":"1.2.1"},"recipientSha256":"0000000000000000000000000000000000000000000000000000000000000000","files":{"schubert_nk.dump":{"size":1,"sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"config.tar":{"size":512,"sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},"credentials.tar.age":{"size":200,"sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"}}}
```

PG165/SSC058先行8a606fc7、BAK001～008/BKO001～008/UI251 §5/SS311・341 §6.4・343 §5.3。PG164正式08のsource凍結中に仕様のみ先行、未実装/未実行/認定0。

| Test ID | class/method | 目的・事前条件/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-186 | BackupManifestCodecTest.independentCanonicalGolden | SS固定field順の手書JSON/golden bytesと両方向照合、Production生成expected禁止 |
| PT-BAT-187 | BackupManifestCodecTest.allFieldsAndMaximumLengths | 全fieldを個別に違う値へした独立vector、正longとversion128上限 |
| PT-BAT-188 | BackupManifestCodecTest.structuralByteMutation | 固定key/区切り/LF各位置の改変・CR/NUL/BOM/非ASCIIで誤受理しない |
| PT-BAT-189 | BackupManifestCodecTest.noncanonicalScalarsAndDates | 数値alias/UUID/hash大文字・時刻省略µs/offset/日付自動補正・閏秒を拒否 |
| PT-BAT-190 | BackupManifestCodecTest.missingUnknownDuplicateAndOrder | unknown/duplicate/欠落/null/key順・空白・escape・末尾余剰を拒否 |
| PT-BAT-191 | BackupManifestCodecTest.sizeAndNullBoundaries | 最大4096前後/empty/null・過大数値と固定診断/cause/suppressed |
| PT-BAT-192 | BackupManifestCodecTest.inputOutputOwnership | 入力byte改変後もmodel不変、encodeごと独立array、返却改変が次回へ影響しない |
| PT-BAT-193 | BackupManifestCodecTest.concurrentCanonicalRoundTrips | 64並行の独立手書golden値とencode/decodeの一致、同modelでもarray共有なし |

Fixtureは公開合成run/id/version/count/hashだけ。サイズ/hashは申告値のvalidation fixtureでありactual dump成功の証明ではない。golden JSONはSS順・literal fieldから独立作成しProductionでexpectedを生成しない。PK/実DB state/実artifactのI/O・hash/暗号・復元・7世代は別未完了。全正常/境界/異常/例外/NULL/未知/所有/64並行を上記Test IDへ一意に対応付ける。

Production全class/method（record accessorを含む）: BackupManifestCodec constructor/encode/decode/全private render・parse helper。line/method/class/branch100%・NullAway/negative・SpotBugs/Spotless成功が必要、除外や無意味assertionで代替しない。障害は修正前915、共通原因916、設計はSSC058を先行する。

実行環境は421 Java25/Maven、コマンドは該当batch -am test/正式clean verify。036_NK-BAT-001_backup_manifest_codec_実行結果.mdとmanifestへ日時・OS/tool/branch/対象commit/実行command/exit/input/期待と実際/4coverage/static/BUG・SSC/証跡path・hashを記録する。未実行/skipped/flaky/error/failedは合格にしない。
