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
| JUnit Jupiter | 5.13.4 | Maven Central `org.junit.jupiter:junit-jupiter` | Protocol POMでversion固定 | 52 PT PASS、skip 0 |
| JSpecify | 1.0.0 | Maven Central `org.jspecify:jspecify` | Protocol production packageを`@NullMarked`、必要境界を`@Nullable` | Compile、null negative PT |
| JaCoCo | 0.8.15 | Maven Central `org.jacoco:jacoco-maven-plugin` | Protocol `verify`で4指標100%をPOM gate化 | line 2666/2666、method 580/580、class 125/125、branch 707/707 |
| SpotBugs Maven Plugin | 4.10.4.0 | Maven Central `com.github.spotbugs:spotbugs-maven-plugin` | Protocol `verify`、Max/Low、error時FAIL、XML出力 | BUG-002検出・修正後bug/error 0 |
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

## 6. 導入予定・工程内service

| 対象 | 方針 | 状態 |
|---|---|---|
| PostgreSQL | 18。Rootless展開または実PostgreSQL test runtimeを用い、DDL/Flyway・role/grantのPTを実施 | 未着手 |
| Artemis | POM固定versionのembedded brokerとproduction `broker.xml` schema検査を併用 | 未着手 |
| JDBC/Flyway | Maven Centralのversion固定artifact | 未着手 |
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
