# 1739 Prometheus SDK分離依存 準備・検証計画

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI252/SS351、PG-D584、group1966/PG8168fresh18残82/reset1793382075。開始0.25/0.75/2pp/cap10、工具準備は元製造/PT/新受入に加算しない。元/v4/v5/工数N-Tnull維持。

## 現在地・非重複

1734後続索引PrometheusMeterRegistry=0、Production API/Web POMはcore1.17.1だけ、当toolchainにregistry/clientJar無し。1727/1738はSimple SDKから実Prometheus表現を推定しないと留保している。許可済みホストtoolchain導入として、公式public Maven Centralの固定座標だけを隔離準備する。registry/core versionは既1.17.1を変更しない。VM/Root/DB/既deployment・BOM・アプリ起動・実network collector/endpoint/権限/鍵等HOLDは解除しない。

## 固定供給元・依存閉集合

root=io.micrometer:micrometer-registry-prometheus:1.17.1。公式POMのcompile/runtime依存は既jspecify1.0.1/core1.17.1とio.prometheusのcore/tracer-common/exposition-formats1.7.0。直接POMの当compile/runtime依存をnamespace-aware XMLで追跡する。project.versionは宣言1.7.0へ限定、group/artifact/versionが未解決/未知scope又は座標なら停止し推測しない。

当確認済み新Jar閉集合10：
micrometer-registry-prometheus1.17.1、
prometheus-metrics-{core,tracer-common,exposition-formats,model,config,tracer-initializer,exposition-textformats,tracer-otel,tracer-otel-agent}1.7.0。
既再利用5Jarはcore/commons/observation1.17.1・HdrHistogram2.2.2・jspecify1.0.1。既M2とSDK原hash不変更、io.prometheus提供scopeのOpenTelemetryAPI・optional annotation・test依存はMavenの推移則上の非runtimeとして理由/座標を保持し、実行済/解決済/production依存へ偽装しない。残るmetadataの未解決があれば後続実行は保留する。

ダウンロード先は公式 https://repo.maven.apache.org/maven2/ の当固定座標URLだけ、認証/代替repo/credential無し。work/toolchain/prometheus-sdk-1.17.1-client-1.7.0-new-v1へnew-only、既source/M2座標の上書き/metadata更新0。POM/Jarと各repo SHA1を取得し一致、SHA256を独立計算して全byteをmanifestへpinする。SHA1はorigin整合補助で署名/強い認証の代用でなく、TLS供給元＋固定SHA256を再現基点にする。vendor署名検証済とは称さない。各JarはZIPとして読むだけで.class名/CRC健全/重複classpath/構造/sizeを照合、target class load/init/実行/SDK registry構築0、binary/POMはGit外、metadataだけ公開する。

## 工程と後続

PG8170は固定new-onlydownload/既5pin照合/POMdirectclosureと除外理由・Jar/hash/元version/source/全command/開始終端/終了の準備証跡を作る。工具pyflakes、closed coordinate/source/path/不一致拒否、全actualtarget操作0を記録する。ダウンロード/unknown中断時はbegin/process/terminalから回収し同slot再発行せず、別経路やrefusal探りをしない。新不具合は修正前915/916。1740に当結果と再現/環境を記載する。

依存準備後は、別群で既Web Gauge/Counterを当実SDKへ自己所有のin-memory registryで結合し、実textを独立SS literalで検証する通常PTを予定する。Production POM/コードへの導入・live管理HTTPへの接続は今回行わず、classifier/資源所有/実configを推測しない。Timerは1.17.1 PrometheusTimerがlong累積と専用collectorを持ち、Simple専用wrapperの安全性/公開値を流用できないため別の未受入課題として保持。まずGauge/Counterとunknown対0/label有限/owner/closeの安全に分離できる範囲を対象とする。

公式一次資料（2026-10-24）：
https://repo.maven.apache.org/maven2/io/micrometer/micrometer-registry-prometheus/1.17.1/micrometer-registry-prometheus-1.17.1.pom
https://raw.githubusercontent.com/micrometer-metrics/micrometer/v1.17.1/implementations/micrometer-registry-prometheus/src/main/java/io/micrometer/prometheusmetrics/PrometheusMeterRegistry.java
https://raw.githubusercontent.com/micrometer-metrics/micrometer/v1.17.1/implementations/micrometer-registry-prometheus/src/main/java/io/micrometer/prometheusmetrics/PrometheusTimer.java

Web readerはPOMを表示不能だったが、通常の同public URLのcurl読取は終了0で固定POM4422byteを取得済み。これはプラットフォームの安全拒否ではなく文書readerの取得不能であり、拒否されたPGPT処理/VM操作の別経路実行ではない。今後実際の拒否が出た場合はその操作を再試行しない。正式1964/53・原190新受入0/effortnull/QA051final/PTALT0と全actualHOLDを維持、通常小区切りで停止しない。
