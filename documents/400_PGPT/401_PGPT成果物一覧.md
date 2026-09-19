# PGPT成果物一覧・進捗

2026-09-20 最新確定: dev-foundation/source 5f813145c442e2b80df28d0ede5d1a9e4b9b55ad、正式PT-WEB-20260920-01（00:50:23～01:06:30 JST、Maven16:05/exit0）、全1455件（Protocol80/Storage74/API660/Web241/Batch359/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3method限定静的レビュー・coverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと46負canary成功。DB29部品266＋Batch24部品273＋OPS15部品126＝68部分成果665 PT（全1455の内数）。今回9月19日再開比+40 PT/+3部分成果、PG178～180のLog225/読取136/Cleanup136＝497複合と4NULL資源反例は既存Test ID内で追加認定し部品/件数増算0。BUG205/YKT161完了、BUG195/206・YKT154/162・SSC063は残Repository分類/修正のため継続。PG181は仕様のみで未実装。実archive/7世代/親実子制御/全cleanup/通常Question/Web/Logout/QA045/実NK互換gateは未完了、固定加重約4割（35～50%、456）を維持。利用枠残85%で継続、元dev-web3file保全、IT/ST完了ではない。以下は履歴。

最新確定: 正式PT-WEB-20260909-12、source 970681dfb6e2a0ba021c71402cdc5b69fb950b0d、dev-web、2026-09-09 03:27:49～03:32:41 JST。全790件（Protocol80/Storage34/API394/Web241/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Web165件、Admin73、Inbox11+3+4、Media61、Scenario155/Auth91等は重複する内数。API0102のlocal session破棄/HTTP終端/全result分類8件を追加PASS、DB削除前・commit故障/実HTTP/100並行/新Login非削除を確認、SSC-048完了、7collector収集成功。CHR41はrunner単体試験であり実NK互換gateではない。Logout revoke queue・本番logger固定/残画面/全layout登録/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、再走待ち1件（RERUN-001/SSC-045、455のLogout期限設計）。PG-D-118のScenario6電文clientとPT166～173を先行仕様化し、画面接続へ継続する。以下は履歴。

最新確定: 正式PT-ADM-20260908-04、source 1f1d321ad40bd7ba5f8461e5954e94e7ac6142d3、dev-admin、2026-09-08 15:59:29～16:03:00 JST。全571件（Protocol80/Storage34/API340/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin23、Media61、Scenario151/Auth91等は重複する内数。User作成/状態/role/password/unlock、実PG監査・全session失効・故障rollback・独立PBKDF2/USRMUT24・並行raceを追加PASS。BUG-045～047/YKT-040～042は再試験完了。正式03は静的解析失敗で非合格。SSC-031の外側Inbox接続とSSC-032の新規canonical接続、HTTP/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。以下は履歴。

最新確定: 正式PT-ADM-20260908-02、source c828f77ec11b1b0727724050323700c19b04dc76、dev-admin、2026-09-08 15:13:34～15:16:56 JST。全561件（Protocol80/Storage34/API330/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin13、Media61、Scenario151/Auth91等は重複する内数。SSC-031の管理認証prelude・実相互target/role再検証/100並行・全faultを追加PASS。SSC-031はUser command/Inbox接続まで対応中。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。User更新本体・HTTP/起動/実NK CHRと未完了Program、QA-045承認依存は継続。以下は履歴。

最新確定: 正式PT-ADM-20260908-01、source 9cbdfa1ae9dfda67557f48405c55a6a019294b71、dev-admin、2026-09-08 14:58:00～15:01:23 JST。全555件（Protocol80/Storage34/API324/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin照会7、Media61、Scenario151/Auth85等は重複する内数。User一覧/詳細・独立wire/実PG権限/NULL/時刻/容量・close/100並行をPASS。User更新接続前にSSC-031の認証/target lock順を先行補足し、PT-ADM-008～013は未実施。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。HTTP/起動/実NK CHRと各未完了Program、QA-045承認依存は継続。以下は履歴。

