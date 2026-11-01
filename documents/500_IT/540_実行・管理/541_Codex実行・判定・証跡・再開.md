# Codex実行・判定・証跡・中断再開手順

## 1. この仕様書を受け取ったCodexの最初の操作

この文書自体は実行許可を与えない。PGPT完了後のIT実行依頼と正規scopeを確認してから、baseline/cases/conditions/issuesのhashを読む。今回全結果NOT_EXECUTED。既存実行中job/停止VM/原本/鍵/intent/permit/stashを変更しない。

1. 設計用隔離checkoutでfetch origin mainし、baselineのdesign commitとの差分をRD/UI/SS/911〜914へ限定して保存する。設計基準版/最終版/差分SHAをmanifestへ記録する。
2. 条件IDの原文hashが変わったもの、新設・削除・節移動、承認QA/UIC/SSCの状態差を抽出する。削除条件も履歴を残す。文書/節が同じだけで不変更と認定しない。
3. 最終releaseのsource/branch/tag/SBOM/JAR/全lib/SQL/config/Unit/署名/asset/data/toolのSHAと、最終PGPT完了461/462/463・451各gate・464残件・最新456/460/485/486を照合する。source不一致の過去正式PASS/native成功は新sourceへ補完しない。
4. 差分を「期待値/状態/部品契約変更」「実装のみ修正」「設定/環境/工具/データ変更」「文書のみ」に分類し、conditions→case assertion→fixture/oracle→PT/IT/ST/OTへ影響を伝播する。無影響にも具体的理由を残す。
5. 変更ケース/対応表/未確定台帳を更新し、期待結果の独立性と準備物を再レビュー。判断待ちをCONFIRMEDへ自動昇格しない。PGPT完了・仕様確定・実行可能の各署名欄を個別承認する。
6. release/config/schema/protocol/credential ID版/environment/fixture/tool manifestと開始gateが全一致したケースだけ選択する。文書差分だけのために製品試験を発行しない。

## 2. 実行束縛と準備（今回未実施）

`run-template.json`をGit外の新規private0600領域へ複製し、run UUID/人が読めるrun名・対象source・環境digest・spec commitを記入する。公開版は非秘密投影で作る。scope承認ID、復旧点、操作対象、外部依存の所有、全job一覧を記録する。秘密値をenv/argv/URL/logへ渡さない。

工具T-*は513の仕様に従って別途実装・reviewし、最終入口を `tool-manifest` の実path/sha/argv/cwd/環境allowlist/作用/timeout/cleanupへ固定する。未作成commandを創作して実行しない。検証SQL packもSQL本文/hash/param schema/期待列/権限をreviewする。既存018 collectorはPT専用であり自動転用しない。

環境準備は512のE-REAL/E-OPS/E-RESTOREとC-ISOLATE。provisioning/migration/credential配布は実行依頼の許可範囲と既存HOLDを確認した準備工程でのみ行う。準備完了時に全構成/設定/権限/DB/Queue/file・restore点の前後snapshotを確定し、ケースのinputと結合する。最終release artifactがないなら実行準備未了。

## 3. ケース実行の順序と判定

caseはJSONのcommon_profileと個別全項目をmergeして解釈する。個別値が優先し、未指定を推測しない。matrix入力は順序・期待値を保持したvariant IDを採番し、各variantを独立cloneへ実施する。100反復はseed/iteration1..100を保存、反復数をTest数へ水増ししない。

1. 予約キー=`releaseDigest/environmentDigest/caseID/variantID/attempt`。T-RESUMEのO_EXCL予約とOS所有lockを取得し、同じキーのRUNNING/UNKNOWN/途中原本がないことを確認する。
2. `RESERVED→PRECHECKED→SETUP→READY`をdurable append-onlyで記録する。全開始条件/fixture/oracle hash/initial count/side-effect allowed setを確認する。
3. collector開始→barrier登録→操作入力のSHA確定→一回dispatch→`DISPATCHED/RUNNING`。request Message/Correlation/token/receipt/DB PK/file ID/jobはprivate bindingに記録する。
4. caseの同期条件を待つ。HTTP2秒、DB/API1500ms、lock500ms、stop30/60秒、Morning1800秒等の製品境界とcase watchdogを別時計にする。watchdog内の遅い成功を製品timeoutの成功へ変換しない。
5. `COLLECTED`後、各assertionにexpected・actual・判定式・証跡path/SHA/測定区間・許容根拠・判定を保存する。必須証跡不足/unknown/collector失敗はPASS不可。仕様TBDはNOT_JUDGED。
6. 全assertion true、非更新条件成立、全相関/版/証跡hash整合で `JUDGED_PASS`。不一致は原失敗を保存して `JUDGED_FAIL`、原因は未判定から始める。
7. 後片付けは判定とは別に `CLEANUP_PENDING→CLEANED`。故障解除・自己所有worker/FD/lock/Unit/許可外差分0・snapshot復旧/正常readyを確認し、最後に予約を完了する。判定PASSでもcleanup未確認ならrun完了不可。

JUnit XMLが必要なら1 testcase=case/variant/attempt、failure/error/skipped/not-runを区別し、XML0件を成功にしない。実行状態ledgerの正本はJSON、Markdownはrenderのみ。ITケース本文へ実測を書き戻さない。

## 4. 証跡配置と保全

run/<case>/<variant>/<attempt>/に `input.manifest.json`、`environment.manifest.json`、`timeline.jsonl`、HTTP/DOM安全投影、wire安全投影、DB前後/lock、Queue、file metadata/hash、Unit/metric、`assertions.json`、`cleanup.json`、`SHA256SUMS` をnew-only保存する。秘密rawは別private subtree。公開manifestはprivate原本へのopaque参照とhashだけを持つ。

collection途中もstageごとにforce/renameで確定し、元fileを上書きしない。原失敗/rawを保全せず環境だけ清掃しない。DB/Outbox/Queue/fileの削除は後条件採取と対象確定後に限定し、PENDING/DLQ/UNKNOWNを一括purgeしない。canary検査・同run/source/artifact/env/case/attemptのjoinが失敗なら公開/合格を止める。

## 5. 中断・再開

再開時は、spec/design/source/artifact/config/schema/protocol/fixture/tool hash、host/boot/PID/startTicks/job ID、現在stage/heartbeat/予約lock、Message/token/receipt/PK/lease、既存Queue/DB/file、証跡hash/末尾確定eventを照合する。PIDだけ、session消失だけ、heartbeat期限だけで未実行とはしない。

| 観測 | 再開動作 |
|---|---|
| 同所有jobがRUNNING | 元jobを観測してcollectorだけ継続。新dispatch禁止 |
| dispatch前と証明済み・資源未取得 | 同予約を正規引継ぎ後setup再開、source/env driftがあれば新plan |
| dispatch後・DB/JMS commit確認済み | 同Message/tokenを正規再送仕様で照合し既存結果を観測。勝手な新token発行禁止 |
| commit/close/停止/所有がUNKNOWN | 原job/証跡/ownerを保全しHOLD。新環境や別driverで同検証を迂回しない |
| 完了証跡/cleanupが揃う | 既存結果をそのまま検証し終了、再実行を新PASSとして加算しない |
| 修正後の再試験が必要 | 原失敗IDへ紐づく新attempt。必要変更/回帰選択を542で確定 |

停止要求は既定のgraceful/正規所有経路だけ。SSのUNKNOWN保持や承認をshell kill/force resetで置換しない。長い運転中も60秒以内に短い進捗/残り不確定を報告できる非blocking job/collectorを準備する。
