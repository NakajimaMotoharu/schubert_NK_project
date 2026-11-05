# Characterization Test実行準備・PG開始gate

## 1. 目的・位置づけ

現行schubertの実動を利用者向け互換性のbaselineとして機械取得・比較できるよう、test harness、fixture、
normalizer、oracle、証跡、差異管理、PG開始gateの実装仕様を定める。設計確定後、利用者指示により本仕様のtest artifactをNK production codeと分離して作成・実行し、最初のNK production code着手前gateを完了した。

- 状態: `確定・実行済み`。Executable artifact/current baselineを作成し、CHR-G01～G06は全件PASS
- 上位設計: UI 221～226、254、261、263～265
- 関連RD: SCP-001、SCP-004、MIG-002、MIG-006、TST-001～TST-005、TST-103
- 関連SS: [313_画面template・controller・form設計](../310_アプリケーション/313_画面template・controller・form設計.md)、
  [333_大容量結果file・media・Range配信設計](../330_データ・ファイル/333_大容量結果file・media・Range配信設計.md)、
  [354_PT・IT試験観点詳細設計](354_PT・IT試験観点詳細設計.md)
- 関連QA/RDF/UIC: QA-015、044、RDFなし、UIC-004

## 2. 固定baseline識別

PG開始gateはUI 264の次の識別値を入力にする。実行開始時に同じ算出規則で再計算する。

| 対象 | Baseline |
|---|---|
| Current source/schema | Source 56＋DB関連3件、集約SHA-256 `c9ce7c85de2d0443b4d7bb4d9a3082b39985c1cbf3121945de1ee4a936b0bd6c` |
| Current documents | Markdown 18件、集約SHA-256 `1904756ba0e0cbf73f3942ad8481d17d727e3e8f3770dacf8bc64ee06c2acaff` |
| Master | 59,627 file、19,240,707,190 byte |
| Scenario | 262 file、99,661 entry、audio metadata 37,256、link 35,201 |
| Media | Video 20、Music 129 |

集約hashはrootからのPOSIX相対pathのUTF-8 byte昇順で
`<file SHA-256><two spaces><relative path>\n`を作り、そのUTF-8 byte列をSHA-256化する。Symlinkは追跡せず、
存在する場合はlinkとtargetをmanifestへ記録して失敗とする。

不一致時は実動取得を続行せず、差分file、変更理由、利用者影響をreviewする。互換性に影響する場合はUI 264と差異管理の
見直しを先行し、新hashだけを自動受入しない。

## 3. Artifact構成

NK repositoryへ次を実装済みである。production moduleとは分離したtest artifactとする。

```text
program/characterization/
  pom.xml                         # Java 25、JUnit 5、Playwright Java、version固定
  src/main/java/...               # preflight/source検証/比較/report/baseline昇格CLI
  tests/java/...                  # case/runner/adapter/normalizer/assertion
  tests/resources/
    cases/                        # CHR case定義、DIF allowlist、schema
    browser/                      # viewport/font/locale定義
    fixtures/expected.json        # ID非依存の順序・件数・manifest
  fixtures/
    manifest.yaml                 # 機密を含まないlogical fixture
  baseline/current/
    manifest.json                 # source/hash/environment/case/artifact version
    artifacts/                    # 24 caseの正規化JSON/HTTP/DOM/data assertion
    screenshots/                  # 固定条件PNG
  reports/
    current/<run-id>/             # 実行report、diff、redacted log index
    gate-report.json              # CHR-G01～G06集約判定
  run-gate.sh                     # 上書き禁止のcommand entrypoint
```

Repository rootのMaven WrapperとJava toolchainを使い、dependency/plugin/browser binary/fontをversion/hash manifestで固定する。
PlaywrightはBrowser自動操作・DOM・screenshot・HTTP context、JUnit 5はcase・assertion・reportを管理する。画面期待値を
CSS selectorの存在だけで判定せず、表示文字、順序、操作後URL・処理結果まで取得する。

## 4. Runner・外部設定

