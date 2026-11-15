# Build・静的解析・coverage方針

2026-10-28静的完了条件の具体化（BUG2038/YKT1786、品質緩和なし）：SpotBugsは既4.10.4/Max/Low・全対象を維持し、command0/BugInstance0だけでなくMissingClass/解析Error0・同sourceの全物理MainとClassStats集合一致を必須とする。解析auxはfresh siblingと固定外部依存へ束縛し、古いlocal m2 snapshot混入を拒否する。原不完全結果を修正せず、当sourceの新解析と独立postに分離する。2430/13216/13220は全1843/六artifactの当静的証拠であってPT/coverage/native/全F03/正式451受入ではない。以後のactive staticも同条件を満たし、旧Maven経路のexit0だけを受入根拠にしない。

SSC234（2026-10-09）：固定INSPECTOR/BOOTSTRAPの同期CLOSINGはSS342343354を正とし、terminal→closing同source/単一session/actor/時刻順/probe単調性/完了markerを独立照合してlatest closing一つを選ぶ。古いterminalへのfallback/同session union/採取点連鎖/除外0。追加点自身のtail・同main terminationは独立port試験、実native権限/終端の代用にしない。Root BEFORE_EXEC/API-Web terminal/全四100/正式同source全scope条件は不変更。

SSC193採取補足（2026-10-06）：隔離PG/PTの固定pin/output=none/公開getExecutionData(false)・held新0600 inode・Root exec直前と普通owned帰還後終端はSS342343を正とする。host選択は独立literal/metadata/byte/FD/null/並行/例外の限定証拠、実main/session/真正manager及びstop後条件の代用ではない。正式runへ加えるexecは同source/frozen byte/boot/Invocation/PID/start/time/pointを独立に照合し、before-execだけから普通成功を推定しない。全counter100%、既定argv/env/2FD/security/owner/budget・独立oracle・非秘密/trace・全scope/run条件は不変更、除外追加/累積exec/別source流用0。

2026-09-30運用参照: 次回の受入経路・coverage閉鎖・検証の区切りは[477 §4～5](../470_PMO/477_GPT61Sol実行計画・再開判定.md)を参照する。本書の品質条件は変更しない。小部品追加だけで全正式認定を繰り返さず、下記の機能受入・変更後停止・PR/工程gate・横断変更では所定の全体検証を実施する。各正式runの前に実際のtriggerと対象受入IDを1行で残す。管理文書だけの今回改定は新規試験認定ではない。

PG201追補（2026-09-20）: Production JavaScriptはNode24.19.0の構文checkと実script/独立DOM event fixtureをJUnitから必須実行する。V8 line/function/branchを各100%へ強制し、対象Production fileがcoverage表に実在することを確認する。検索scriptはclass定義なし（class0/0、除外なし）、定義した全functionをmethod相当として100%・source file inventory1/1を検査する。JavaのJaCoCo4指標100%は従来どおり維持。8Node subcaseは1JUnit内数。Node不存在/異version、構文失敗、対象なし、failed/skipped/todoを合格にしない。実Browser描画・IT/STは別gate。

検索scriptの静的確認はNode構文check＋限定source全体review（document.querySelector/制御されたform event/setCustomValidity/requestSubmit、TextEncoder/Decoder/NFC/固定ASCII trimだけ）。inline handler/eval/innerHTML/network/storage/console/秘密値読取りなし。JavaのNullAway/SpotBugsをJSにも実施したとは記載しない。再現Node path/version/hashは421、実command/coverage/hashは016005/006・manifest。

## 1. Gate順序

以下は正式認定/受入の順序であり、小部品の編集ごとに全gateを再認定する要求ではない。開発中は変更moduleと依存/影響suiteを選び、選択根拠・実行/未実行範囲を記録する。機能がつながる完成単位、変更後の停止・PR・工程gateでは全体検証を実施する。POM/共通codec/DDL/security等の横断変更は全回帰を先行する。予算上限等で実施できない場合は未認定として保存し、限定試験を正式合格へ読み替えない。運用目的は456に従う重複調査/証跡更新のトークン削減であり、機械実行時間だけを理由に必要試験を削らない。

1. Maven Enforcer/toolchain/dependency convergenceとformatを検査する。
2. Java 25 compileを全warning error化し、null/static/security analysisを実行する。
3. Program単位PTを実行し、failed/flaky/skipped/disabled/not-runが0であることを確認する。
4. JaCoCoでproduction対象のline、method、class、branchが各100%であることを確認する。
5. DDL/設定/schema/shell、secret、trace、evidence manifest/hashを検査する。
   収集は018_collect_verified_evidence_set.pyで各collector失敗時に停止し、固定必須scopeの同一run/source/branch・全file hash・参照を横断照合する。017/019の負canaryを先行実行する。個別hash成功だけを全証跡収集完了としない（BUG-099/100、YKT-089、458）。
6. 影響するNK Characterization caseを実行し、DIF-001～016以外の差分0を確認する。

## 2. Build contract

正式認定の基準commandは次とし、root POMから全moduleをreactor buildする。開発中の限定実行はこの基準の代替ではない。source/試験/設定/toolが未変更の再開や管理文書のみの変更では、既存認定との一致確認を行い、新しい実行結果として再認定しない。

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

