# NK-OPS-001 静的Inspector環境file単体テスト仕様書

PG-D-151/SSC-049（先行85eef317）、OPS-009、UI251、SS311/343 §6.6/6.8。Program/class: batch.platform.InspectorStaticEnvironment.requireValid。設定管理者がrenderする2行の非秘密fixture、実DB接続なし。file所有/IO/publishは別PT。本試験の成功だけではProgram完了にしない。

| Test ID | method | 入力・操作・独立期待値/根拠 |
|---|---|---|
| PT-OPS-CFG-001 | canonicalFixtures | SSのliteral 2行、port1/65535、DB1/63文字、version1/16文字・複数・大小文字区別。全byte不変・成功。Production生成expectedなし |
| PT-OPS-CFG-002 | sourceAndSyntaxRejection | 0/1/3行、逆順、重複/未知/alias/run/credential key、quotes/escape/comments/CRLF/NUL/高bit/全controlを独立列挙。全て固定IllegalArgumentException、cause/suppressedなし |
| PT-OPS-CFG-003 | urlBoundaries | remote/IPv6/hostname/userinfo/query/fragment、不正port0/65536/先頭0/6桁、DB空/64/大文字/不正字。§6.6の独立literalで拒否し、既存子のURL値契約へ反する受理なし |
| PT-OPS-CFG-004 | versionBoundaries | 65535/65536byteの一意version列成功、65537拒否、各16/17文字、先頭記号、空/重複/末尾comma/大小文字の境界。上限値は独立算術から生成 |
| PT-OPS-CFG-005 | sizeNullAndRedaction | null NPE、empty/65848/65849byte不正fixtureを容量/形式で拒否。malicious値を診断へ反射せず入力不変。切断した全prefix拒否 |
| PT-OPS-CFG-006 | concurrentValidation | 64並行に独立正常/不正fixtureを検証。共有mutable state/IOなし、入力不変・各期待どおり、有限wait |

実行: Java25/Maven3.9.12、固定local toolchain・隔離tmp。探索は`./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch -am verify`、正式は新run IDで全reactor `clean verify`。line/method/class/branch各100%・NullAway/SpotBugs/Spotless必須、失敗/skipを合格に算入しない。実行日時/対象commit/OS/tool/command/exit/fixture根拠/実際結果/coverage/BUG/hashは012とevidence/manifest.jsonへ固定する。未実装TDD初回failureはBUGではない。