| 設定 | 必須 | 規則 |
|---|:---:|---|
| `target` | yes | `current`/`nk` allowlist |
| `baseUrl` | yes | HTTPS URL、test host allowlist外を拒否 |
| USER/ADMIN credential reference | yes | 0600 credential file/reference。値はGit/reportへ保存しない |
| Browser | yes | Pinned Chromium。headless/headedのpreflight差を検査 |
| Locale/timezone | yes | `ja-JP`、`Asia/Tokyo`。Report timestampはUTCも保持 |
| Fixture/profile | yes | Read-only master、test専用account/log/questionの初期化手順 |
| Evidence root | yes | Repository内reportsの対象run-id。既存baseline上書き禁止 |

Command contractは`verify-source`、`preflight`、`capture-current`、`compare-current`、
`report`、`promote-current`を独立taskにする。NK比較taskはNK実装時に同じrunnerへ追加する。`capture-current`は新しいstaging runだけへ出力し、
reviewなしで`baseline/current`を上書きしない。

## 5. Case catalog・適用性

UI 264の24 caseを名称・粒度とも変更せず実装する。

| Group | Case | Current | NK | 主証跡 |
|---|---|:---:|:---:|---|
| Authentication | CHR-A01～A03 | ○ | ○ | DOM/header/HTTP/audit |
| Common UI | CHR-U01～U02 | ○ | ○ | Semantic DOM/PNG |
| Scenario | CHR-S01～S08 | ○ | ○ | 正規化result/DOM/HTTP |
| Media | CHR-M01～M07 | ○ | ○ | DOM/manifest/header/range hash |
| Log | CHR-L01 | ○ | ○ | Result/DOM/DB/log projection |
| Error | CHR-E01 | ○ | ○ | HTTP/DOM/redaction |
| New feature | CHR-N01 | `NK_ONLY`固定 | ○ | User/質問/通知/回答受入 |
| Operation | CHR-O01 | ○ | ○ | Restart/cache/dependency HTTP/log |

`current全case成功`はCurrent適用case 23件のPASSと、CHR-N01のcase metadataが`NK_ONLY`であることのschema検査PASSを
意味する。CHR-N01をSKIPPEDまたはCurrent不具合と扱わず、NK比較では必須PASSとする。他caseへ`NK_ONLY`を追加できない。

## 6. Browser・HTTP固定条件

| 項目 | 固定値・比較規則 |
|---|---|
| Desktop viewport | 1366×768、device scale 1、default zoom 100% |
| Mobile viewport | 390×844、device scale 1（responsive対象case） |
| Browser/font | Pinned Chromium build、manifest記載font、font load完了後撮影 |
| Locale/time | `ja-JP`、`Asia/Tokyo`、animation/transition/caret停止、利用可能な画面は固定test clock |
| Navigation | Network idleではなく期待DOM state/responseの明示wait。自動retryでも最初の失敗をreportへ残す |
| Screenshot | PNG、full page＋主要region。Anti-alias差の最小thresholdとdiff imageを保存し、文字・配置差は許容しない |
| HTTP | Method/status/redirect/Content-Type/Disposition/Length/Range/cache/security header/body length/hash |

TLS警告のtest回避はcurrent/NKの内部証明書に限定し、hostname・暗号化・公開portの確認を省略しない。

## 7. 正規化規則

### 7.1 正規化する可変値

- CSRF hidden/cookie/session IDの値は用途と属性を残し`<TOKEN>`、`<SESSION>`へ置換する。
- Request/message/correlation/event ID、自動採番DB ID、作成・更新時刻は同case内参照関係を保つplaceholderへ置換する。
- HTTP `Date`、test runner/run ID、非表示nonceを除外する。`Server`の存在は除外せず、非表示性を比較する。
- DOM属性順、browserが等価に扱うclass順、見た目に影響しないtag間whitespaceだけを正規化する。

### 7.2 正規化しない項目

