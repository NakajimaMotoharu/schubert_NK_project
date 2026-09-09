# 開発環境・toolchain構築記録

## 1. 原則

Tool version、入手元、hash、設定、commandを固定し、secretを含めずに再現できる状態を保つ。OS packageを管理者権限で導入できない場合は`/home/mini/codex/project1/work/toolchain`へ展開し、repositoryへbinaryをcommitしない。

## 2. 開始時環境

SSC-020/PT-SCN-20260908-10のgroup fixture: `id`で本機のmini(primary mini)がusers supplementary groupに所属することを確認。API module targetのJUnit一時directoryと合成record fileだけをusers groupへ変更し、新規childのchgrp/0750/0640と既存不一致拒否を試験した。実service account、所属group、credential、mount設定の変更は行っていない。Serverではschubert-api専用primary group＋schubert-web supplementaryを342/343どおりprovisionし、private file0600とroot権限をITで実UID検証する。別PT実行accountでは同等の非primary所属group fixtureが必要。

PG-D-058/PT-SCN-20260908-08のFS条件: 本機`df -T /tmp /home/mini/codex/project1/work`では/tmp=tmpfs、project/work=ext4。TransferRootInspectionの初期対応FSはext4のみ。正常系の実root fixtureはJUnit 5.13.4 TempDirFactoryでAPI module `target`内へ一意の一時directoryを絶対pathで作成し、JUnitが試験後に回収する。tmpfs/未知FSを正常系として受理する設定変更は行わない。Serverも起動前にfilesystem typeとnative no-replace/fsync適合を確認する。追加tool導入・OS mount変更なし。

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
| PostgreSQL JDBC | 42.7.13 | Maven Central `org.postgresql:postgresql` | PG-D-142でAPI runtime scopeへ移行（PTでも同一artifact）、専用InspectorのDriverManager接続に使用。版更新/再導入なし | 従来catalog/SQLSTATE/role権限PT PASS、新SCRAM/接続PTは048で別判定 |
| Apache Artemis | 2.56.0 | Apache Artemis公式配布とMaven Central `org.apache.artemis` | Binaryは`work/toolchain/artemis`へ展開。API/Web POMでJakarta clientをproduction、APIのserver/Jakarta serverをPT scopeに固定 | Java 25で`artemis version`、archive SHA-512照合、実NIO File Journalの再起動・duplicate・1/5/25秒再配送・transaction・DLQ component PT PASS |
| Python | 3.14.4 | OS既存 | SS 323 named recordのversion管理済み再現生成scriptと検証補助に限定。通常のsource編集には使用しない | `python3 --version`、69 record/64 mappingの再生成hash一致 |
| jq | OS既存 | Ubuntu package | PATH | 最終gateでversion記録 |
| unzip/sha256sum | OS既存 | Ubuntu package/coreutils | PATH | command存在確認済み |

PG-D-142/JDBC runtime再現: `org.postgresql:postgresql:42.7.13` jar SHA-256 `6e0e4cc2d8cae902084f8a2b18728b073a6fd9d1f87c9d8bff8f298c18185b93`、既存Maven Central取得済みm2をoffline利用。JDK25.0.4+7/Maven3.9.12は不変更。`src/schubert-nk-api/pom.xml`のruntime依存を含めたrelease classpathが必要で、jar単体をdriver同梱と誤記しない。PT207はJUnit TempDirの隔離PGだけへ合成SCRAM password/専用role限定hbaを設定し、daemon/実DB/実credentialを変更しない。起動・試験・証跡の正式再現commandは048へ記録する。

DownloadしたdebとMaven cacheは作業領域だけに保持する。Evidence manifestへpackage versionとbinary SHA-256を記録し、Gitにはdownload binaryを含めない。

### 3.1 Null dataflow解析（2026-09-07）

NullAway 0.14.1（SHA-256 `a74a5fb5a047537a4bdc362f9c1821279d7122d9d36aa2e6a72b79832fab7e4d`）とError Prone core 2.50.0（`40a88d3ea732fac3a57ae0e2b27f1729ce76cc41857bcd63d5845e79eae5f72e`）をMaven Centralから取得し、parent POMのannotationProcessorPathsへversion固定した。Production runtime依存へは追加しない。

