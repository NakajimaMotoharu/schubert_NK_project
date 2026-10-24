# 1735 Grafana配布設定 単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON010～013/UI252§5/253§6/SS351§8/9、PG-D582。group1962/P01809_OFFLINE_GRAFANA_CONFIG_V1、PG8154fresh receipt、開始0.75/2/5pp/cap10・fresh18残82/reset1793382075。元/v4/v5・実N/T/工数null維持。

## 選定根拠・対象

1734の後続索引を先行し、Grafanaは1540/1541/1699/1730/1731に未稼働・未配布の留保、grafana.ini一致0。現tracked src/deploymentはPrometheus三dataだけでGrafana config/artifact無し。これは当sourceと公開範囲のgapであって、全hostの不存在推定でない。新規対象はsrc/deployment/monitoring/grafana/{grafana.ini.template,datasources-debug.yml.template,datasources-standard.yml.template,README.md}。

PT_DEFAULT：公開data read/strict INI・JSON subset YAML構造、固定独立oracleとmemory変異のみ。Grafana daemon/API/アカウント/DB/鍵/ネットワーク/VM/Root/配備/既storage操作0。新データは実行scriptでなく、C07 runtime/正式受入を増やさない。新role/外部認証仕様を勝手に決めない。

INIは候補loopback127.0.0.1:3000/http、data/provisioning候補pathを明示、初期admin自動作成を無効・anonymous/signup/org-create無効。auto_assign_org=true/roleViewerは公式defaultと同じで、falseが新org作成を生む仕様を混同しない。reporting/update/plugin-update検査を無効・consoleINFO、全security/runtimeを証明するものではない。秘密/admin-password/secret-key/GF環境値を置かず、必要な管理者/鍵/所有等の正規供給が別に確立するまで配備/起動HOLD。全egress停止や既account不存在を設定textから保証しない。

DEBUG data sourceはPrometheus一つ、固定http://127.0.0.1:9090/proxy/org1/uidschubert-nk-prometheus/version1/readonly UI、既Prom dataのcandidate listenに整合。JSONdataはGET/15s、追加datasource/credential/scrape先/任意query無し。STANDARDはdatasources空だがprune=false/deleteDatasources空を維持し、既DB内の保持sourceを削除しない。空profileは既source自動削除/無効化/daemon停止の証拠でなく、STANDARD service停止は別gate。既存DBとdashboardsは一切触れない。

## 独立Test ID

|ID|操作と期待値|
|---|---|
|GRAFCFG001|INI全section/key/valueを独立literalへ厳密比較、DEFAULT inheritance/重複を許さない|
|GRAFCFG002|DEBUG全JSON構造/型・固定一source/url/proxy/readonly/default/version/GET15sを独立照合|
|GRAFCFG003|STANDARD空sourceとprunefalse/delete空、既データ削除を指示しない|
|GRAFCFG004|各INIkey欠落/値変異・余計なsection/key/Boolean偽装/重複/環境置換/秘密欄を拒否|
|GRAFCFG005|DEBUGurl/port/access/type/uid/org/version/editable型・追加source/credential等変異を拒否|
|GRAFCFG006|JSON null/empty/unknown/duplicate/nonfinite/末尾document・STDprunetrue/削除list/取り違え拒否|
|GRAFCFG007|既Prometheus listen候補9090/DEBUG15sと当独立固定値一致、旧試験実行0・双方実target成功推定0|
|GRAFCFG008|source/src差分は当4dataだけ、全regular/non-executable/Git/followup refs・README留保を確認|

期待値は1735/SS固定mode/loopbackとPG-D582の内部候補literal、production code/methodからexpectedを作らない。検証器はPython stdlibConfigParser/既strict JSON tool helperだけで、Grafana本体parserではない。command/環境・version/source/branch/開始終端/exit・全input/expected/actual/case/hash/変異数/BUGはPG8156と1736へ。Java/POM/既configは不変更、元4222/114/common44等の確認再演0。構成dataのJava四counterは非適用、0/0の100認定・既coverage転用0。新不具合は修正前915/916、失敗/skip/notrunを合格にしない。

actual binary/version/hash/install/native parser、管理者/鍵/permission、起動・実socket/egress、既DATA保存/総5GB、DEBUG表示・STANDARD停止、署名BOMの配布対象・全26metric/exposer・451/CHR/native/QA051/原190個別終了依存はUNRUN/HOLD。通常小区切りで停止しない。

## 公式一次資料（2026-10-24読取、製品version認定でない）

https://grafana.com/docs/grafana/latest/administration/provisioning/
https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/
https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/

provisioningのprune/deleteは実DB削除動作、INI http_addr空はwildcard、disable_initial_admin_creation=falseでは初回defaultADMIN生成、auto_assign_org=falseは新org生成という区別を根拠とする。最新docの項目確認を実binary挙動の試験へ転用しない。