最新確定: 正式PT-MED-20260908-11、source 34ba78f138fd1e1db0cca48501f9b787ff4c526e、dev-media、2026-09-08（開始終了日時はmanifest）。全548件（Protocol80/Storage34/API317/Web76/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media61件（他Programと重複する内数）。8queryの認証/Inbox→DB外の実file→最新認証/確定→実JMS送信・ACK、100同一Message再送と障害回復を追加PASS。BUG-044/YKT-039の時刻oracle再試験完了。Web session/security・HTTP/画面/起動登録/実NK CHRは残件。確定5/20=25%（Program件数比、工数換算なし）、明確な行き詰まり0件。SS362順でUser管理APIのPG/PTへ進む。以下は履歴。

最新確定: 正式PT-MED-20260908-10、source 9b152e0797948d1f346855bf5441164a46804618、dev-media、2026-09-08 13:58:53～14:01:59 JST。全541件（Protocol80/Storage34/API310/Web76/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media54件（他Programと重複する内数）。全8応答snapshot/独立JCEと手組wire/改変拒否/100並行を追加PASS、BUG-043/YKT-038のBerror oracle是正・再試験完了。実認証Inbox/file/JMS段階接続・HTTP/起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-09、source c5de0e44d433180680c0c87b1c32612d7b37060e、dev-media、2026-09-08 13:43:18～13:46:23 JST。全536件（Protocol80/Storage34/API305/Web76/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media49件、Scenario151等は重複する内数。checksum manifest/実保持asset metadata・59,627合成件数・異常/100並行を追加PASS、BUG-042/YKT-037再試験完了。認証Inbox/応答snapshot/実HTTP・起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-08、source c2f0bddf6ac741d1a743bad0792a60dc2f69caa5、dev-media、2026-09-08 13:19:55～13:22:59 JST。全527件（Protocol80/Storage34/API296/Web76/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media40件、Scenario151等は重複する内数。SSC-030を上位wire/credentialに整合化し、手組応答のlayout/correlation/context64位置/全descriptor・error profile/100並行を追加PASS。manifest/認証Inbox/応答snapshot/実HTTP・起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-07、source 2a0939a7962e93f89c7541d6f5dfb6de6520601a、dev-media、2026-09-08 13:05:36～13:08:38 JST。全523件（Protocol80/Storage34/API296/Web72/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media36件、Scenario151等は重複する内数。SSC-029の8要求decode/独立canonical HMAC/実query振分けと共通field factory・Scenario非回帰を追加PASS。manifest/認証Inbox/応答snapshot/実HTTP・起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）。SSC-030の応答検証責務整合を先行起票、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-06、source 279f72798abfbfe5d2db7e30f0d4a2dc46c2eebb、dev-media、2026-09-08 12:52:59～12:56:03 JST。全519件（Protocol80/Storage34/API292/Web72/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media32件、Scenario151等は重複する内数。Web descriptor-file接続と内部Response portの200/206/416・HEAD/download・20/21枠/故障解放/100並行を追加PASS。manifest/API認証Inbox/MQ-実HTTP接続・client abort分類/起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-05、source 6c9c4bcf6a75315cb174cd46c68a03bb6eedf081、dev-media、2026-09-08 12:43:33～12:46:37 JST。全512件（Protocol80/Storage34/API292/Web65/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media25件（Storage8を含む）、Scenario151等は重複する内数。保持全segment/前後Unix属性・size/256階層/48MB超/100並行/故障の低位file accessを追加PASS。manifest/API認証Inbox/Web descriptor・20permit/HTTP/起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-04、source 46c09773eb5a994dd1f6f7d37dbd6051fa91eac7、dev-media、2026-09-08 12:35:32～12:38:36 JST。全507件（Protocol80/Storage29/API292/Web65/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media20件、Scenario146件等は重複する内数。SSC-028の保持child/entry・正サイズ属性共通化3PTを完了。Asset全walk/manifest/認証Inbox/20permit/HTTP/起動/実NK CHRは継続。確定5/20=25%（件数比・工数換算なし）。詳細はmanifest、以下は履歴。