[Error Prone公式Maven導入手順](https://errorprone.info/docs/installation)、[NullAway設定](https://github.com/uber/NullAway/wiki/Configuration)に従い、forked javac、必要なcompiler module exports/opens、JSpecifyModeとJSpecifyJDKModelsを設定する。JDKモデルは0.14系の実験的機能であるため、単に有効化するだけでなく、453の独立canaryでnullableなcollection要素・引数・戻り値・dereferenceを検出できることを検証する。新moduleにも同じ親設定を継承する。

初回はonlineの`./mvnw --no-transfer-progress compile`で固定依存を取得し、以後`-o`で再現する。Maven cache/JAVA_HOMEは以下と同じ。canaryは`JAVA_HOME=... python3 tools/quality/001_verify_null_contracts.py --maven-repository <cache>/repository --output <sanitized-evidence-directory>`で実行する。NullAwayの指摘を抑止・対象除外で回避しない。

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

### 5.1 API REQUEST Details JSON parser（2026-09-07）

- Maven Centralの`com.google.code.gson:gson:2.14.0`をAPI production dependencyとして明示固定する。既存Flyway依存で取得済みの同versionを利用し、別parserやnative libraryは追加しない。
- 入手元: `https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar`。JAR SHA-256: `2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f`。
- `JsonReader`を`Strictness.STRICT`/nesting limit 2で使い、重複keyと型・値のallowlistはAPIで別途検査する。反射による任意class deserializeを行わない。SS351 §3.3/SSC-008、PT-IDEM-012を参照。
- 再現: 上記固定JDK/Maven/local repositoryでroot `./mvnw --no-transfer-progress clean verify`（初回取得後は`-o`）。`RequestLogDetailsTest`がstrict JSON/重複/型/byte上限を確認する。

### 5.2 Build契約・固定整形・生成再現（2026-09-07）

全artifactはMaven Central `https://repo.maven.apache.org/maven2/`から取得する。version rangeでの取得を行わない。

| Artifact / repository内path | version | JAR SHA-256 |
|---|---|---|
| org/apache/maven/plugins/maven-enforcer-plugin | 3.6.3 | `32347686c513894a2fae96eeb11527883f47b8957850d793ea833646ad954dca` |
| com/diffplug/spotless/spotless-maven-plugin | 3.10.2 | `5a8264cb01785dc2fb55cef96e31bc9f98a300a27e237b2d86c4c9fc6d770ea6` |
| com/google/googlejavaformat/google-java-format（all-deps classifier） | 1.36.1 | `25b400f003089d23cc5320cdaf1a16cabee19b8aa3434d0ff021b3d9f42154b4` |
| org/slf4j/slf4j-api | 2.0.18 | `44508fd1576500688c790b190acdd16fec4f8c79a3e0b900afd70503cf055f55` |

親POMのvalidateでEnforcer（JDK25、Maven3.9.12以上4未満、dependencyConvergence）とSpotless checkを必須化。整形は`./mvnw spotless:apply`、確認は`./mvnw clean verify`。通常と同じJAVA_HOME/Maven local repositoryを指定する。再生成は次の隔離検査を使用し、productionやgoldenを上書きしない。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 python3 tools/quality/002_verify_generation.py \
  --formatter /home/mini/codex/project1/work/toolchain/google-java-format-1.36.1-all-deps.jar \
  --work-dir /home/mini/codex/project1/work \
  --output /home/mini/codex/project1/work/generation-results.json
```

比較器は70 fileの一致に加え、隔離catalogに1行の差を与えた場合の拒否を確認する。再生成一致は機能期待値の証明と混同せず、固定長golden・semantic negative PTを併用する（BUG-017～019、YKT-014～016、PG-D-030/031）。

### 5.3 API password encoding（2026-09-07）

- Spring Security crypto 7.1.1をAPIだけへcompile dependency追加。Maven Central metadataの2026-08-20更新における最新正式版（7.2.0-M1は採用しない）。
- 入手元: `https://repo.maven.apache.org/maven2/org/springframework/security/spring-security-crypto/7.1.1/spring-security-crypto-7.1.1.jar`。SHA-256 `6e8bb2337faccabd30626f917ed1d2bfa9dde982229b6b373b644d1a01635403`。
- 公式実装確認: [Pbkdf2PasswordEncoder 7.1.1](https://github.com/spring-projects/spring-security/blob/7.1.1/crypto/src/main/java/org/springframework/security/crypto/password/Pbkdf2PasswordEncoder.java)、[DelegatingPasswordEncoder API](https://docs.spring.io/spring-security/reference/api/java/org/springframework/security/crypto/password/DelegatingPasswordEncoder.html)。SS314のPBKDF2-HMAC-SHA256/310000/16byte salt/256bit、hex、additional secret空を固定する。
- 再現は既定JDK/Mavenのroot clean verify。初回依存解決はoffline指定を外す。Production CPU上p95は後続Linux IT/ST測定として残し、このPCの速度を理由にID/parameterを変更しない。
- `-Xlint:all -Werror`はcrypto単体jarの`org.springframework.lang.Contract`欠落を検出した。Spring Security7.1.1の[公式version catalog](https://github.com/spring-projects/spring-security/blob/7.1.1/gradle/libs.versions.toml)と同じSpring core7.0.9を明示依存として追加し、warning抑止はしない。`https://repo.maven.apache.org/maven2/org/springframework/spring-core/7.0.9/spring-core-7.0.9.jar`、SHA-256 `5195f4722699b39878d99a832549fe65df2890b159d063b88fff31b1ca65ae36`。Mavenのfork診断が省略されたため`-X`で生成されたtarget/javac.shを同一引数で実行して原因を特定した。初回失敗は合格に算入しない。

### 5.4 API native filesystem port（SSC-019、2026-09-08）

既存JDK25.0.4の公開FFMと本機Linux libcを使用し、新規JNI library/JDK internal APIは導入しない。API Surefireは既存JaCoCo argLineを保持して`--enable-native-access=ALL-UNNAMED`を追加する。API実起動にも同flagが必要（SS342）。初回compileはjavacのrestricted-call注意を-Werrorで検出し、失敗を合格へ数えない。仕様上必要なLinker.downcallHandleの一箇所だけ、PG-D-055/SSC-019・担当NK-SCN-001 PG・PG gate/JDK/ABI更新ごとの再審査を隣接記録した`@SuppressWarnings("restricted")`で明示承認する。Package/file全体の抑止やcoverage除外はない。

libc symbol署名とABIは固定し、openatのvariadic境界とerrno captureを明示する。本機PTはLinux amd64で実施し、Linux aarch64は同定数の対象ABIだが実行適合は配備機のreadiness/ITで要確認。OS/CPU/symbol不一致は停止し、非atomic・上書きrenameへfallbackしない。再現は既定root clean verify、合成fixture以外を操作しない。

### 5.5 Web framework選定調査（2026-09-08、導入前）

[Spring Boot公式system requirements](https://docs.spring.io/spring-boot/system-requirements.html)で正式4.1.1のJava17～26/Maven3.6.3以上を確認し、本機Java25/Maven3.9.12は範囲内。[公式Maven Central BOM](https://repo.maven.apache.org/maven2/org/springframework/boot/spring-boot-dependencies/4.1.1/spring-boot-dependencies-4.1.1.pom)をwget標準出力で確認し、Framework7.0.9/Security7.1.1/Session4.1.1/Thymeleaf3.1.5.RELEASE/Tomcat11.0.24。既存APIのFramework/Security固定versionと一致する。まだWeb framework dependency導入・起動確認済みとはしない。BOM導入時は既存JUnit/Artemis/Netty等のversionを無意識に変更しない。

[Spring Session公式API説明](https://docs.spring.io/spring-session/reference/api.html)のcustom SessionRepository＋SessionRepositoryFilter/HttpSession接続を参考にし、標準Jdbc repository/Java serializationは採用しない。公式ページからの4.1.1 Javadoc linkは404のため、必要なsignatureはMaven release source jarで確認する方針。本機curlコマンド未導入だがwgetが利用でき、調査継続可能。環境blocker/高推論再走対象ではない。

Session属性JSONにはAPI側で既に固定導入済みのGson2.14.0をWebへcompile依存追加。入手元はMaven Central `com/google/code/gson/gson/2.14.0/gson-2.14.0.jar`、SHA256 `2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f`。既存local cacheを使用し、他依存versionは変更しない。2026-09-08 19:32:03、完全修飾`org.apache.maven.plugins:maven-dependency-plugin:3.9.0:tree -Dincludes=com.google.code.gson:gson`のoffline Web reactor出力でcompile2.14.0を確認。command/log hashは015/evidence/logs/attributes-exploration.md。streaming Strictness.STRICT/型・重複key・nesting/byte境界を独立7PT、初回8PTはJDKのみ。Spring framework配線完了と混同しない。

### 5.6 Spring Session API実体確認（2026-09-08、dependency追加前）

Maven Centralの`org/springframework/session/spring-session-core/4.1.1/spring-session-core-4.1.1-sources.jar`をwgetで`/tmp/schubert-spring-session-core-4.1.1-sources.jar`へ取得、SHA256 `d75a8e9c32c2357255971a4cd9330f463e0e5e2ac26e7024bd4a7785606f0bad`。`unzip -p`でSession/SessionRepository/SessionRepositoryFilterを読み、Javadoc404を回避した。これは調査sourceで、Web runtime dependency追加/起動済みとはしない。

SessionRepositoryはcreate/save/findById(nullable)/deleteById、saveはvoid。SessionはchangeSessionId、nullable属性read、null値setでremove、creation/last access/max idle/isExpiredを持つ。Filterはrequest読取時にInstant.nowでlast accessを設定し、response commit前にrepository.saveを呼ぶ。従ってadapterではDB microsecond精度への明示変換と、削除済rowのstale saveを新規insertへ化けさせない制御が必要。Libraryの任意Object属性をそのままserializationせず、SS314の閉schemaへ明示projectionする。実装・接続PTは後続。

### 5.7 Spring Session/Servlet接続用の固定依存（2026-09-08）

Web moduleへ以下を導入。取得元はMaven Centralの`https://repo.maven.apache.org/maven2/`＋表artifact path＋version/artifact-version.jar。公開[Spring Session API](https://docs.spring.io/spring-session/reference/api.html)と5.6のrelease sourceに基づき、標準SessionRepositoryFilterをcustom encrypted repositoryへ接続する。Boot server/Security chain全体の起動完了ではない。

| artifact path | version/scope | JAR SHA256 |
|---|---|---|
| org/springframework/session/spring-session-core | 4.1.1 compile | 01b836bfcc5b64f7039c3430980878112a10db5066eda4274a1d3eb874e49733 |
| org/springframework/spring-web | 7.0.9 compile | 941ced476427bde2533872f293da535fd0258de3f3a650a7f1bfe01ed2927302 |
| jakarta/servlet/jakarta.servlet-api | 6.1.0 compile | 8a31f465f3593bf2351531a5c952014eb839da96a605b5825b93dd54714c48c4 |
| org/springframework/spring-test | 7.0.9 test | 6ce8fc116f5d309b9ac50a6738bd1b15ea4012a4a5563c0ee89b795bfc9af0dc |
| commons-logging/commons-logging | 1.4.0 Web runtimeへ収束 | d175dbd751dd782a63bde28c7a039520e971f25e84b79c19b8435edc3603e0dc |
| org/jspecify/jspecify | 1.0.1 Web runtimeへ収束 | 070d75f261fe4c5b8202508366715f7f2d4660f88c8ef7e6d3575e48c9683b66 |

初回compileはEnforcer dependency convergenceがcommons-logging1.4.0/1.3.5、JSpecify1.0.1/1.0.0の混在を拒否。WebだけのdependencyManagementへ上位patchを明示固定し、ruleを無効化しない。Protocol/Storage/APIの既存宣言は不変更、Web実行classpathでは同artifactの一意versionへ収束する。JSpecify4 annotationのjavap公開signatureは1.0.0と1.0.1で差分0（2026-09-08確認）、NullAway/compileを再実施。JUnit5.13.4/Artemis2.56.0/Netty4.1.137.Finalは維持。Spring beans/core7.0.9、observation/commons1.16.7はspring-webの推移依存、既存broker test側micrometer-core1.17.0はtest scopeのまま。全BOMによる一括上書きはしない。

導入再現は既存JAVA_HOME/local repository指定でWeb reactorのonline compileを一回実行し、以後`-o`。`org.apache.maven.plugins:maven-dependency-plugin:3.9.0:tree`をWeb reactorへoffline実行、2026-09-08 21:19:35 JST exit0、`/tmp/PT-WEB-spring-dependencies-01.log` SHA256 `063eed991f99cae20506b510358c0e6024dfe6d71a49980f3fde4636783bfafa`。依存source/binary/license metadataは配布元artifactで確認可能、Gitへvendor copyはしない。探索初回失敗は合格へ算入せず、015 spring-session-exploration.mdへ記録する。

### 5.8 Spring Security CSRF接続（2026-09-08）

Webへspring-security-web7.1.1をcompile追加。API既存crypto7.1.1/Framework7.0.9と同じ系列。取得元はMaven Central `https://repo.maven.apache.org/maven2/`＋artifact path/version/artifact-version.jar。CsrfFilter/Repository/RequestHandlerとCsrfConfigurerのrelease sourceを確認した。

| artifact path | version/scope | JAR SHA256 |
|---|---|---|
| org/springframework/security/spring-security-web | 7.1.1 compile | dece134a2332c976a2c94ecf13f816c64e8ea7f2139795485afe655fba0408f3 |
| org/springframework/security/spring-security-core | 7.1.1 transitive compile | 98a5011baa78df36fb184e6ce0e8e086ca9a64fcdd8f161c0a96475a3a0907bd |
| io/micrometer/micrometer-observation | 1.17.1 Web compile | eb34f0cd84a879393ae5c21160fc06385ccdc74f36a4d1e31b199f59acfdaf71 |
| io/micrometer/micrometer-commons | 1.17.1 Web compile | f2cee6ef046e72eec8128474c7f58c6217173b45ae373c30de0289f2a56ab0fd |
| io/micrometer/micrometer-core | 1.17.1 Web test | 9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56 |

Security core POMがobservation1.17.1、Frameworkが1.16.7を要求し初回Enforcerは混在を拒否した。Webの3artifactをSecurityの1.17.1へ明示収束、既存broker用coreもWeb testだけ同patchへ揃えた。他module/JUnit/Artemis/Netty/versionは不変更。途中1.17.0候補compileも成功したがSecurity POMのpatchに合わせて不採用とし、正式試験には含めない。Enforcer/NullAway/format/coverageを無効化しない。

release sourceは `/tmp/schubert-spring-security-web-7.1.1-sources.jar` SHA256 `eb520d0386c0119d903baa915dd6999c7361cbdd779b9b698e5a369b58fd6606`、config source `2674581781d685573d067733d75ddc9cf378785c47ea45e59f04b31275a3b4e9`。vendor copyはGitへ入れない。CSRFの標準constant-time比較、request attribute handler、null-save契約、CsrfConfigurer.sessionAuthenticationStrategyの正規差替え点をPG-D-100へ反映。CsrfFilter DEBUGのfull URL診断とsecret-bearing拒否例外を本番log/HTTPへ出さない設定・handler接続は継続作業。

再現は既存JAVA_HOME/local repository指定のonline Web compile後offline運用。完全修飾dependency:treeを2026-09-08 21:37:36 JSTにexit0、`/tmp/PT-WEB-csrf-filter-dependencies-01.log` SHA256 `3a656edb3d7a56d12b7fbd122ee008b1d76ff8a4752d6f275bae44cf067e5790`。探索command/hashは015 csrf-filter-exploration.md。Security chain全体や実API認証の完了ではない。

### 5.9 Embedded Servlet container（2026-09-09、PG-D-109）

実HTTP/ERROR dispatchのPG/PT向けにApache Tomcat embed core **11.0.25**を採用する。5.5のBoot BOM調査時候補11.0.24は本projectへまだ導入していなかった。[Apache公式security情報](https://tomcat.apache.org/security-11.html)を再確認し、11.0.24までに影響するHTTP/2資源漏れや認証/認可関連修正を含む11.0.25へ固定する。未導入候補の選定更新であり、既存toolの無検証置換やSS外部仕様変更ではない。配備直前にもsecurity公告を再確認する。

[Apache公式embedded Tomcat API](https://tomcat.apache.org/tomcat-11.0-doc/api/org/apache/catalina/startup/Tomcat.html)と、[固定release POM](https://repo.maven.apache.org/maven2/org/apache/tomcat/embed/tomcat-embed-core/11.0.25/tomcat-embed-core-11.0.25.pom)、同release sourceを照合。`addContext`によるprogrammatic contextではdefault servlet/JSP/WebSocketを自動公開しない。CoreがServlet6.1 APIを含むため、Webのstandalone jakarta.servlet-api6.1.0依存はcoreへ置換して二重class提供を避ける予定。他module/Spring7.0.9/Security7.1.1/Session4.1.1/Artemis2.56.0を変更しない。全PT・依存収束・classpath・静的解析を再検証するまで導入完了とはしない。

| Artifact | SHA256 |
|---|---|
| tomcat-embed-core-11.0.25.jar | 282b65b9fe43647b1459c0df11101f8599a58de5832075acff485c3705ba4894 |
| tomcat-annotations-api-11.0.25.jar（coreのcompile依存） | d32cc2aad115b27456ce075b2167b3d549aa9ca75439d67f6a60bcc057d7212d |
| tomcat-embed-core-11.0.25.pom | 1dcba0b0070ad6a999dc07c82f2b692f449c29d47a05d77813ab5a72283ddf52 |
| tomcat-embed-core-11.0.25-sources.jar | 1d2ec2c563194f0b768be5a34979ce14eb2dde4f9e866f954c19dfbdcb46b9bc |

取得元はMaven Centralのorg/apache/tomcat配下。Binaryは既存work/toolchain/m2/repositoryに配置。source/POM調査copyは/tmp/schubert-tomcat-embed-core-11.0.25-*、秘密情報なし。再現:

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -N -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress org.apache.maven.plugins:maven-dependency-plugin:3.9.0:get -Dartifact=org.apache.tomcat.embed:tomcat-embed-core:11.0.25 -Dtransitive=true
```

依存取得は2026-09-09 00:39:53 JST成功。正式PT-WEB-20260909-03の実行中はsrc/POM/collectorを固定し、取得だけを行った。組込みPTはloopbackのみ・ephemeral port・JUnit所有temporary directory・明示close、合成Servlet/DB/監査だけとする。TLS/Caddyは本番と同じbackend境界を模擬し、証明書/実serverのIT/ST合格と混同しない。

導入確認: 正式PT-WEB-20260909-05（source1640ca7）で全737件/全coverage100%/静的解析0、PT109のServlet API resource1件・native session0を確認した。単一Tomcat providerへの置換とloopback実HTTP4件のPG/PT導入は完了。本番bootstrap/TLS/CaddyのIT/STは未実施。

### 5.10 MVC・Thymeleaf・DOM PT（PG-D-115）

2026-09-09、WebだけへSpring MVC7.0.9/Thymeleaf3.1.5.RELEASE、test-only Jsoup1.23.2を追加。既存Framework7.0.9/Security7.1.1/Session4.1.1/Tomcat11.0.25/SLF4J2.0.18を維持し、BOMの一括適用やlogging backendの変更はしない。[Thymeleaf公式Spring integration](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html)と[release POM](https://repo.maven.apache.org/maven2/org/thymeleaf/thymeleaf-spring6/3.1.5.RELEASE/thymeleaf-spring6-3.1.5.RELEASE.pom)を確認し、Spring6 integration artifactのprovided/optional Spring依存は既存7.0.9を使用する。Boot4.1.1公式BOMの同組合せと整合する。任意のOGNLを追加しない。Jsoup versionはMaven Central公式metadataのrelease1.23.2を確認した。

取得元は`https://repo.maven.apache.org/maven2/`＋artifact path＋version/artifact-version.jar。依存・sourceは外部toolchain/tmpに保持し、Gitへvendor copyしない。

| Artifact path | Version/scope | SHA-256 |
|---|---|---|
| org/springframework/spring-webmvc | 7.0.9 compile | 8f114c1461692c5e534e82b27de23b7fb23370db8dee7ce0c92d5106906c9555 |
| org/thymeleaf/thymeleaf-spring6 | 3.1.5.RELEASE compile | fd5d306052d7aa6769a8ec77778d328e6f7c83af5ac074df38035bbb1e9cd72b |
| org/thymeleaf/thymeleaf | 3.1.5.RELEASE transitive compile | 4011795f8494dd69e764b7709443dd13d3068ba8ac37624f61d7084f4429cbe2 |
| org/attoparser/attoparser | 2.0.7.RELEASE transitive compile | 75dd1c045492bff8e1963aabb28bfe903c2064e11e27fe2f0f0aff1ad3d84476 |
| org/unbescape/unbescape | 1.1.6.RELEASE transitive compile | 597cf87d5b1a4f385b9d1cec974b7b483abb3ee85fc5b3f8b62af8e4bec95c2c |
| org/jsoup/jsoup | 1.23.2 test | e9d8c856856680427f096d156f02a414289985c930998fcb519ce5be39b42003 |

release source（同URLの`-sources.jar`）: Spring MVC7.0.9 SHA256 `c22ef47b861c6b9dffc9c57e425fe3f7391171b75dda4de11597b36cd306d39f`、Thymeleaf Spring6 3.1.5 SHA256 `935872ace7a59657bb84a8510252c98fd96cae4df7800df6706a6f79055d03df`。Servlet integrationは既存Security7.1.1 sourceのCsrfRequestDataValueProcessorも確認する。

再現: repo root、既存JAVA_HOME/local repository指定で`./mvnw -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am test-compile`を一回online実行。2026-09-09 02:15:57 JST exit0、raw log（非格納）SHA256 `53c61e92d0cc751b4538d282f37d1af24d21bc6690793ddcd93fc001e2761a6b`。以後`-o`。同条件の`org.apache.maven.plugins:maven-dependency-plugin:3.9.0:tree`は02:22:21 JST exit0、SHA256 `1cdbe2b2eb1117d2a3aaaced86cc76d93ccb51e6e87df78a093dbefa1b8306c3`。新推移依存は表のparser/escapeだけ、Enforcer一意性を維持。MVC/Menu PT結果は015のmenu-mvc-exploration.md/正式manifestへ記録する。全画面/本番bootstrap/Log backend固定/IT/STの完了を意味しない。

## 6. 導入予定・工程内service

Native port実機: 本機既存Ubuntu package `libc6:amd64 2.43-2ubuntu2.3`（`dpkg-query -W libc6`）、runtime `glibc 2.43`（`getconf GNU_LIBC_VERSION`）。取得元は本機Ubuntu配布packageで、本工程によるlibc置換・独自共有library導入は行っていない。O_PATH/procfs inode属性とread channel再openも同runtimeで合成PTを実施する。配備先version/FS/systemd条件の確認はITS-H-008。

| 対象 | 方針 | 状態 |
|---|---|---|
| PostgreSQL | 18.6をrootless展開し、実PostgreSQL test runtimeでDDL/Flyway・role/grantのPTを実施 | 完了 |
| Artemis | POM固定2.56.0のFile Journal brokerとproduction `broker.xml` schema/config検査を併用 | 導入済み。実ACL 90組合せ、全route/provider負値、Expiry/DLQ再起動保持までcomponent PT完了。Application adapterを継続 |
| JDBC/Flyway | Flyway 13.4.0、PostgreSQL JDBC 42.7.13をMaven Central artifactで固定 | 完了 |
| 静的解析/coverage | ProtocolはCompiler `-Xlint:all -Werror`、JSpecify、SpotBugs Max/Low、JaCoCo 4指標100%を導入済み。NullAway相当のcompile-time null dataflow、PMD/Checkstyle/Spotlessとparent継承は後続module追加前にgate化する | 一部完了 |
| Secret scan | Program対象source/config/test/reportをcredential/private key/token、raw body marker、CRLF/NUL、disabled/flaky/skipped/not-runと併せてscanしsanitized report化 | 実施中（NK-MSG-001でpattern/known-marker scanを導入しhit 0。全repositoryのentropy scanは総合gateで実施） |

### 6.1 検査process接続準備の既存systemd/ACL環境

2026-09-09、`dpkg-query -W systemd acl libacl1`でsystemd259.5-0ubuntu3.4、acl/libacl1 2.3.2-2を確認。Ubuntu既存package、今回のinstall/upgrade/置換はなし。本体はPATH上でなく`/usr/lib/systemd/systemd --version`、validatorは`systemd-analyze`。`getfacl --version`は2.3.2、libacl.so.1は/usr/lib/x86_64-linux-gnu。system/system-user managerのread-only状態照会はともにrunning。既存service停止/再設定は行っていない。

再現: 上記version照会と`systemctl is-system-running`/`systemctl --user is-system-running`で可用性を確認する。PG-D-131/SS343 §6.1のsource0600とruntime readonly/ACLの区別は、将来の専用unit/ACL実PTで検証する。現在はそのPTを実施済みにせず、IT/ST稼働完了を宣言しない。参照は[systemd v259原本](https://raw.githubusercontent.com/systemd/systemd/v259/src/core/exec-credential.c)。導入先minor版と実ACLの照合は後続gate。

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
| 2026-09-03 | Production broker.xml、NIO File Journal再起動・duplicate cache・1/5/25秒再配送・JMS transaction/DLQ、API/Web moduleのcoverage/SpotBugs中間gateを確認。 |
| 2026-09-03 | `ActiveMQBasicSecurityManager`の実行時UUID credentialでrole/address/operation ACLを検証。値は一時directoryだけに保持し、source/reportへ保存しない。 |