Compiler `-Xlint:all -Werror`、JSpecify1.0.0、SpotBugs4.10.4.0 Max/Low、JaCoCo0.8.15に加え、2026-09-07に親default-compileへNullAway0.14.1/Error Prone2.50.0を導入した。全NK production packageをJSpecifyMode/JSpecifyJDKModelsで解析し、生成recordの除外なし。JSpecifyの注釈だけを解析PASSとみなさない。453のpositive/4 negative canaryと全263 PTのRun PT-IDEM-20260907-04でBUG-016/YKT-013を完了。新moduleにも親gateを継承する。Enforcer/format/PMD等は引き続き検証し、全品質gate完了とはまだ宣言しない。

## 4. Coverage

- 対象は`src`配下production Javaの全class/method/branch/line。JaCoCo reportとcheck ruleをmodule/aggregate双方へ固定する。
- Line 100%、method 100%、class 100%、branch 100%を小数丸め前のcounterで判定する。
- Record/enum/compiler生成分岐も原則対象。自動生成codeを除外する場合はProgram PT仕様に生成元、対象、理由、要求coverageへの非影響、独立検査を記録し、review承認を得る。
- 無意味なassertion、production methodによるexpected生成、private reflection、到達不能偽装、除外glob拡大を禁止する。
- SS 323から再現生成する69 named recordもproduction coverage対象とし、除外0で4指標100%を満たす。型名対応は生成scriptから独立した64行fixtureで検査する。

## 5. NPE排除

Nullability/static analysis、constructor/factory invariant、API/DB/config/collection契約、null/欠落/空/未知値negative testを組み合わせる。NPE catchによる正常化はgate failureとする。

## 6. PT evidence

各Program directoryに仕様書、実行結果、必要な`evidence/*`、`manifest.json`を置く。Manifestには実行UTC/JST、OS/JDK/tool、branch/commit、command/exit code、Test ID、sanitized input/expected/actual、coverage counter、BUG/SSC、artifact path/SHA-256を記録する。秘密値は保存しない。

開発中の限定実行は対象/未実行範囲/command/source/結果を暫定記録へ残し、正式manifestへ混入しない。小編集ごとの全証跡再生成や最新概況の多文書転記は不要。正式収集では従来どおり全必須scopeを同一run/source/branchで横断検証し、古い別sourceの成功結果を流用しない。過去runの証跡は履歴として保全し、最新状態は456・各Programの正式manifestへの参照で追跡する。collectorの厳密性・coverage条件は変更しない。

2026-09-23以降の新run IDは`tools/quality/030_run_pgpt_verify.sh`（既存`work/pgpt_foundation_verify.sh`は入口）で当日・未使用だけを発行する。018の`--validate-only`は`/tmp/<run>.commit`消失後も保存root manifestのrun/source/branch/exitと全必須scope/hashを照合する。これは`PASS_PERSISTED_EVIDENCE_ONLY`であり旧runを再実行・再認定した表示ではない。新しい正式runの収集は従来どおり実行時commit・同一source/tools・負canaryを要する。

## 7. 完了gate

Build、全PT、4指標coverage、NPE/static、重大BUG 0、全BUG再試験、全YKT完了、未回答QA/RDF/UIC/SSC 0、未承認CHR差分0、secret hit 0、trace漏れ0、clean worktree、必要commit/branch/PR/push済みをすべて満たした場合だけPGPT完了とする。Remote認証やLinux実測など工程外依存は隠さずblockerとして報告し、未達のまま完了扱いしない。

## 8. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | Build・静的解析・coverage・NPE・evidence gate初版を確定。 |
| 2026-09-02 | Protocolのcompiler/JSpecify/SpotBugs/JaCoCo実績と、JSpecify単独でnull dataflow PASSとしない判定を追記。 |
| 2026-09-20 | 開発中の限定実行と正式全体認定を区別。週次枠優先で重複更新を減らすが、全gate/全scope同一source検証と未実行の非合格扱いを維持。 |
| 2026-09-23 | PMO W00で新規日付run IDと永続保存manifestからのvalidate-only入口を整合。旧runの照合と新規正式認定を区別。 |


2026-11-15 SSC417 source段: 2026-11-15、dev-foundation、source前HEAD7b2f17f40bfff283913a30a6fe4ab8329d9d8031。実行環境/時刻/command/exit/hashはPG33710/source-only-checks-v2.json、独立source判断はsource-only-review-v2.json。整形GJF1.36.1とCheckstyle14.3のJava source parseは終了0・指摘0。旧途中結果も保存し、新24Testを一度も起動していない。

SDK ABI/compile、NullAway、SpotBugs、semantic PMD、全体build、動的PT24、実Driver/DB/nativeはNOT_RUN_HOLD。line/method/class/branch/instruction coverageはすべてnull、PASS数0。旧Coreef461eba/Unita48eec60の全1050は新POM変更前の歴史資格として保持し、新port・新POMへ流用しない。旧105Java source byte不変はレビュー済みだが、新依存グラフ全体の受入を意味しない。

BUG3001/YKT2530は表示escape誤読による誤検知取り下げ、source修正実績0。BUG3002/YKT2531はfuture fixture初期化順をsource是正し型compile/PT待ち。BUG3003/YKT2532はowned capture後の幅検査へsource是正、未来PGCOPY005を追加し、既4Mainの非該当根拠をsource-only水平確認、動的未完OPEN。BUG3004/YKT2533の誤った旧vector異常前提は原・現同値正例と独立合成負例で是正、metadata source review限定で閉鎖し製品PT成功に数えない。

価格1/3/8pp cap9はこのsource製造・PT source・強化レビュー段のみ。未実行SDK/PTの残工数を0としない。後続費用は元P019/全451費用に含む未確定内訳として保留、追加二重課金0、今回段完了を工程完了/工数完成率に換算しない。正式1964PT/53scope、正本184/625、元190新0、工数率nullを維持。