最新確定: 正式PT-MED-20260908-03、source 6fa233d4ee69e8eff4ccbd155d0ffb028589981d、dev-media、2026-09-08 12:24:43～12:27:45 JST。全504件（Protocol80/Storage26/API292/Web65/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media17件（Range/header/stream7＋DB menu/list7＋3 descriptor query）成功。DB metadata取得は物理fileの配信許可ではない。manifest/認証Inbox/実asset/20permit/HTTP/起動/実NK CHRは継続、確定5/20=25%（件数比、工数換算なし）。詳細manifest/Test ID/hash、以下は履歴。

最新確定: 正式PT-MED-20260908-02、source dc580fc7ed9c9f608430072b1ddf5caaf646eaae、dev-media、2026-09-08 12:14:50～12:17:52 JST。全501件（Protocol80/Storage26/API289/Web65/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。 Media14件（先行Range/header/stream7＋実PG menu/list7）成功。各Programの内数を重複加算しない。descriptor/manifest/認証・実asset/20permit/HTTP/起動/実NK CHR等は未完了、確定5/20=25%を維持。詳細manifest/Test ID/hash、以下は履歴。

最新確定: 正式PT-MED-20260908-01、source d986d3e3163069522fa052491a7431f865d673f7、dev-media、2026-09-08 11:59:40～12:02:43 JST。全494件（Protocol80/Storage26/API282/Web65/CHR41）、failed/error/skipped0、全5moduleのline/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。 Media7/Scenario143/Auth85/Inbox11+3/PRO00317は重複する内数。Media Range/header/bounded stream部品PASS、API query/descriptor/認証・asset/manifest・20permit/HTTP/実NK CHR等は未完了。確定Programは5/20=25%（件数比、工数換算なし）。詳細は対応manifest/Test ID/hash、以下は履歴。

最新確定: 正式PT-SCN-20260908-23、source e6b4368407043850f0d11a8227d5577977f4868c、2026-09-08 11:46:25～11:49:26 JST、全487件（Protocol80/Storage26/API282/Web58/CHR41）。failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。 BUG-038～041/YKT-034～036の現存対象再試験完了。NK-PRO-003復帰、確定5/20=25%（件数比・工数換算なし）。Scenario内部段階service T01～T07はPG/PT PASS。full startup/単一instance/登録/readiness・HTTP/実NK CHR、他Programは未完了。 以下は履歴。

2026-09-08 11:46 暫定判定: BUG-040/YKT-036のstorage拡張子検証漏れを修正前起票し、NK-PRO-003完了を再試験まで保留。確定4/20（20%、工数換算ではない）。正式22は全486件/coverage100%/静的解析0だったが、collectorのTest ID完全名誤りBUG-041で収集未完了。以下の過去完了表示を現在判定としない。BUG-038/039の再試験と併せ、source/collectorを固定した正式23へ進む。

最新: 正式`PT-SCN-20260908-20`、source `e9d89e5a339320cc57dd7f50b9bb40810edd2a43`、dev-scenario、2026-09-08 11:02:42～11:05:27 JST。全479件（Protocol79/Storage26/API275/Web58/CHR41）、Scenario関連136/Auth85/coordinator11/置換3（重複を全体総数へ再加算しない）。failed/error/skipped0、5対象module全coverage100%、NullAway/Enforcer/format PASS、SpotBugs0。 SSC-027のsnapshot置換SQLも内部PG/PT完了。確定5/20=25%（工数換算なし）。段階service/実writer・JMS接続、full startup/readiness、HTTP/実NK CHR等は未完了。

