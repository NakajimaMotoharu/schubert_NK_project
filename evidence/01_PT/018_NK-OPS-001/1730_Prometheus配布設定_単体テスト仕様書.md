# 1730 Prometheus profile配布設定 単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07、RD171 MON005010011012013/UI252§5・253§6/SS342§5.2・343共通mode・351§6/8。PG-D580。group1957/P01809_OFFLINE_PROM_CONFIG_V1、PG8138 fresh receipt、開始0.75/2/5pp・cap10。原/v4/v5固定、実費/工数null・共有枠差は専有費ではない。

## 対象と着手前判定

src/deployment/monitoring/prometheus/{debug.yml.template,standard.yml.template,debug-arguments.json.template}を新規製造し、同directory READMEへ適用/未受入事項を記す。PT_DEFAULT：公開templateの読取、独立literalのJSON subset YAML構造照合、テスト自身のmemory内mutantだけ。daemon/promtool/network/DB/VM/Root/credential/配置/service/read actual storage等0。未知の拒否範囲と依存しない。実runtime/source/所有/HOLDを推測しない。

DEBUGはSS342固定Web127.0.0.1:8081/API127.0.0.1:8091、GET /actuator/prometheus、二jobのみ。IPv4loopback以外/リダイレクト/環境proxy/remote storage/discovery/credential/canary/動的labelを追加しない。アプリの詳細26metric公開は未受入であり、当設定が取得結果を捏造しない。STANDARDは空scrape_configs/remote/ruleなく、誤ってdaemonが稼働しても収集しない防御層であり、service停止の代用ではない。

設定はJSONのYAML subsetでコメント/変数展開なし。JSON duplicate keys/nonfiniteは独立test readerが拒否する。global scrape_interval=15s/scrape_timeout=5sはSS未指定の内部初期値、独立vectorで固定し性能合格を主張しない。固定job名schubert-nk-web/api以外のラベル追加0、secret/query/body/log内容なし。専用port/daemon選定/version/install/監視user/permission・実exporter互換はこの変更で定めない。

debug-argumentsは配布用data（実行scriptでなく自動実行禁止）。固定loopback listen127.0.0.1:9090は内部既定値、config/data pathは専用監視配布先の候補としてREADMEに留保。retention.time=15d/retention.size=5000000000Bをbyte明記しbinary5GBとの差を避ける。Prometheus TSDBの背景cleanup/WAL/head/compactionはこの設定でhard上限とならないため、総容量5GB/保存15日の実成立は未受入。自動削除/volume作成/既storageへ適用0。STANDARD用retention0を渡して無制限運転させない：STANDARDはdaemon停止＋空収集設定。

## 独立Test ID

全入力は当3template、操作はread/parse/compare又はmemory内変異のみ。expectedはSS固定port/path/modeと以下literalで、production helperから生成しない。

|Test ID|目的と期待値|
|---|---|
|PROMCFG001|DEBUG全documentを独立literalへ厳密比較、二固定target/15s/5s・GET path/http、未知key/label0|
|PROMCFG002|STANDARD厳密空scrape、target0、remote/rule/credential0|
|PROMCFG003|argv全順序を固定literal比較、15d/5000000000B/loopback、remote/admin/lifecycle0|
|PROMCFG004|DEBUG/STDの入替え・同一化・欠落・null・空/未知設定を不一致として拒否、JSON duplicate/nonfinite/末尾document拒否|
|PROMCFG005|各jobのtarget/port/path/scheme/method/proxy/redirect値変異と未知key挿入を拒否、原入力不変更|
|PROMCFG006|retentionの5GB/5GiB/0/-1/5000000001B・time0/14d/16d・listenwildcard/外部・pathずれ/追加argvを拒否|
|PROMCFG007|数値/Boolean/nullの型偽装とglobal/time/targetsのcollection構造・過剰/欠落job/再順序を厳密拒否|
|PROMCFG008|全3対象＋READMEの実Git/source/hash/trace・非実行data、元src/POM/原1669/root等未変更と記録|

Program単位はDEPLOY-PROM-CFG（上3artifact）。Java class/method/NPE/並行/再送は当dataに非適用、readerはnull/欠落/型境界を上記で検証、daemon並行・再送・runtimeは未実行。line/method/class/branchのJava四coverageを当configのsemantic PTへ転用しない。Python helperの負例は検証器確認でありProduction Java試験へ加算0。configuration自体に命令/branchはなく構造/全field/異常変異を対象にする。

## 実行/証跡

予定command：env PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<既pyflakes runtime> python3 -B tools/quality/pg8140_prometheus_config_pt.py。src/spec/testをsource固定してから実行する。OS/Python/branch/commit/command/開始終端/exit/TestID/expected/actual/hashとBUGはPG8140 manifest/1731へ。必要時は修正前915/916へ起票し期待値を結果追従させない。

当工程はファイル製造＋独立semantic PT。公式Prometheus binary/promtool parser、起動・scrape・endpoint内容/loopback socket/daemon停止/保存・上限/owner/permission・Grafana/exporter/全26series・451全scopeはUNRUN/HOLDで合格へ混ぜない。元4222/common44を再演せず、変更はJava/POM/既deploymentに及ぼさないため正常六compile/旧coverage確認目的再演なし。正式1964/53・原190新受入0・effortnull・QA051final/PTALT0・全actualHOLD不変更。

## 外部構文・実装判断の根拠（2026-10-24参照）

- https://prometheus.io/docs/prometheus/latest/configuration/configuration/ ：YAML/global/scrape/static target/http設定の一次資料。文書latestで製品version認定ではない。
- https://prometheus.io/docs/prometheus/latest/storage/ ：size単位はpowers-of-two、Bでdecimal5000000000を明示。永続block削除/背景遅延とWAL/head/compactionのため設定値だけで総使用量を保証しない。
- https://prometheus.io/docs/prometheus/latest/command-line/prometheus/ ：listen/config/storage/time/size flag形。実binary入手/実行/version資格は未実施。