表示文字・error文言、title/label/順序/件数/page/link先、role別要素、form name/method/action/autocomplete/autofocus、
status/redirect、Content-Type/Disposition/Length/Range、security/cache headerの存在・値、media byte hash、
取消・削除・通知stateは正規化しない。Current/NKの相違は必ずDIF-001～016へ帰属させる。

## 8. 比較oracle・DIF適用

1. Currentで正規化artifactを取得し、同一currentへ再実行して0 diffを確認する。
2. NKは原則baseline完全一致。UI 264のDIF-001～016に記載したcase・項目・NK期待値だけを許容する。
   QA-045/UIC-005/SSC-074によりDIF-001のbrand/title対象へCHR-A01を追加する。Current baselineのLogin titleは変更せず、NKの`schubert NK - ログイン`だけを比較時に登録した差分として扱う。
3. DIFは包括wildcardでDOM/page全体を除外せず、JSON Pointer、semantic element key、header名、before/afterまで指定する。
4. 未登録diff、未使用DIF、対象case外のDIF、過度なnormalizationはgate失敗とする。

Current sourceと実動が異なる場合は実動証跡をbaselineにする。NKで修正する利用者差異は新規DIFと必要なQA/RDF/UIC承認前に
許容しない。

### 8.1 CHR-L01の相関付き比較（QA-051/SSC-184、2026-11-02承認）

§8のbaseline一致規則には、UI264 §5.1/DIF-010に明記したログaction名称と比較投影の差分だけを追加適用する。Current baselineを再取得・上書きして差分を消さず、他caseへこの例外を広げない。

1. 実行前にCurrent/NKのsource・設計・artifact・fixture・oracle版と、今回操作ごとの独立期待表を固定する。SS351 §4/§4.1からcategory/action/記録先/必要件数を導き、実装や実測から期待値を生成しない。
2. 既存ログの保全用beforeと専用fixtureを区別する。同じ操作とDOM条件を用い、request/event/message相関とbefore/afterの整合snapshotを保存する。時刻・最大IDの水位だけを相関証明に使わない。
3. Current/NKのPK等を直接一致させる代わりに、承認されたaction対応と論理操作の相関を明示した安全投影を比較する。投影のfield/key、before/after、期待差分をartifactへ記録し、相関不能・不足・未登録追加を無視しない。
4. REQUESTはlocal→outbox→DBを同じeventの識別根拠で追跡し、論理DB投影の欠落0・重複0、必要HTTP項目保持、再送時の冪等性を独立に検証する。業務/security監査の正本は既存設計のAPI transaction内DB記録のままとし、REQUEST投影で代替しない。
5. 既承認設計の追加技術行も独立期待表で検証する。`menu`/`log_search`相当、画面の日時順・100件/page・表示件数・明細・検索及び業務結果の未登録差分をnormalizationで消さない。既存ログ保全の前後条件も検証する。
6. 相関・観測の不足又は未承認の件数/順序/表示差は未判定又は不合格として記録し、別途仕様判断が必要なら影響を特定する。本承認を包括的な差分免除としない。

比較artifact/oracleの改修、独立正常/欠落/重複/相関誤り/対象外差分の検証、最終同sourceの実NK CHR-L01は未完である。過去のactual0、設計承認、原観測を新方式のPASSに変換しない。今回のQA回答待ちは解消するが、資源所有・権限・安全・他の品質HOLD、利用枠停止と明示再開条件は維持する。

### 8.1.1 QA-054の追加独立期待値（SSC-336）

UI264 §5.1/SS351のQA-054期待表を凍結し、Current menu→NK MENU_VIEWED/ACTION、Current log_search→NK LOG_SEARCHED/ACTIONを同操作相関付きで比較する。正常メニューGETでは別eventのREQUEST 1＋MENU_VIEWED 1と各local/outbox/DBの欠落重複0、ADMIN初回成功ログ検索ではREQUEST 1＋API LOG_SEARCHED 1を確認する。保存結果再送では成功ACTION追加0、拒否/失敗/HEAD等では当該成功ACTION 0を確認し、必要MQ記録は別検証する。

