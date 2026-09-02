# 開発環境・toolchain構築記録

## 1. 原則

Tool version、入手元、hash、設定、commandを固定し、secretを含めずに再現できる状態を保つ。OS packageを管理者権限で導入できない場合は`/home/mini/codex/project1/work/toolchain`へ展開し、repositoryへbinaryをcommitしない。

## 2. 開始時環境

| 項目 | 値 |
|---|---|
| 確認日時 | 2026-09-01 JST |
| OS | Ubuntu 26.04.1 LTS (`resolute`)、Linux `7.0.0-30-generic`、x86_64 |
| Locale/timezone | shell default `en`、工程固定値 `ja-JP` / `Asia/Tokyo` / UTF-8 |
| Git | 2.53.0 |
| 開始時Java/Maven | 未導入 |
| 開始時DB/broker | PostgreSQL/Artemis未導入 |
| Repository | `main` / `749a777` / clean、origin未設定 |
| Remote | 指定HTTPS URLをoriginへ追加。private repository認証がなくfetch/push/PRは未実行 |

## 3. 導入済みtool

| Tool | Version | 入手元 | 配置・設定 | 検証 |
|---|---|---|---|---|
| OpenJDK | Ubuntu OpenJDK `25.0.4+7-1~26.04` | Ubuntu 26.04 `resolute-updates/main`の`openjdk-25-jre-headless`・`openjdk-25-jdk-headless` deb | 元展開は`work/toolchain/java`。Debの絶対`/etc` symlinkを同deb内設定へ置換し、OS trust anchorからJava cacertsを生成したself-contained copyを`work/toolchain/jdk-25.0.4`へ配置 | `java -version`、`javac -version`、Maven起動 |
| Maven Wrapper | wrapper 3.3.4 / Apache Maven 3.9.12 | `repo.maven.apache.org`のversion固定distribution | `MAVEN_USER_HOME=work/toolchain/m2` | `./mvnw -version` |
| JUnit Jupiter | 5.13.4 | Maven Central `org.junit.jupiter:junit-jupiter` | Protocol POMでversion固定 | Protocol 67 PT PASS、skip 0 |
| JSpecify | 1.0.0 | Maven Central `org.jspecify:jspecify` | Protocol production packageを`@NullMarked`、必要境界を`@Nullable` | Compile、null negative PT |
| JaCoCo | 0.8.15 | Maven Central `org.jacoco:jacoco-maven-plugin` | Protocol `verify`で4指標100%をPOM gate化 | line 3357/3357、method 730/730、class 156/156、branch 976/976 |
| SpotBugs Maven Plugin | 4.10.4.0 | Maven Central `com.github.spotbugs:spotbugs-maven-plugin` | Protocol `verify`、Max/Low、error時FAIL、XML出力 | BUG-002検出・修正後bug/error 0 |
| PostgreSQL | 18.6 (`18.6-0ubuntu0.26.04.1`) | Ubuntu 26.04 `resolute-updates/main`の`postgresql-18`、`postgresql-client-18`、`libpq5` deb | `work/characterization-tools/root/usr`へrootless展開。Testごとに`target`下へ`initdb`し、loopbackの自動選択portと合成fixtureだけを使用 | Flyway V001～V005、21 table、role/grant/constraint/functionのPT 15件PASS |
| Flyway | 13.4.0 | Maven Central `org.flywaydb:flyway-core` / `flyway-database-postgresql` | API PT scopeにversion固定。`schubert_meta.flyway_schema_history`、`initSql=SET ROLE nk_owner`、validate on、out-of-order/baseline off、clean disabled | 初回5 migration、再実行0、checksum drift拒否、並行実行直列化 |
| PostgreSQL JDBC | 42.7.13 | Maven Central `org.postgresql:postgresql` | API PT scopeにversion固定、PostgreSQL 18へのJDBC検査に使用 | catalog/SQLSTATE/role権限PT PASS |
| Apache Artemis | 2.56.0 | Apache Artemis公式配布とMaven Central `org.apache.artemis` | Binaryは`work/toolchain/artemis`へ展開。API POMでJakarta clientをproduction、server/Jakarta serverをPT scopeに固定 | Java 25で`artemis version`、archive SHA-512照合、HMAC/Outbox中間gate 26 PT PASS |
| Python | 3.14.4 | OS既存 | SS 323 named recordのversion管理済み再現生成scriptと検証補助に限定。通常のsource編集には使用しない | `python3 --version`、69 record/64 mappingの再生成hash一致 |
| jq | OS既存 | Ubuntu package | PATH | 最終gateでversion記録 |
| unzip/sha256sum | OS既存 | Ubuntu package/coreutils | PATH | command存在確認済み |