最新判定（2026-09-08 10:43）: BUG-037/YKT-033を正式再試験完了しNK-PRO-003復帰、確定5/20=25%（Program数比、工数換算なし）。正式`PT-SCN-20260908-19`、source `e46555c4dbfa5449e06f4c871b2aaa7fc4ec493a`、dev-scenario、2026-09-08 10:40:52～10:43:33 JST。全476件（Protocol79/Storage26/API272/Web58/CHR41）、Scenario関連133/Auth85/coordinator11（重複を全体総数へ再加算しない）。failed/error/skipped0、5対象module全coverage100%、NullAway/Enforcer/format PASS、SpotBugs0。 SSC-026保存・再送部品完了。SSC-027のguard/実ready検査/元content再生成・descriptor置換の内部10追加PTもPASS、最終DB接続は継続。段階service/実file再生成/起動/HTTP/CHR等は継続。

## 1. 位置づけ

追加管理資料: [459_保守run固定時刻の永続化検討](450_品質/459_保守run固定時刻の永続化検討.md)（SSC-055調査中、固定cutoffの設計残件。未完了）。

再開時の残件整理: [460_基盤残件・再開優先順](450_品質/460_基盤残件・再開優先順.md)。確定部品/不足するProductionとPT/後続Linux IT・STを区別する。新たな完了認定ではない。

本ディレクトリをschubert NK再構築projectの製造・単体テスト（PGPT）工程における文書最正本とする。外部仕様の最正本は`documents/100_RD`、`documents/200_UI`、実装・試験詳細の最正本は`documents/300_SS`であり、本工程の文書・code・test・evidenceはそれらを変更せず具体化する。

開始基準は`main`のSS最終commit `749a777`、Characterization baseline/gate commit `843de94`、CHR-G01～G06全件PASS、QA-001～044解決、UIC-001～004完了、RDF/SSC 0件である。PG開始時精査でQA-045/UIC-005、SSC-001～003、BUG-001/YKT-001を起票した。

## 2. 成果物一覧