検索snapshot取得時点と後発LOG_SEARCHEDのcommit後DB後条件を区別する。snapshotに自身の監査が含まれないことだけで欠落とせず、後条件で保存1件を検証する。日時順/100件page/表示件数/明細の差分や未登録追加を包括免除しない。独立wire goldenは全offset/length/type・2336 byte・64 layout不変、REQUEST互換、MENU_VIEWED限定、未知/交差/Action欠落拒否を確認する。本設計承認・静的照合を動的PT/実NK L01/coverage/native/451 PASSへ加算しない。

## 9. Case別実装契約

| Case | Driver・入力 | Oracle・証跡 |
|---|---|---|
| A01～A03 | Browser/HTTP、専用account、制御clock、restart | DOM、cookie/header、redirect、lock/session/audit、password非再表示。A02のCurrent 3 session継続はDIF-016、NKは最古revoke |
| U01～U02 | Desktop/mobile、keyboard、JS on/off | Card/title/order/nav/focus/empty/error、semantic DOM/PNG |
| S01～S08 | Query単独/AND/boundary、game/route/file/entry/audio | Logical content/display path/order/page/count、ID非依存JSON/DOM/HTTP |
| M01～M07 | 全logical media ID、inline/download、Range境界 | 20/129/pair/order/path、status/header/body length/chunk SHA-256/416 |
| L01 | Filter/page、Broker/API停止・復旧 | 日時順/件数/detail、REQUEST local/outbox/DBの欠落・重複0 |
| E01 | 401/403/404/409/416/503の正規操作 | 文言/再操作、secret/path/exception非表示 |
| N01 | NKだけUSER/ADMINで新規flow・replay | Menu差、User/質問/空回答/通知/取消/削除、同payload 0200・異payload 0105 |
| O01 | Web/Caddy/DB、NKはMQ/APIも停止・restart | Session継続、no-store、取違い0、復旧後に同じ利用者結果 |

CHR-S03/S06/S07/M02/M05/M06はPKではなくlogical key・display orderをsnapshotする。CHR-M04/M07はRangeごとに
`status, Content-Range, Content-Length, Accept-Ranges, chunk SHA-256`を1 recordで保存する。

## 10. Preflight・取得手順

1. Git worktree/commit、current source/document/master集約hash、OS/JDK/current Spring Boot/PostgreSQL/Caddy/Chromium/fontを記録する。
2. Current source/masterをread-onlyにし、test用DB/account/logの変更領域と復旧方法を分離する。
3. Host allowlist、TLS、public/loopback port、証跡領域空き20GB以上、clock、credential permission、Browser/fontをpreflightする。
4. Currentをclean stateで起動しsmoke後、A→U→S→M→L→E→Oの順でcaptureする。各caseはfixture初期化/後条件を持つ。
5. 同じcommit/environmentで再実行し、0 diff、failed/flaky/skipped/not-run 0、機密canary 0を確認する。
6. Baseline staging diffをreviewし、manifest・artifact・report・source hashを同一commitに固定する。

Current環境の破壊、source/master変更、証跡容量不足、credential漏えい、case後条件不明の場合は即時中断しbaselineをcommitしない。

## 11. PG開始gate

| Gate ID | 条件 | 必須証跡 |
|---|---|---|
| CHR-G01 | Harness/case/schema/normalizer/DIF allowlistがbuild・static test合格 | Artifact version、dependency/browser/font manifest |
| CHR-G02 | Current適用caseが全PASS、N01は`NK_ONLY` schema PASS | JUnit/report、case coverage 24/24 |
| CHR-G03 | 同一Currentの2回目が0 diff、flaky/skipped/not-run 0 | Run 2件のcomparison report |
| CHR-G04 | Baseline、source/document/master hash、environment、reportが同一commit | `baseline/current/manifest.json`、Git commit |
| CHR-G05 | DIF-001～016だけが機械読取可能で、未登録・過度除外0 | DIF schema/unused/coverage report |
| CHR-G06 | Source/master原本非変更、機密値非収録、review承認 | Git diff、canary/secret scan、review record |

