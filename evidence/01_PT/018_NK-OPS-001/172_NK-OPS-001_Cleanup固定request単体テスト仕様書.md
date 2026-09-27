# 172 NK-OPS-001 Cleanup固定request単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。対象はProduction `src/schubert-nk-batch/.../platform/CleanupWorkerRequest`のconstructor、`encode`、`consume`、`toString`。RD OPS-009/BAK-001、UI251、SS341§2/3/7・342§4・343§6、SSC104、PT-OPS-CREQ001～007。PG324の親→子非秘密相関だけを対象とし、削除権限、親M/A、DB advisory、同run backup現物、Artemis起動の合格ではない。

前提/fixture：Java25.0.4/Maven3.9.12、JSpecify/NullAway・SpotBugs、独立固定ASCII golden `NKCLEAN1`＋小文字UUID2値＋UTC cutoff `2026-09-27T15:00:00Z`＋lowercase SHA256 `0123456789abcdef`×4。期待byteはSS104で確定したfield順/改行を試験内のliteralから作り、Production `encode`をexpected生成へ呼ばない。任意path/command/credential/secretを含めない。入力byteはcaller所有として成功/失敗とも全byte0になることを確認する。

| Test ID | 入力・操作 | 独立期待・算出根拠 |
|---|---|---|
| CREQ001 | fixed vectorをconstructor/encodeとconsumeへ渡す | literal ASCII全byte一致、4field固定値、元入力byte全0。record値の同値性と別digestの非同値を確認 |
| CREQ002 | 4field各null、nil/run=activation、cutoff上下端/範囲外/µs不一致、digest長/大文字/非hex | nullは契約違反NPE、その他は固定IllegalArgumentException。UTC µs上下端だけ受入。NPEをcatchして正常化しない |
| CREQ003 | null byte array、0/257byte、NUL/CR/DEL/high-bit | nullはNPE、他は拒否・所有byte全消去。上限256/ASCII/LFはSS104固定 |
| CREQ004 | header、field名/順、末尾LF欠落/余分、追加row、末尾非空 | canonical以外すべて固定拒否・入力消去。各fieldの独立literalを改変 |
| CREQ005 | UUID異常/nil/重複、時刻異常/非µs/別表示、digest大文字、UUID非canonical大文字 | parse可能でも再encodeとbyte不一致なら拒否。現在時刻でcutoffを補完しない |
| CREQ006 | record diagnostic | 固定redacted文字列でUUID/digest値がない |
| CREQ007 | 異なる2所有arrayをvirtual threadで同時consume、同一値再送 | 両結果は同じ相関値、各array独立消去。parserは再送を受理しても、親の実原本・step照合なしに実行許可にならない |

異常/例外/境界/null/並行/再送は上記7件で扱う。固定byte列・明示例外/0化・record fieldをoracleとし、Production decode/encodeをexpected生成に用いない。Module dependencyとしてStorage/Bootstrapの限定8件ずつ、Batch既存停止11件を同時検査する。実行commandは173/manifest、実行環境・branch/source hash・終了code・sanitized JUnit/JaCoCo/SpotBugs・coverage・関連SSCは`evidence/provisional/PG324-cleanup-request`に一意追跡する。no-clean累積coverageを正式全scope/PGPT完了へ加算しない。実子Unit・root publisher/reader・DB/backup/transfer/native受入は未実行。