| 文書 | 目的 | 状態 | 更新条件 |
|---|---|---|---|
| [411_コーディング規約](410_工程標準/411_コーディング規約.md) | Java 25実装・test共通規約 | 確定 | 規約変更時 |
| [421_開発環境・toolchain構築記録](420_環境/421_開発環境・toolchain構築記録.md) | version、入手元、設定、再現手順 | 作成中 | tool導入・更新時 |
| [431_Module・Program一覧](430_構成・追跡/431_Module・Program一覧.md) | Module/programとRD/UI/SS/PTの追跡 | 作成中 | program/test追加時 |
| [441_実装判断記録](440_判断/441_実装判断記録.md) | SSより詳細な内部判断 | 作成中 | 判断確定時 |
| [451_Build・静的解析・coverage方針](450_品質/451_Build・静的解析・coverage方針.md) | 品質gateと実行方法 | 確定 | gate変更時 |
| [452_継続走行・再走管理](450_品質/452_継続走行・再走管理.md) | 長時間走行の依存関係・行き詰まり・再走条件 | 運用中 | 走行状態・再走対象の変更時 |
| [453_Null解析gate検証仕様](450_品質/453_Null解析gate検証仕様.md) | 解析器の負canary・JDBC NULL境界 | 検証済み | null gate設定・結果の変更時 |
| [454_Build契約・整形・再生成gate検証仕様](450_品質/454_Build契約・整形・再生成gate検証仕様.md) | 固定整形・依存収束・70生成fileの再現 | 検証中 | Build/生成toolの変更時 |
| [455_再走論点_RERUN-001_Logout期限](450_品質/455_再走論点_RERUN-001_Logout期限.md) | Logout queue削除期限の設計論点・再走条件 | 再走待ち/SSC-045 | 安全性の証明・再試験時 |
| [456_領域別進捗・利用枠・中断再開管理](450_品質/456_領域別進捗・利用枠・中断再開管理.md) | 暫定加重進捗・基盤完了条件・10%/5%停止・未検証変更の保存 | 運用中 | 領域の検証済成果・残量・中断理由の変更時 |
| [457_Inbox削除保護の実行主体・承認論点](450_品質/457_Inbox削除保護の実行主体・承認論点.md) | BUG-014の検査主体と権限境界、代替案、承認後のPT条件 | QA-046承認済み/UIC-006・SSC-049対応中 | 回答・設計確定・検証時 |
| [458_証跡scope横断gate・BUG099_100](450_品質/458_証跡scope横断gate・BUG099_100.md) | 正式26の集約非合格、分類修正・全scope同時点性と再試験 | 正式27で再試験完了、現在は運用中 | collector/必須scope変更時 |
| [459_保守run固定時刻の永続化検討](450_品質/459_保守run固定時刻の永続化検討.md) | reboot前後のrun原本・再attempt/保持の未確定事項 | SSC-055調査中 | 設計再走時 |
| [460_基盤残件・再開優先順](450_品質/460_基盤残件・再開優先順.md) | 部品/親結線/PGPT・ITSTの境界と次手順 | 残件整理中 | 完了根拠・依存関係の変更時 |
| [461_PG完了報告](460_完了報告/461_PG完了報告.md) | PG完了判定 | 工程未完了・判定保留 | PG gate完了時 |
| [462_PT完了報告](460_完了報告/462_PT完了報告.md) | PT完了判定 | 工程未完了・判定保留 | PT gate完了時 |
| [463_PGPTフェーズ完了報告](460_完了報告/463_PGPTフェーズ完了報告.md) | PGPT総合完了判定 | 工程未完了・判定保留 | 全gate完了時 |
| [464_IT・ST引継ぎ事項](460_完了報告/464_IT・ST引継ぎ事項.md) | Linux server後続工程への引継ぎ | 作成中 | 未実測値・制約判明時 |
| [915_障害表](../900_OTHER/910_台帳/915_障害表.md) | 実装済み処理の仕様違反管理 | 運用中 | 障害発見前に起票 |
| [916_横展開管理台帳](../900_OTHER/910_台帳/916_横展開管理台帳.md) | 共通原因の全対象確認 | 運用中 | 横展開対象判明時 |

Program単位PT仕様・結果・sanitized evidenceは`evidence/01_PT/NNN_<Program-ID>/`を最正本とし、Test IDでcode・仕様・結果・manifestを一意に結ぶ。

## 3. 工程進捗