CHR-G01～G06を1つでも満たさないcommitへNK production source・DDL・production configを追加しない。Gate commitは
`Characterization baseline`と識別し、その次のcommit以降だけをNK production実装とする。

### 11.1 2026-09-01実行結果

| 項目 | 結果 |
|---|---|
| Source/document/master照合 | PASS。Source 59件、document 18件、master 59,627件/19,240,707,190 byte、symlink 0、集約hash一致 |
| Preflight | PASS。Credential 0600、loopback allowlist、証跡空き20GiB以上 |
| Run | `ss-gate-20260901-01`と`ss-gate-20260901-02`。各Current適用23/23 PASS、CHR-N01 metadata PASS、catalog 24/24 |
| Repeat comparison | 26 artifact（24 JSON＋2 PNG）を比較しmissing/extra/changedすべて0 |
| Difference/security | DIF-001～016の16/16整合、秘密情報・`JSESSIONID`の証跡hit 0 |
| Gate | CHR-G01～G06全件PASS、failure 0 |
| Baseline/gate commit | `843de94`。NK production実装と分離 |
| 実行環境 | OpenJDK 25.0.4、Maven 3.9.12、Playwright Java 1.55.0/Chromium build 1187、Caddy 2.6.2、PostgreSQL 18隔離DB |

正式証跡は[gate report](../../../program/characterization/reports/gate-report.json)、[2回比較](../../../program/characterization/reports/current-repeat-comparison.json)、[baseline manifest](../../../program/characterization/baseline/current/manifest.json)を正とする。Playwrightはhost package名の警告を出力したが、pinned Chromiumの起動、DOM/HTTP/PNG取得、2回差分0まで実行済みである。

## 12. NK比較・差異受入

- 同じharness/browser/font/fixture schemaを使い、testをNKに便宜的にforkしない。Target adapter差はbase URLと証跡取得だけ。
- DIF-001～016適用後、Current適用caseの未承認diff 0、CHR-N01 PASS、機密漏えい0をST gateとする。
- Production変更は影響caseを先に追加・細分化する。Baseline期待値をNK結果へ合わせて書き換えない。
- 新しい利用者差異はQA/RDF/UIC/後続変更管理、DIF追加、UI/SS/test横断更新、承認後だけ許容する。

## 13. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-054 | HarnessをJava 25/JUnit 5/Playwright Javaの独立Maven artifactとしcurrent/NKへ同じcaseを実行 | NKとtoolchainを統一しつつproductionから分離し、UI 264のBrowser/HTTP/DOM/PNGを一貫取得 | PG開始前にversion・browser binary固定 |
| SS-D-055 | CHR-N01は`NK_ONLY`とschema固定し、Current gateでは適用case成功とmetadataを検証 | UI 264がN01を「NK受入結果」と明示。任意skipにせず全catalogを維持 | Current 23実行＋N01 metadata、NKは24実行 |
| SS-D-056 | Baseline更新はstaging capture→2回目0 diff→review→hash/report同一commitだけ | 偶発値・無承認変更・機密混入とNKへの期待値追従を防止 | Gate script、manifest、review checklist |

## 14. 禁止事項

- CHR-G01～G06前のNK production code/DDL/config着手、または同一commitへの混載。
- Current source/masterの書換え、production credential・DB dump・media実体・raw cookie/token/bodyのGit/report収録。
- DOM/page全除外、表示文言/順序/header/media hashの正規化、screenshot diffの理由なし閾値拡大。
- Failed/flaky/skipped/not-runをretry/exception/`NK_ONLY`で隠蔽、未登録diffをbaseline更新で解消。

## 15. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Harness構成、baseline/normalization/DIF契約、実行手順、PG開始gateを詳細化。 |
| 2026-09-01 | QA-044/UIC-004に基づき`DIF-016`を追加。Executable artifactを作成しCurrentを2回実行、差分0・秘密情報hit 0・CHR-G01～G06全PASSを確認しbaselineへ昇格。Binary証跡も検査できるようsecret scanを強化し、回帰testを追加。 |
