# 1737 Prometheus公式構文parser ホスト単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON010～013/UI252253/SS351、1730/1731/PG-D583。group1964/P01809_OFFLINE_PROMTOOL_SYNTAX_V1、PG8160fresh18残82/reset1793382075、開始0.5/1.5/4pp/cap10。scope・モデル・451条件・元/v4/v5/実N-Tnull不変更。

## 選定・許可・境界

1734の後続索引promtoolは1730/1731だけ、既公式parser成功なし。現在toolchainにpromtool無し。元利用者のPG/PT tool導入許可の範囲で公式検査工具を新規専用host directoryへ取得し、公開dataの構文だけを初回検証する。これは未実施parser工程であり、拒否PTの別経路再試行やactualVM/Root/DB/backend/HOLD解除ではない。

公式prometheus.io/downloadで2026-10-21LTS3.13.5/linux-amd64 archiveとSHA2560388822ace519c5a3a8ef556a541ce1b536e21d872f82deded465bd27a5a0699を確認。公式GitHubprometheus/prometheus v3.13.5公開releaseだけから取得、既37GiB空き/hostLinuxx86_64。work/toolchain/promtool-3.13.5-linux-amd64はnew-only、存在時は再発行/上書きせず照合へ。archiveからpromtool/LICENSE/NOTICEのregular3memberだけを新規fileへ抽出し、Prometheus daemonは抽出/起動しない。archiveとbinary/hash/version/入手元/command/成功失敗/開始終端をPG8162へ。binary/archiveはGitへ入れずmetadataだけ保存。TLS＋公式掲載SHA照合であり独立vendor署名の検証済とは称さない。

tag3.13.5のcmd/promtool/main.goと公式CLI資料から、check config --syntax-onlyの経路はLoadFileと宣言validation、rule/参照file実検証の一部を省き、service-discovery/query/health/debug/push/TSDB起動を呼ばないことを点検。入力も既固定二管理targetと空STDだけでcredential/SD/remote/rule参照を持たない。元profileを自己所有new job directoryへbyteコピーし、清潔な最小envと有限timeoutで当toolだけを実行する。profile内endpointは解決/接続せず、その他のpromtool commandやPrometheus serverを起動しない。公開tool入手のHTTPSと業務/VM/DB通信を区別して記録する。

## 独立Test ID

|ID|入力・command/期待値と算出根拠|
|---|---|
|PROMTOOL001|公式archive SHA/選択regular member/binaryhash/version3.13.5の元実receiptを照合、再download/再version実行0|
|PROMTOOL002|当debug.yml.templateを同byteコピー、promtool check config --syntax-only <ownedcopy>、期待exit0（公式schemaの二固定static target）|
|PROMTOOL003|当standard.yml.templateコピー、同command exit0（合法empty scrape_configs）|
|PROMTOOL004|独立負例JSONに未知root fieldを追加、同command exit1（LoadFile strict schema）。正式templateを変更しない|
|PROMTOOL005|独立15s intervalに16s timeout、同command exit1（timeout<=intervalの公式契約）|
|PROMTOOL006|独立二jobの同job_name、同command exit1（unique job契約）|

002～006は当new ownedfixtureで一回ずつ、全commandに有限30s、shellなし/close_fds/stdinDEVNULL。元template/Java/POM/BOM/Root等は不変更、原4222/114/common44やPythonsemantic8件の確認目的再演0。expected exit1の正規negativeを失敗PTへ数えず、実exit相違・timeout/unknownを成功へ読替えない。tool導入失敗時は構文PT未実行として保全し、新たなアクセス経路/認証回避を試さない。

原begin/process/終了/OS/Python/tool/binary/input/独立期待とactual/各ID・stdout-stderr（固定公開fixtureだけ）・hash/BUGはPG8162/8164と1738へ。新障害は修正前915/916。config dataにJava命令/class/branchはなく四counter非適用で、元coverageを加算/除外しない。検査器5processを実scrapeやruntime受入に数えない。

実Prometheus/Grafana起動・DB/VM/Root/native資格/鍵/アカウント/サービス/配置/BOM・rule/secret参照fileの検証・exporter互換/全metric/DEBUG実運転/STD停止/総容量・451/CHR/正式はUNRUN-HOLD維持。1731のparser未実行だけを当限定証跡で更新し、全actualHOLD解除・試験代替PASSはしない。

## 公式一次資料（2026-10-24）

https://prometheus.io/download/
https://prometheus.io/docs/prometheus/latest/command-line/promtool/
https://raw.githubusercontent.com/prometheus/prometheus/v3.13.5/cmd/promtool/main.go
https://github.com/prometheus/prometheus/releases/download/v3.13.5/prometheus-3.13.5.linux-amd64.tar.gz

latest docと固定tag/versionの役割を分け、入手確認だけでPT合格/正式更新をしない。通常報告/commit/PMO待ちで停止しない。
