# 1572 Micrometer正規依存のlocal準備記録

2026-10-23/group1828、P018-09/C07共有費0、着手0.25/0.75/2pp・上限10pp。PG7104-micrometer-dependency-prepare-v1/manifest.json SHA `bd4e07eae2bd8234f085fecea37cdd09864fcb55efd4e4bd3cb716380d5d3613`、真正Maven install-file終了0、全五check true、PT実行0。これは工具準備であり製造/実metric/受入へ加算しない。

Micrometer core1.17.1 SHA `9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56` は421§5.8の既導入Web test版と一致し不変更。Coreの正規runtime依存HdrHistogram2.2.2がlocal M2に未導入だったため、既Apache Artemis2.56.0配布 `toolchain/artemis/apache-artemis-2.56.0/lib/HdrHistogram-2.2.2.jar` を再使用。Jar SHA `22d1d4316c4ec13a68b559e98c8256d69071593731da96136640f864fa14fad8`、embedded Maven properties/POM・Bundle-Version=2.2.2、group/artifact/version一致を検査した。元Artemis配布は421§5.2で公式archive SHA512照合済みの履歴があるが、現archiveは残存せず、今回その全archive検証を再実行したと称しない。現在のinstalled Jar/metadata/hashと既記録の由来を区別して保存した。

元Jarと元embedded POMを変更せず、Maven3.9.12/JDK25.0.4・既cache済maven-install-plugin3.1.2を `-o --no-transfer-progress -N` で使用、`install-file -Dfile=<上記Jar> -DpomFile=<元Jarから抽出したPOM> -DgeneratePom=false`、repoは既 `toolchain/m2/repository`。正規 `org/hdrhistogram/HdrHistogram/2.2.2` 座標が存在しないことを先行確認し、新規cacheだけを作成した。Jar/POMの全byte一致、元Jar/core不変更・既非metadata object不変更を終端後確認。依存除外/代替POM/外部download/版変更/既artifact上書き0。

公開pathは `evidence/provisional/PG7104-micrometer-dependency-prepare-v1/manifest.json`、原begin/process/終了/Maven logと抽出POMは `work/pgpt-runs/PG379/pg7104-micrometer-dependency-prepare-v1`。実entrypoint/library/helper/loaded公開sourceを採取・終了時一致。元source/distro/private/DB/鍵/stash/VM等は変更せず、cacheのJar/POM binaryはGitへ格納しない。新環境での再現は421§5.2の公式Artemis導入後に元recordとJar hashを照合し、未導入座標へ上記一回用工具を新保存先で使用する。現環境で同一slotを再発行せず元manifestを参照する。

次は当既管理版coreをWeb compileへ正規に追加し、borrowed MeterRegistryへの二HTTP metric/SLO登録・STANDARD無効/故障伝播/有限labelを自己所有in-memory通常PTで検証する。Micrometer以外のbackendへ置換せず、Prometheus公開名/実exporter/既HTTP terminal接続/Root assemblyと実DB原PTは別の未受入・HOLD条件として維持する。