DownloadしたdebとMaven cacheは作業領域だけに保持する。Evidence manifestへpackage versionとbinary SHA-256を記録し、Gitにはdownload binaryを含めない。

## 4. 実行環境変数

```sh
export SCHUBERT_JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export JAVA_HOME="$SCHUBERT_JAVA_HOME"
export MAVEN_USER_HOME=/home/mini/codex/project1/work/toolchain/m2
export PATH="$JAVA_HOME/bin:$PATH"
export LANG=ja_JP.UTF-8
export TZ=Asia/Tokyo
```

Secret、DB password、JMS credentialはこのblockやrepository内env fileへ追加しない。

## 5. 再現手順

1. Ubuntu package metadataで`openjdk-25-jdk-headless=25.0.4+7-1~26.04`とJREを確認する。
2. `work/toolchain/packages`で`apt-get download openjdk-25-jdk-headless openjdk-25-jre-headless`を実行する。
3. 各debを`dpkg-deb -x`で`work/toolchain/java`へ展開する。
4. 上記環境変数を設定し、`java -version`と`javac -version`が25.0.4を示すことを確認する。
5. Deb内JDKを`work/toolchain/jdk-25.0.4`へ複製し、`/etc/java-25-openjdk`への絶対symlinkを元展開の`etc/java-25-openjdk`実体へ置換する。
6. `trust extract --format=java-cacerts --filter=ca-anchors`でOS trust anchorを作業領域の`lib/security/cacerts`へ生成する。
7. Repository rootで`./mvnw -version`を実行し、Maven 3.9.12とJava 25.0.4を確認する。
8. Maven commandへ`-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository`を指定し、`./mvnw --no-transfer-progress clean verify`でdependency/pluginをpinされたPOMから取得する。

### 5.1 PostgreSQL/Flyway PTの再現

1. Ubuntu package metadataで`postgresql-18=18.6-0ubuntu0.26.04.1`、`postgresql-client-18`、`libpq5`を固定し、
   `apt-get download`後に`dpkg-deb -x`で`work/characterization-tools/root`へ展開する。
2. Deb SHA-256は順に`0536716204dee9152dee758c252936ba41c93b7330395f8abb0c5b86558aa658`、
   `c46d1ace8f7d84a9648c63b566fff799b7ee3281db46ef6e7b99baf0fd7bd2e4`、
   `7e9199f54290b04a28e9f136207624ca30b0988d613159977fd84e8b4467e0a4`と照合する。
3. Test launcherは`LD_LIBRARY_PATH=<root>/usr/lib/x86_64-linux-gnu:<root>/usr/lib/postgresql/18/lib`、
   `initdb -L <root>/usr/share/postgresql/18`、PostgreSQL起動時の`extension_control_path`と
   `dynamic_library_path`を同rootに固定する。Clusterはmodule `target`下、Unix socketはpath長制約を避けて`/tmp`、TCPはloopback限定とする。
4. POM固定JARのSHA-256はFlyway core
   `e6147827cb883a8bb359231202e8d0d32e0f8e905caf0e20d2890e36dcd12251`、PostgreSQL database plugin
   `1219a89b93fe5dc74ddec8271d810136751820d5bc2a880e51f6ff21e02d66ac`、pgJDBC
   `6e0e4cc2d8cae902084f8a2b18728b073a6fd9d1f87c9d8bff8f298c18185b93`とする。
5. Repository rootでAPI moduleと依存moduleに対する`clean verify`を実行する。Test用`trust`認証は
   loopbackの破棄可能clusterと合成fixtureに限定し、production設定雛形へは転用しない。

### 5.2 Artemis/JMS PTの再現

