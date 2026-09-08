# Null解析gate検証仕様

## 1. 目的・追跡

PT-QUALITY-001は411 §4/11、451 §3/5、PG-D-003、SS354のNPE排除を機械的に検証する共通Build試験。NK-PRO-001～003、NK-MSG-001/002および後続production Programへ適用する。Production対象は`src`の全`dev.codex.schubert.nk` package（子package・生成recordを含む）。

## 2. 契約

- NullAway 0.14.1 / Error Prone 2.50.0 / JSpecify 1.0.0 / JDK25。parent POMのdefault-compileに設定し、ERROR時にBuildを失敗させる。
- `AnnotatedPackages=dev.codex.schubert.nk`、`JSpecifyMode=true`、`JSpecifyJDKModels=true`。JDKモデルはcollection要素・JDBC等のnullable戻り値を解析するため有効化する。除外package/class、NullUnmarked、NullAway抑止を追加しない。Error ProneはNullAwayの実行基盤として使用し、それ以外の解析は別のSpotBugs/PMD等gateで担う。
- production全体を解析する。意図的なNULL入力を持つJUnit negative testはdefault-testCompileで通常compileし、実際の境界拒否を実行検証する。これはproductionのcoverage除外ではない。
- `program/characterization`は別packageの互換試験基盤であり、このproduction null解析PASSの対象に含めない。既存CHRの全PTは引き続き実行する。
- 外部libraryの未注釈APIは解析だけで安全と断定せず、DB列のNOT NULL/欠落guard、constructor invariantとnegative testを併用する。

## 3. 独立した合否oracle

Canaryは`tools/quality/null-contracts`に置くcompile-only fixtureで、production source/module/jarへ含めない。

| Case | 操作 | 独立期待値 |
|---|---|---|
| QLT-NULL-01 | valid fixtureを親設定でcompile | exit0。明示null分岐とnon-null要素の参照を受理 |
| QLT-NULL-02 | invalid fixture nullableDereference | NullAwayがnullable値のdereferenceを拒否 |
| QLT-NULL-03 | invalid fixture nullableReturn | non-null戻り値へのnullを拒否 |
| QLT-NULL-04 | invalid fixture nullableElement | collectionのnullable要素dereferenceを拒否 |
| QLT-NULL-05 | invalid fixture nullableArgument | non-null parameterへのnullを拒否 |
| QLT-NULL-06 | 全productionをclean compile、全PT/coverage/staticをverify | production NullAway error0、既存品質条件を維持 |

Command（共通JAVA_HOME/Maven cache設定は421を参照）:

```sh
./mvnw -f tools/quality/null-contracts/pom.xml clean compile
./mvnw -f tools/quality/null-contracts/pom.xml -Dcanary.source=fixtures/invalid clean compile
./mvnw clean verify
```

負のcanaryはcompile失敗が期待結果であり、productionの失敗を合格へ算入するものではない。診断にNullAwayと対象行の対応が全件存在することを確認する。証跡にはcommit、command、exit code、tool hash、sanitized diagnostic、全productionの対象件数・結果を記録する。

### PT-QUALITY-002 JDBC必須列

`RequiredColumn.requireValue`はSQL NULLをSQLDataException/SQLSTATE22004へ変換し、値やcolumn値をmessage/causeへ漏らさない。String/Instant/byte配列のnon-null値は同一参照、NULLは固定messageとcauseなしという独立期待値を`RequiredColumnTest`で確認する。Inbox/Outboxの必須reference型列へ適用し、optional列はOptional/wasNullで区別する。SS331のNOT NULL/CHECKと実PostgreSQL非回帰試験を併用する。

## 4. 状態

Null gate導入・検証PASS。commit `18b426f`、Run PT-IDEM-20260907-04全263件成功・coverage100%/SpotBugs0。QLT-NULL-01..05は2026-09-07 22:38:04～22:38:15 JSTに独立実行しpositive exit0、negative exit1・4診断すべて一致。証跡は`evidence/01_PT/006_NK-MSG-002/evidence/quality/null-canary-results.json`、PT-QUALITY-002は同ProgramのRequiredColumnTest XMLとmanifest。BUG-016/YKT-013完了。後続のformat/PMD等およびPGPT全体の完了を意味しない。