| Workstream | 状態 | 完了条件 | 現在値 |
|---|---|---|---|
| 開始時確認 | 完了 | status/branch/commit/remote/既存変更確認 | `main`/`749a777`、clean、既存remoteなし。指定URLを`origin`へ設定 |
| Remote整合 | 完了 | fetchでremote履歴との一致を確認し、通常push | 2026-09-04にGitHub認証を確認。空remoteへ`main`、`dev`、既存feature branchをforceなしでpush済み |
| 上位資料精査 | 完了 | RD/UI/SS全資料と台帳・baselineの追跡完了 | RD 16、UI 29、SS 24文書とCurrent/CHRを横断確認 |
| 工程基盤 | 整備中 | 規約、toolchain、全品質gate、915/916確定 | rootless JDK/Maven、台帳、compiler/coverage/SpotBugs/NullAway稼働。Enforcer/formatは検証済み、PMD等の残gateを追加予定。文書上の方針確定だけで全gate完了とはしない |
| Characterization是正 | 完了 | BUG-001/YKT-001再試験PASS | commit `8cfaa9b`/`57f9ac2`、41/41、coverage全100%、run 05/06・G01～G06 PASS |
| PG | 実施中 | 全program実装、build/static analysis/関連CHR PASS | 確定完了5/20（25%、工数換算ではない）。NK-DAT-001はBUG-014により再確認中。NK-MSG-002のHTTP/Inbox保護/業務stressと、NK-AUT-001の全layout dispatcher・起動/管理command/expiry・Web recovery/HTTP/CHR接続が残る。NK-SCN-001の5 query＋detail snapshotを実装・PT（全476件/Scenario関連133、e46555c）。Native directory能力部品/100並行非上書き/保持FD差替え防御を追加。保持inode・owner/group/mode/nlink/sizeを追加PT。I/F配送投影とatomic容量予約は部品PASS。Root論理非重複/保持属性・ext4/SDS検査は部品PASS。CREATE_NEW/属性設定/最大48MB write・hash/再試行/公開・清掃/100並行と容量の内部writer接続PASS。Web内部read-only readerの最大48MB/100並行・属性/hash二段検証・途中改変/リンク/close故障拒否PASS。起動前metadata scan・0byte part算入・複数dateを跨ぐ9000/10000/10001件境界・列挙/close/差替え故障拒否PASS。自作診断fileの起動probe（force/group/hash/no-replace/fsync/所有別清掃・不確定ready保全）PASS。全root実体/exclusive起動結線/readiness・scan-to-service初期化とwriter service登録/認証Inbox/HTTP/CHRは未完了。匿名Login Inbox/JDBC・実JMS再配送、owner付きLogout Inbox/replay、任意監査IP、stage時計進行、管理session全失効とcritical監査を実DBで確認した。 |
| PT | 実施中 | 全PT PASS、line/method/class/branch 100%、skip等0 | 確定完了5/20（BUG-023再試験で復帰）。Run PT-SCN-20260908-19全476件成功（Protocol79/Storage26/API272/Web58/CHR41、Scenario関連133＋横断追加3）、Java coverage100%、SpotBugs/NullAway0、Enforcer/format PASS。Auth85件は実Login/Logout/管理失効/監査/rollback/競合を含む。Login replay保存/再構成・匿名HMAC/Inbox/application原子接続/100同時再配送を追加。BUG-022～036/SSC-010～016/018直接対応完了。YKT-032の4class13method・caller monitor独立再試験完了、SSC-019はwriter/root admission接続待ち、SSC-017のquery/detail補正は反映済み・file接続試験待ち、YKT-022/023/024/026完了、YKT-019/021/025後続対象は継続。BUG-014 Inbox保護、Auth 全layout dispatcher・起動/expiry・Web recovery、残業務・PMD等の全体gateは未完了。 |
| PGPT完了 | 未着手 | 451の全gate PASS、worktree clean、push/PR済み | 未判定 |

## 4. 進捗更新規則

- PGとPTはprogram単位で同時に進め、production codeだけが未試験の状態をdevへ取り込まない。
- `Failed`、`flaky`、`skipped`、`not-run`はPASSへ算入しない。
- 上位仕様の確認・変更は911～914の分類に従い、台帳登録前に質問やoracle変更を行わない。
- 実装済み処理の仕様違反は修正前に915、共通原因または予防確認は916へ起票する。
- Current baselineはread-onlyとし、NK結果へ合わせて更新しない。
- IT/STは本工程の完了宣言対象外とする。