1. `https://downloads.apache.org/artemis/artemis/2.56.0/apache-artemis-2.56.0-bin.tar.gz`と公式`.sha512`を取得し、
   SHA-512 `441ad38aa1b0526e5709edf43542039f016669d24134056613e4cbafdf6b101e5351f79f7ee190b43fc8031f6ec596a5fd075490dcee4d3eb3a88d8ed2cfc01b`
   を照合する（SHA-256 `df469079b6388c8c6276197388a0f5ee0d64d0ca42d7f0e2ca5e392e21b955de`）。
2. `work/toolchain/artemis/apache-artemis-2.56.0`へ展開し、JDK 25.0.4の`JAVA_HOME`/`PATH`で`bin/artemis version`を実行する。
3. Maven artifact SHA-256は`artemis-jakarta-client`
   `89eb1f27e583119db4c1c23db26cbc1916c82bfc5fcc23dbcb7ef040602f09d6`、`artemis-server`
   `4bc0bb2d74e340fbb54d84121f2c52708e00bdad0a84751b9bd4f4b21e03c358`、`artemis-jakarta-server`
   `27353ffe275980135c63b81e5497403a29cf843fd2e484536ac521b4ad03cb3e`と照合する。
4. Broker component PTはmodule `target` 下の隔離File Journal、loopback自動選択port、合成credential/dataだけを使い、
   production credentialとCurrent dataを読まない。

## 6. 導入予定・工程内service

| 対象 | 方針 | 状態 |
|---|---|---|
| PostgreSQL | 18.6をrootless展開し、実PostgreSQL test runtimeでDDL/Flyway・role/grantのPTを実施 | 完了 |
| Artemis | POM固定2.56.0のFile Journal brokerとproduction `broker.xml` schema/config検査を併用 | 導入済み・component PT実装中 |
| JDBC/Flyway | Flyway 13.4.0、PostgreSQL JDBC 42.7.13をMaven Central artifactで固定 | 完了 |
| 静的解析/coverage | ProtocolはCompiler `-Xlint:all -Werror`、JSpecify、SpotBugs Max/Low、JaCoCo 4指標100%を導入済み。NullAway相当のcompile-time null dataflow、PMD/Checkstyle/Spotlessとparent継承は後続module追加前にgate化する | 一部完了 |
| Secret scan | Tracked/untracked対象のpattern・entropy・known secret detectorをsanitized report化 | 未着手 |

## 7. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | 開始時環境を確認し、rootless OpenJDK 25.0.4とMaven 3.9.12を構築。 |
| 2026-09-01 | Ubuntu debの絶対設定symlinkをrootless用にrelocateし、OS trust anchorからcacertsを生成。Maven local repositoryをwork領域へ固定。 |
| 2026-09-02 | Protocol用JUnit 5.13.4、JSpecify 1.0.0、JaCoCo 0.8.15、SpotBugs Maven Plugin 4.10.4.0をMaven Centralから導入し、version・設定・再現commandを固定。 |
| 2026-09-02 | SS 323 named record生成scriptを固定し、69 record・64 mappingの再生成がbyte単位で同一になることを確認。 |
| 2026-09-02 | Semantic型追加後のProtocol 52 PT、production 125 class、coverage 4指標100%、SpotBugs 0を同一toolchainで再確認。 |
| 2026-09-02 | ID/enum/X numeric/range型追加後のProtocol 56 PT、production 155 class、coverage 4指標100%、SpotBugs 0をrun 06で再確認。 |
| 2026-09-02 | Layout semantic/golden追加後のProtocol 67 PT、production 156 class、coverage 4指標100%、SpotBugs 0をRun 08で再確認。専用Maven local repository指定を省いたRun 07はoffline依存解決前に失敗し、PASSへ算入しない。 |
| 2026-09-03 | Ubuntu公式PostgreSQL 18.6をrootless展開し、Flyway 13.4.0、PostgreSQL JDBC 42.7.13と隔離clusterによるNK-DAT-001 PTを導入。 |
| 2026-09-03 | Apache Artemis公式2.56.0のarchive/hashとMaven client/server artifactを固定し、Java 25の実File Journal component PT用toolchainを導入。 |
