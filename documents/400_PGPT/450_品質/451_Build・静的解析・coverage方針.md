# Build・静的解析・coverage方針

## 1. Gate順序

1. Maven Enforcer/toolchain/dependency convergenceとformatを検査する。
2. Java 25 compileを全warning error化し、null/static/security analysisを実行する。
3. Program単位PTを実行し、failed/flaky/skipped/disabled/not-runが0であることを確認する。
4. JaCoCoでproduction対象のline、method、class、branchが各100%であることを確認する。
5. DDL/設定/schema/shell、secret、trace、evidence manifest/hashを検査する。
6. 影響するNK Characterization caseを実行し、DIF-001～016以外の差分0を確認する。

## 2. Build contract

基準commandは次とし、root POMから全moduleをreactor buildする。

```sh
./mvnw --no-transfer-progress clean verify
```

Java release 25、UTF-8、`ja-JP`、`Asia/Tokyo`を固定する。Dependency/plugin version range、SNAPSHOT外部依存、暗黙最新版、repository追加を禁止する。Build生成物は`target`だけに置きGit管理しない。

## 3. 静的解析

| Gate | 合格条件 |
|---|---|
| Compiler lint | Production/testともwarning 0 |
| Null analysis | API境界・DB・設定・collection elementを解析、error 0 |
| SpotBugs/PMD/Checkstyle | High/Mediumを含む違反0。恣意的suppression 0 |
| Spotless | Format差分0 |
| SQL/DDL/schema | Flyway順序、parse、constraint/index/role/grant trace PASS |
| Shell | ShellCheck error/warning 0、秘密値表示0 |
| Secret scan | Credential/password/raw token/session/cookie/key/DB dump/master実体 hit 0 |

Protocol moduleは2026-09-02時点でCompiler `-Xlint:all -Werror`、JSpecify 1.0.0、SpotBugs 4.10.4.0 Max/Low、JaCoCo 0.8.15を`verify`へ導入済みである。JSpecifyはnull契約の表明であり、それ単独をnull dataflow解析PASSとはみなさない。後続moduleの実装開始前にNullAway相当をparent gateに追加する。

## 4. Coverage

- 対象は`src`配下production Javaの全class/method/branch/line。JaCoCo reportとcheck ruleをmodule/aggregate双方へ固定する。
- Line 100%、method 100%、class 100%、branch 100%を小数丸め前のcounterで判定する。
- Record/enum/compiler生成分岐も原則対象。自動生成codeを除外する場合はProgram PT仕様に生成元、対象、理由、要求coverageへの非影響、独立検査を記録し、review承認を得る。
- 無意味なassertion、production methodによるexpected生成、private reflection、到達不能偽装、除外glob拡大を禁止する。

## 5. NPE排除

Nullability/static analysis、constructor/factory invariant、API/DB/config/collection契約、null/欠落/空/未知値negative testを組み合わせる。NPE catchによる正常化はgate failureとする。

## 6. PT evidence

各Program directoryに仕様書、実行結果、必要な`evidence/*`、`manifest.json`を置く。Manifestには実行UTC/JST、OS/JDK/tool、branch/commit、command/exit code、Test ID、sanitized input/expected/actual、coverage counter、BUG/SSC、artifact path/SHA-256を記録する。秘密値は保存しない。

## 7. 完了gate

Build、全PT、4指標coverage、NPE/static、重大BUG 0、全BUG再試験、全YKT完了、未回答QA/RDF/UIC/SSC 0、未承認CHR差分0、secret hit 0、trace漏れ0、clean worktree、必要commit/branch/PR/push済みをすべて満たした場合だけPGPT完了とする。Remote認証やLinux実測など工程外依存は隠さずblockerとして報告し、未達のまま完了扱いしない。

## 8. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | Build・静的解析・coverage・NPE・evidence gate初版を確定。 |
| 2026-09-02 | Protocolのcompiler/JSpecify/SpotBugs/JaCoCo実績と、JSpecify単独でnull dataflow PASSとしない判定を追記。 |