## 5. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-07 | Web log sender/dispatcherと追加9試験を実装、正式Run PT-IDEM-20260907-01全251件成功・coverage100%・SpotBugs0。BUG-013修正、YKT-009～011完了。NK-MSG-002はAPI ingest/HTTP投影等を残し継続、完了率6/20=30%据置。 |
| 2026-09-01 | PGPT工程開始。開始基準、成果物構成、初期進捗を登録。 |
| 2026-09-02 | Characterization是正とNK-CHR-001 PG/PTを完了。Production module着手gateを再確立。 |
| 2026-09-02 | Protocol基盤33件の中間gateをPASSし、NK-PRO-003をPG/PT完了。NK-PRO-001/002は未実装範囲を残し継続。 |
| 2026-09-02 | Protocol 43 PT、389 field catalog、64 layout success/error codecの中間gateをPASS。BUG-003/YKT-003を修正・再試験。 |
| 2026-09-02 | Protocol 48 PT、SS 323の69 named record・64明示mapper・独立型fixtureの中間gateをPASS。 |
| 2026-09-02 | Protocol 52 PT、日時/UUID/context/SHA/path semantic型の中間gateをPASS。BUG-004/YKT-004を修正し、全reactor非回帰を確認。 |
| 2026-09-02 | Protocol 56 PT、N12 ID、primitive数値、X numeric、18 wire enumを含むSS 323共通Java型を完了し、NK-PRO-001をPG/PT完了。 |
| 2026-09-02 | Protocol 67 PT、layout相関、NTCRSP01/0107個別field、64 layout min/max/error golden、最大record・並行試験を完了し、NK-PRO-002をPG/PT完了。 |
| 2026-09-03 | PostgreSQL 18.6/Flyway V001～V005、21 table、constraint/index/role/grant/view、6 maintenance functionとPT-DB-001～015を完了し、NK-DAT-001をPG/PT完了。SSC-005のSecurity hold物理化を含む。 |
| 2026-09-03 | `dev-data-schema`をlocal `dev`へno-ff統合。GitHub credential不在でpushは継続阻害中。`dev-messaging`を作成し、NK-MSG-001/002のPT仕様と実装を開始。 |
| 2026-09-03 | Production `broker.xml`、実NIO File Journal/restart/redelivery/transaction PT、JMS guard/factory/DLQ、Web module相関registryを中間実装。API 46件・Web 5件、coverage全100%、SpotBugs 0を確認したが未実施caseを残しProgram完了とはしていない。 |
| 2026-09-03 | Web request/reply clientの12並行wait、13件目拒否、timeout/interrupt/send失敗cleanupを実装・試験し、Web中間gateを13件へ更新。 |
| 2026-09-03 | 実Artemis ACL 90組合せ、全route/provider負値、DLQ/Expiry再起動保持、production request senderを追加。API 50件・Web 16件とcoverage全100%/SpotBugs 0を確認。 |
| 2026-09-03 | API Reply/DLQ senderをlistener所有transactionへ実装し、commit前不可視・rollback・commitとproperty/body契約を実brokerで確認。API 52件、coverage全100%、SpotBugs 0。 |
| 2026-09-03 | Web reply decoder/consumerとbody/type不変DLQ隔離を実装。active/late ACK、恒久不正commit後fatal、隔離失敗rollbackを実broker/negative PTで確認し、Web 27件・coverage全100%・SpotBugs 0。 |
| 2026-09-04 | GitHub認証復旧後、空remoteへ`main`、`dev`、全既存feature branchをforceなしでpush。remote阻害を解消。 |
| 2026-09-04 | NK-MSG-001最終run `PT-JMS-20260904-01`を実施。PT-JMS 12/12、関連JUnit 65/65、全reactor 199/199、coverage全100%、SpotBugs/secret/CRLF/NUL/skip等0でPG/PT完了。 |
| 2026-09-04 | NK-MSG-002のResponse snapshot圧縮/AES-GCM/`NKENC1`/AAD/key rotation、平文・暗号文上限と圧縮bomb防御を中間実装。BUG-007/008を修正し、Protocol 69件・API 68件、coverage全100%、SpotBugs 0を確認。 |
| 2026-09-05 | NK-MSG-002のInbox coordinator、Message ID/owner-token/HMAC replay、caller所有transaction・savepoint競合回復を実装。PT-IDEM-001～008をProtocol 69件・API 79件、coverage全100%、SpotBugs 0で中間PASS。 |

## 2026-09-08 電文接続監査の再判定

BUG-023/SSC-012でNK-PRO-002を一時保留した後、正式Run06（8fed52b）全317件/独立error vector/全coverage100%で是正を確認し完了へ復帰。現在の確定完了は5/20（25%、工数換算ではない）。追加Auth mapperも試験済だがAuth Program全体は未完了。
