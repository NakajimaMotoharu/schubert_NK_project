# 開発環境・toolchain構築記録

## 2026-11-05 通常PGPTの明示選択JUnit/coverage工具

既pinのJUnit5.13.4/platform1.13.4とJaCoCo0.8.15に合わせ、Maven Central公式artifactのConsoleStandalone1.13.4とJaCoCoCLI0.8.15-nodepsをhost toolchainへ導入。URL・固定SHA256/SHA512・取得過程の404/既存byte保全・publisherSHA1の限界はPGPT500/635へ保存。production依存/POM/実サービス変更0。635記載URLからartifactとpublisher.sha1を取得して照合し、計算SHA256が635に一致することを確認。標準Consoleの明示12method selector/--fail-if-no-testsと標準JaCoCo reportだけに用い、新しい用途別launcherを増設しない。compileはJDK25.0.4/-proc:none、現FlywayCore13.4.0は型参照のみ。private credential/DB/VM/Rootへの接続は含まない。使用結果は3505/3506、636の具体PT事前判定へ結合する。

2026-10-25 1904/1905静的参照：ASM9.10.1既jar=/home/mini/codex/project1/work/toolchain/m2/repository/org/ow2/asm/asm/9.10.1/asm-9.10.1.jar、SHA ed825d10ab1399c8c0cb669e688cf0c8c82629b4c8399b58352b68e92ca10fcb、download/install0。JDK25.0.4の限定javac55source（proc:none/implicit:none/Xlint-all/Werror/heap768MiB）とjavap/ASM ClassReaderで新96classのsource/参照を照合。normal9246六Main Jar＋既fixture class metadata/103Jarをpinしcompiler Plugin0/targetRuntime0、raw disassemblyは非保存。自己所有slot pg9358/pg9360/pg9362のactual command/env/PID/exit/hashを正本とし、工具10/9vectorとSourceFile所属の検査をPT実行へ転用しない。Root/VM/DB/JMS/鍵やネットワーク操作0。

2026-10-25 1902/1903静的source解析工具：既配置Maven coordinate com.github.javaparser:javaparser-core:3.28.2 を使用（今回download/installなし）、jar=/home/mini/codex/project1/work/toolchain/m2/repository/com/github/javaparser/javaparser-core/3.28.2/javaparser-core-3.28.2.jar、SHA256 b5499a3b1c40b16c0671fabe478c9aafeab38160c6fde74a6c13f42d86716ecd。JavaParser JAVA_25 APIは実jarのjavapで確認、独立経路はJDK25.0.4のjavax.tools/com.sun.source JavacTask.parseのみで外部libraryなし。新規専用slot pg9344/pg9346、javac --release25 -proc:none -Xlint:all -Werror、formatter1.36.1を固定。対象module Jar/target class load/compile/analyze/generate/annotation processor/JUnit/native/VM/DBを使わず、工具helperだけをcompile/runする。実command/env/PID所有/原exit/hashは9344/9346 manifest/stages参照、各16/13手書きmetadata vectorは製品PTに加算しない。環境PATHは当JDK/bin:/usr/bin:/bin、LANG=C.UTF-8、network操作0。既source正常build9246/旧成功4222等は確認再演しない。

2026-10-25 C01 format（1851）：1519と同じ既Caddy2.6.2 binary `/home/mini/codex/project1/work/characterization-tools/root/usr/bin/caddy` SHA678c1849…を実byte照合して使用、新取得/版変更0。fmt stdoutだけをapply_patch反映、当sourceのfmt三/普通adapt二を最小env/自己slot XDG/15秒/明示inputで実行しstate生成0。別途存在する2.11.4を暗黙採用せず、実VM採用版/動作は未認証HOLD。JDK25.0.4/Maven3.9.12正常六compile/ordinary三/JaCoCo0.8.15+ASM9.10.1実partial計測のcommand/source/env/hashは9014/16/18/20へ固定。四100未達を0/PASSにしない。

2026-10-25 1844/1845追補：8979で公式固定tag v8.30.1 default config97,731byte/222ruleを公開HTTPS一件追加取得、SHA256 e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf。専用new-only slot/実URL/環境/entry hashは原manifest97b57201、既binary/config/settingsを上書きせずscanner再演0。8980/8982は既findingのexact captureと公開Git blob bytesの限定分類、29,468誤検出根拠付き/10,618未分類・vendor path限界53、全G07未受入。8966二downloadと別計数、秘密値出力0/製品PT0。

## 2026-10-25 G07 Gitleaks8.30.1専用toolchain（1841/1842、PG-D628）

公式 https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1 のLinux x64 archive/checksums二件を8966へ記録した固定SHA256/sizeで取得・照合、bin/licenseだけを `../toolchain/gitleaks-8.30.1-linux-x64/` のnew-only0700へ導入。binary SHA256 88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509、実version8.30.1/終了0。取得URL/二asset hash/OS/actual command/実entry hash/licenseはPG8966 manifest ef630842…を正とする。published hash+HTTPSでありvendor署名とは称しない。system PATH/settings/credential/製品POM変更0、公開download2/target通信0。

再現entry `tools/quality/pg8966_gitleaks_toolchain.py` は既slotへ再実行しないnew-only契約。scanは `pg8968_public_blob_scan.py` の明示固定content・合成canary成立後のみ、default rulesを明示configで使用しprojectignore/baseline非適用、reportはstdout memoryからallowlistへ変換する。8970で独立hash/安全出力を確認。今回55,722 blob/40,086未分類・binary等22限界、PG/PT合格やG07受入と同義でない。版/環境/証跡/制限・次分類は1842参照。

2026-10-24配置訂正（1758/BUG1697）：Prometheus textformat/model/config1.7.0の取得/全checksum/専用M2座標はそのまま、Production依存はAPI/Web各appのtextformatsへ明示しBootstrapの新Micrometer/textformat依存を退役した。SS311限定共用起動責務を広げず、追加download0/新module0/既settings・内部snapshot上書き0。8317責務guardは既PT-IDEM-016のWeb→API test-only edgeを元f02 POMとscopeで区別し、compile/runtime等への昇格を拒否、製品POMの既test依存/実行JUnit5.13.4は不変更。各新sourceの正常六build/Enforcer/実classpathと1758の同source品質を正とし、以下初稿共用配置の記述は歴史として扱う。

## 2026-10-24 Summary formatter正式外部Maven座標（1753、PG-D592）

既隔離SDK8170/8173のio.prometheus textformats/model/config1.7.0の各Jar/POM6byteを、既checksum＋SHA256と照合し専用M2の新外部座標だけへ配置。元8240原1028c8ee、独立8241原02af072fを正とし、元publicArtifactDownloads=2は誤りで実4（client_java/client_java_parent親POM＋checksum）。原改変せずBUG1694/YKT1445で追記訂正する。秘密/内部snapshot/settings上書き0、異hash/symlinkは拒否。

Maven model解決用imported BOMはJunit6.1.0（8243原03d9fe43）、OpenTelemetry instrumentation2.28.1-alphaほか親/import四POM（8244原0b7fec5c）。これらは第三者POMのdescriptor解決のみで製品JUnit5.13.4やRoot/plugin設定を変更しない。各全座標/実URL/hash/command/PID/終了は公開manifestとown PG379 slotsに固定。入手先はhttps://repo.maven.apache.org/maven2/ の指定公開座標、curl --disable/HTTPS限定/有限timeout/size、proxy等非継承、retry/redirect/代替経路なし。published SHA1＋独自SHA256照合でありvendor署名とは称しない。

再現entryは tools/quality/pg8240_prometheus_maven_coordinates.py → pg8241_prometheus_coordinates_post.py → pg8243_prometheus_bom_prepare.py → pg8244_prometheus_descriptor_closure.py。新only slot、既runを再起動せず元receiptを参照する。Pythonは既PYTHONPATH/pyflakes runtime、JDK25.0.4/Maven3.9.12/offlineの通常sixで確認、失敗/未実行PTは成功へ含めない。実daemon/service/VM/DB/network target操作は行わない。

2026-10-24Prometheus SDK分離依存（1739～1740/PG-D584）：公式Maven Central固定registry1.17.1/client1.7.0新10Jarと既core/commons/observation1.17.1/Hdr2.2.2/jspecify1.0.1の5pin。隔離toolchain/prometheus-sdk-1.17.1-client-1.7.0-new-v1へPOM/Jar/各repoSHA1取得・独立SHA256、既M2/Production POM変更0/target init0。PG8170原371004a7/source69204dd136341d24df67d8b51fc6fea8fc3b7c31、当15Jar3,688,470byte/1824class名/重複0・新PG8173原a5a2bfbeの独立7反例で確認。旧8172prefix guardはBUG1688/YKT1439・00581f4b7で是正/元post保全。全hash/URL/directgraph/非runtime除外理由/再現は1740/原manifest、vendor署名やMaven全effective/製品PTを認定しない。実VM/DB/daemon等0・全actualHOLD維持。

2026-10-24公式構文工具（1737～1738/PG-D583）：Prometheus LTS3.13.5/linux-amd64公式archive SHA0388822ace519c5a3a8ef556a541ce1b536e21d872f82deded465bd27a5a0699をhttps://github.com/prometheus/prometheus/releases/download/v3.13.5/prometheus-3.13.5.linux-amd64.tar.gzからnew-only取得。toolchain/promtool-3.13.5-linux-amd64へpromtool/LICENSE/NOTICEだけ抽出、実binary SHA4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff/mode0700/実version0。PG8162原ca3c9318（tool準備source0c246）/PG8164原df069f5e（source941bd/設定syntax6ID・5process期待0/0/1/1/1）/PG8165原f18a6b5f独立post。再現・由来/command/全hash/環境とnew-only再発行防止は1738、binaryはGit外。公式TLS+掲載SHAでvendor署名認定ではない。daemon抽出/実サービス/VM/DB/Root/target通信0、公式schema範囲だけで実運用/全品質未受入。元tool/config/Java/POM/秘密/原保全物の変更0。

2026-10-24 DLQ供給観測：既JDK25.0.4/Maven3.9.12/SDK4＋正常六compile API-only2をoffline再利用/導入取得0。sourcecfd8c12dd/237普通PT31suite/実59四100/CRC0・正常六compile/PT0・全1760Main/元1669byte不変/三POM・SDK・当五rule0。raw28同byte全理由/生成115の当直接契約/除外0、環境/command/time/hashは1690、actual操作0。

2026-10-24 Integrity：既JDK25.0.4/Maven3.9.12/SDK4＋正常六compile API-only2をoffline再利用/導入取得0。source676b954e7/229普通PT30suite/実56四100/CRC0・正常六compile/PT0・全1757Main/元1669byte不変/三POM・SDK・当五rule0、全環境/command/time/hashは1688。工具draft文字列置換の構文不備は実行前pyflakesで拒否/未実行工具のみ是正→実0、Product再演0、raw28全理由/生成104/除外0・actual操作0。

2026-10-24 Restart：既JDK25.0.4/Maven3.9.12/SDK4＋正常六compile API-only2をoffline再利用/導入取得0。source9f7697a28/221普通PT29suite/実54四100/CRC0・正常六compile/PT0・全1755Main/元1669byte不変/三POM・SDK・当五rule0、環境/command/time/hashは1686。raw28全理由/変更Threshold百分率method不変/生成新6＋既93当実行/除外0、actual操作0。

2026-10-24 Backup供給観測：既JDK25.0.4/Maven3.9.12/SDK4＋正常六compile API-only2をoffline再利用/導入取得0。source017308824/212普通PT28suite・実52四100/CRC0・六正常Main/Test compile/PT0・全1753/旧1669byte不変/三POM/SDK/五rule0。全環境/command/time/hashは1684、raw28同byte理由/生成新11＋既82当実行/除外0、actual操作0。

2026-10-24自動close禁止：既toolchain/SDK再利用・導入取得0。source9c初回204F2/normal六compilePT0を保持し、旧oracle二追補source3aの204/27・実49四100/CRC0/新正常六compile/全1750/当五rule/全94traceを別資格。PMD全28は二source行移動をexact二行guard挿入へ結合し抑制0、全環境/command/日時/hash/失敗原因は1682。actual操作0。

2026-10-24是正完了：source8f6b3bff2/202PT27suite/実49四100/六正常compile/全1750Main/SDK各pin一致/当五rule0・取得0。工具7542旧raw位置guard exit1を保存→新7543で一件の明示行移動context再認証・PT再演0、全command/OS/JDK/tool/time/hashは1680。最新fresh25/75・専有費N/Tnull、全actual操作0。

2026-10-24：Expiry6247/200の全環境/commandは1677。Async byte単位是正8f6b3bff2/1679は既JDK25.0.4/Maven3.9.12/SDK4＋正常六compile API-only2をoffline再利用/導入取得0。host初回PYTHONPATH pyflakes不足import exit1/PT0/job未作成、正規PYTHONPATHで唯一7532実202/27成功、同source独立/六compile検証中。実broker/DB/VM操作0、旧成功の転用0。

2026-10-23 Async Queue警報：既toolchain/SDK4＋正常六compile API専用2再利用/取得0。d56b2cc0a/192普通PT26suite/実46四100/CRC0/六正常Main-Test compile0/PT0、全1747Main/旧1669byte不変/三POM/当五rule0/全92trace。元pin変更0を独立読取検査し、raw28同byte理由と新生成6＋既66当ordinaryを結合、環境/command/time/hashは1675。実queue/JMS/DB/外部操作0、mode-neutral pure kernelだけ。

2026-10-23 WebLog滞留警報：既SDK4/normal六compile API専用2/全toolchain再利用・導入取得0。3174583f4/184普通PT25suite/実44四100/CRC0/六正常Main-Test compile0/PT0、全1745Main・旧1669byte不変/三POM/当五rule0/全90trace。raw28個別理由と生成新6＋既60samebyte/current ordinaryを結合、環境/command/time/hashは1673。新marker/外部接続/実queue観測0、mode-neutral pure health kernelのみ。

2026-10-23 API Outbox二family結線：既toolchain/SDK/六aux/harness不変更/導入取得0、69a835b2b/98普通PT12suite/実20四100/CRC0/六正常Main-Test compile0/PT0、全1743Main/旧1669byte不変/三POM/当五rule0/全88trace。raw13の新private lock/同一failure未知化三contextを正確source行と独立ordinary契約へ個別分類、抑制・有効違反0。環境/command/time/hashは1668～1671、実DB/Clock/driver接続0。

2026-10-23 API Outbox観測Repository：既toolchain/SDK/六aux/harness不変更、332f970a7/90普通PT11suite/実19四100/CRC0/六正常Main-Test compile0/PT0、全1742Main・旧1669byte不変/三POM/当五rule0/全86trace。raw10の新existing-variable TWR二件は正確source/row/column・全close故障fixtureへ個別理由、全未分類/有効違反0。導入取得0/実DB-driver接続0、環境/command/time/hashは1664～1667。

2026-10-23 API Outbox滞留時間：既toolchain/六aux/harness不変更・導入取得0、d6c7f61b5/80PT10suite/実17四100/六正常compile/PT0・全1740Main/旧1669byte不変/三POM/当五rule0。API18実byteと歴史Batch43(source9d8/176)/Web10(source6db/27)は別domain、全84trace・新record六generated contract/九negative・raw8全個別理由、環境/command/日時/hashは1660～1663。actualDB/Clock/Root操作0。

2026-10-23 Web生成補足：6dbf7f17b/27PT4suite/実9四100/六正常Main-Test compile・当normal classpath、既SDK/工具再利用・取得0。新JUnit launcherの変更はgenerated Test一追加/27件四型、全失敗・未実行guardを保持。SDK4と正常六compile API専用2を分離、1738Main byte不変/公式filter・JDK同byteのみ参照、元PTの転用0。全command/環境/hashは1659。

2026-10-23 Batch generated補足：既toolchain/SDK4/harness不変更、source9d8e52037・176PT/24suite/実42四100/六正常compile/全1738byte一致。正常六compileのSDK4＋API専用既2を当Batch auxiliary4と分離、全Main不変更に基づく五rule/JDK31fold/公式filterの静的性質再利用（実行転用0）。初回commandのPYTHONPATH不足import exit1・実job未開始をtool費へ保存、correct環境初回job0。全command/環境/hashは1657/7420～7430、導入取得0。

2026-10-23 Outbox件数/生成contract：既六aux/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15再利用/取得0。元dbb64普通PT/四100は歴史保全、生成補足Test-only fcedの7402/7404真正72/9suite/実15CRC0/L236M52C15B118全miss0/raw8個別理由、7406正常六compileのみ/7408全1738/三POM/五rule0。javapで6型/生成21method/公式RecordsFilter→nested Matcher/EnumFilter/JDK31 hashを独立確認し生成contract8を実行、counter合成/除外追加0。src.zip symlink先欠落は記録してinstalled bytecodeで照合、7411工具誤判定exit1を保存/39c0915c5→新7413で是正・PT再演0。環境/全command/hash/横展開OPENは1647・1650～1653。

2026-10-23 operation mismatch metric：既SDK四＋Hikari/SLF二aux/JDK25.0.4/Maven3.9.12/静的工具をoffline再利用、導入取得0/harness不変更/実token-HMAC-key-auth操作0。7376/7378当56PT7suite/実12CRC0/L197M41C12B95全miss0/新metric raw0・既8理由同byte再照合、7380正常六compileのみ/7382全1735/三POM/五rule0、7384全77trace。元command/日時/環境/hashは1643～1646、actual全HOLD/全体451未受入を維持。

2026-10-23 API pool借用型観測：既API HikariCP7.1.0/Jar2be45c641b841e81df87292e181f2c203500c5f0e9a1676f135927387f3cf40b、親管理SLF4J2.0.18/Jar44508fd1576500688c790b190acdd16fec4f8c79a3e0b900afd70503cf055f55、SDK四Jar/JDK25.0.4/Maven3.9.12をoffline再利用/導入取得0。M2 provenance/POM hash/upstream/re現commandは1639・7362begin/7369、actual pool/config生成/JMX/DBなし。harness一Hikari依存だけ追加し7369で全品質意味不変/六負改変、root parent原e7同byte・Production版不変更。7362/7364当48PT6suite/実10CRC0/四100/raw8全個別理由、7366正常六compileのみ/7368全1733/三POM/五rule0、7370全75trace。実source/管理/外側期限/Root等HOLD不変更。

2026-10-23 API DB pool四metric：既JDK25.0.4/Maven3.9.12/SDK四Jar/静的工具だけ再利用/導入取得0、Hikari/DB管理・接続0。7348/7350当32PT4suite/単一sessionCRC0/L136M31C8B70全miss0、lint-NullAway/SB-CS0/PMD既5同byte理由再分類・新Pool raw0。7352六Main/Test compile-package0/PT0、7354全1731Jar/三POM/五rule0。再現/command/source/OS/tool/hashは1635～1638元manifest、actual source/外側期限/警報等未受入HOLD。

2026-10-23 API count→metric結線：既JDK25.0.4/Maven3.9.12/SDK四Jar/静的工具だけ再利用、取得/導入/実driver接続0。元d791/7328・7332はSDK registry型誤認でtestCompile exit1/PT0、BUG1659起票後003のtest-local AutoCloseable adapter九生成だけ修正。7340/7342当24PT/単一sessionCRC0/L91M18C5B43全miss0、lint-NullAway/SB-CS0・PMD raw5を7338同source限定分類/抑制0。7344正常六Main/Test compile0/PT0、7334全1728Jar/三POM/五rule0。環境・再現command/元失敗と成功path hashは1631～1634、実環境HOLD不変更。

2026-10-23 API readonly count source：既JDK25.0.4/Maven3.9.12/SDK四Jar/静的工具だけ再利用、取得/導入/実driver接続0。PG7314/7316当16PT/単一sessionCRC0/L76M15C4B41全miss0、lint-Werror-NullAway/SB-CS0・PMD raw2は実TWR誤検知で7324個別分類/抑制0。7318六Main/Test compile-packageのみPT0、7320全1727Jar/三POM/五rule0。最初のSpotless `-pl schubert-nk-api` exit1はroot相対path不足、`-pl src/schubert-nk-api`でformat0後sourcefaf7固定。再現command/実行環境/全path hashは1627～1630と元manifest、実環境HOLD不変更。

## 2026-10-23 API Async job metricの既SDK再利用

PG-D539/1623～1626、APIへ既core1.17.1を一compile nodeだけ追加。SDK四Jar/入手元/versionは既Batch/Webの下記記録と同じで、新規取得/除外/別backend0。再現はPG7300（API monitoring ordinary verify/8PT1suite）→7302（実3class/CRC/四100/静的0）→7304（六正常Main/Test compileのみ）→7306（全1726/四domain/三POM厳密）→7307（harness/POM十二改変拒否/旧DDL五状態）→7308/7310（全65src/当APIと歴史域の独立転用拒否）。API childは既真Batch harnessのsource role/artifact/不要fixture routing以外全XML同義で、親Enforcer/NullAway/lint-Werror/SB/JaCoCo四1.0を維持。新8へ歴史Batch169/Web23の成功やcoverageを移植せず、実DB/API/Root/exporter/IT-STを認定しない。

## 2026-10-23 Batch二metricの同版SDK再利用

PG-D536/1611～1614、Batch direct compile/core1.17.1一nodeとhost harness同版を追加。SDK取得0/版変更0/除外0、下記1572/7106既入手元のcore9ca47dfa/commonsf2cee6ef/observationeb34f0cd/Hdr22d1d431全四Jarを開始/終了pinで照合。再現はPG7252 wrapper（offline通常verify/153PT21suite）→7254独立CRC/四100→7256通常六compileのみ→7257 POM一node/六負改変→7258全実Jar/二POM全semantic。新規install/downloadや実exporter/Batch/DB/Root起動は不要・未実施。Testは所有SimpleMeterRegistryにAutoCloseable bridge、productionは借用/close0。全50系列は40counter＋10gaugeでhistogram内部auxなし、未知lastSuccessはNaN。品質の範囲は当36classだけで全体451/IT-STを認定しない。

## 2026-10-23 Web Micrometer coreを同版のままcompileへ昇格

PG-D527/1573～1575、既managed/test版1.17.1のcoreをWeb direct compileへ正規追加。version変更/依存除外/他POM semantic変更0を7122 9e62721bで確認。runtime Hdr2.2.2は下記1572の正規local導入を使用。core9ca47dfa/commonsf2cee6ef/observationeb34f0cd/Hdr22d1d431の全Jarを元15PT/独立static/六compileの前後hashへ結合した。実SDKの自己所有SimpleMeterRegistry/MockClockだけで15PT/四counter100、実7classを正規Web Jarへ照合、全体451/実exporter/Root runtimeやIT-ST認定ではない。Micrometer registryはcloseを持つがAutoCloseableではないため、Test自己所有scopeにだけ明示bridgeを置き、本番Recorderは借用先をcloseしない。Simple providerは九SLO×35の315内部Gaugeをprimary1785とは別に保持、1573のprimary根拠/残存riskを維持する。新外部通信/SDK版変更/別backend置換0。

## 2026-10-23 Micrometer1.17.1の正規HdrHistogram2.2.2をoffline補完

1572/PG7104原bd4e07ea。既core1.17.1（§5.8の9ca47dfa…）のruntime依存HdrHistogram2.2.2を、既SHA512検証履歴のあるApache Artemis2.56.0配布libから同版・Jar SHA256 `22d1d4316c4ec13a68b559e98c8256d69071593731da96136640f864fa14fad8` とembedded正規POMを保ったままlocal M2へ新規導入した。既元archiveは現存しないため今回全archive再検証済みとは称さず、既導入由来と現在Jar版/metadata/hashを区別する。Maven install-plugin3.1.2/-o/-N/install-file/元pomFile/generatePom=false、JDK25.0.4/Maven3.9.12、repo既toolchain/m2/repository。対象座標非存在を先確認し既物上書き/元Jar変更/依存除外/代替POM/外部通信0、全byte・終端0を保存。cache Jar binaryはGit非格納。元ライセンスはvendor embedded POM/Artemis licenses/LICENSE-hdrhistogram.txtを参照。再現/出所/command/設定/hash/原証跡は1572と `018/evidence/provisional/PG7104-micrometer-dependency-prepare-v1/manifest.json`。これは環境準備でPT合格0、Web Production依存追加/実backend接続は次の別工程で検証する。

## 2026-10-23 PG6960/F02 ArchUnit1.4.2・原Jar独立静的確認

既SS311§2のArchUnit工程をtool専用として補完（PG-D516/1526）。入手元は固定Maven Central `https://repo.maven.apache.org/maven2/com/tngtech/archunit/archunit/1.4.2/`、公式release https://www.archunit.org/news/release/2026/04/18/release-v1.4.2.html 。core Jarを既私有toolchain `architecture/archunit-1.4.2/` へ新規取得し、公開SHA1と一致・SHA256 `6d8adf69a3f109ebe1b395764feb07f919e9e0e2ab5e2ea141d2e6251ba7d17f`（4550585byte）。POM SHA256 `05618298545286d697fa6d066f65aebff7f68e8ec88cbf2c3e7d77ce18f26636`、取得receiptは018/provisional/PG6960-archunit-toolchain-v1/manifest.json。vendor POMはSLF4J2.0.17を宣言するが、toolは既承認・導入済み同APIの2.0.18だけを明示classpathへ置く（SHA25644508fd1576500688c790b190acdd16fec4f8c79a3e0b900afd70503cf055f55）。Production POM/runtime/GAV変更0、binaryはGit非格納。licenseは取得POMのApache2.0/BSDを記録。

再現：既Java25.0.4で `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<既pyflakes-runtime> python3 -B tools/quality/pg6960_archunit.py`。同一成功slotはreceipt/hash読取のみ、未完beginから二重起動しない。新しいsourceへ適用する場合は別の着手/原Jar資格/未使用slotを先に用意する。原PG6930の六Jar全1669class hashを照合し、ArchUnitのclasspath不足型解決を無効化したbytecode importerだけを使用。対象classのload/reflection/init/entry実行0。全物理所属・全1669import・5依存境界rule、手書正1/負10canaryとinitializer非実行を確認する。JDK javac lint/Werror compile0、Production PT再演/新PT/coverage/VM操作0。

当原static終了0、全1669class/76823依存/54776call・rule違反0、正負11canary期待一致。原結果SHA2567f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f。各Java childのbegin/exit/time/stdout/stderr hashをsemantic判定前保存。SLF4Jのprovider未指定/NOP通知3行は原stderrへ保持し、隠蔽やstatic違反扱い0。F03 Root11の意味審査・実Root/VM/native等の成功を本追加staticから主張しない。F02個別受入は別の全criteria/原build/toolchain/終了照合後とする。

## 2026-10-19 隔離DB観測の明確化（BUG1440/YKT1204）

018/1091を環境区分訂正の正本追補とする。共通選択は一時PostgreSQL18実clusterでDDL/Flyway/Hikari接続を実行するが、原本/VM業務DBへの操作ではない。現在probeは18.6（Ubuntu18.6-0ubuntu0.26.04.1）、postgres SHA30a38e0516ec1bde4b8ca710cf28ba51ee78bd004cabbf3107e7a52d5414a64a。旧run開始時binary identity欠測はnullのまま保ち、遡及認定しない。pg5148の将来開始manifestへ設定binary version/SHAを追加、独立管理二件/九tool lint0、既成功Maven再演/導入/原本DB操作0。

## 2026-10-18再開時のhost再観測（導入変更なし）

host kernel `Linux 7.0.0-38-generic`、Python `3.14.4`、既存JDK path `/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java` はOpenJDK25.0.4（2026-07-21、build25.0.4+7-1-26.04-Ubuntu）。commandは`uname -sr`/`python3 --version`/同`java -version`。これは現在hostの読取結果で、旧全回帰のOS/JDK証跡を置換せず、guest/source/VM再認証を代替しない。今回toolの新導入・version変更0、既3791 full/独立/署名/18ABIの再実行0。

localbootは変わり旧forward/SOCKSが消失したため、元aru QEMU/boot/diskをpinnedSSHで確認後、4996新ownedforwardと5045新loopback SOCKSだけをnew-only private receipt（boot/parent-child ticks/argv/UID-GID/正確socket）へ束縛した。VM二重起動/鍵転送/旧PIDの権限再利用0。実値/receipt・再開方法は最新456、秘密key/credentialをGitへ格納しない。

2026-10-15 BUG1258/YKT1024：既CLI all-deps Google1.36.1 SHA25b400f003089d23cc5320cdaf1a16cabee19b8aa3434d0ff021b3d9f42154b4、Maven core1.36.1 SHA57f9b550a662dcbbdf344073e3f5812b837a0e6e430548d8a0a3c9090cada65dとPOM指定1.36.1を実照合。差は版でなくlong-string reflow。installed primary Spotless3.10.2/lib4.10.2のjavap `GoogleJavaFormat.newFormatterStep`→`GoogleJavaFormatStep.defaultReflowLongStrings`はfalse/iconst0を確認。Maven正規整形後、CLI既定dry-runはexit1/当Sessionのみ差を検出、`--skip-reflowing-long-strings`ならexit0。同1.36.1でこの差を独立再現した。正本Spotless設定を変更せず、既JDK25.0.4/Maven3.9.12でbatch spotless:apply actual0/347中1変更・346既clean、全六module spotless:check actual0。新取得/install/OS/global変更0。再現commandは411補足、raw actual失敗2918と新formatted61資格2926は保全、新whole2930は全六format first。既Main全byte/source差0を確認、formatter-onlyでも旧失敗全体を新成功へ加算しない。

2026-10-08 PG519/BUG821/YKT590：host専用Python undefined-scope検査へPyflakes3.4.0を固定導入。host Python3.14.4/Linux、pip/pyflakes moduleは未導入だったためsystemへの変更0、PyPI primary JSON `https://pypi.org/pypi/pyflakes/3.4.0/json`が指定するwheel `https://files.pythonhosted.org/packages/c2/2f/81d580a0fb83baeb066698975cb14a618bdbed7720678566f1b046a95fe8/pyflakes-3.4.0-py2.py3-none-any.whl`をwork/toolchain/pyflakes-3.4.0へnew-only保存、SHA256 f742a7dbd0d9cb9ea41e9a24a918996e8170c799fa528688d40dd582c8265f4f確認後unzipでruntimeへ展開。再現=固定URLをcurl --failで取得→sha256sum比較→unzip -q wheel -d runtime→`PYTHONPATH=/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -m pyflakes --version`、出力3.4.0 Python3.14.4 on Linux。全wheel/展開packageはGit外、global pip/reset/課金0。
旧PG519Ref原sourceへの静的再現はundefined baseline line85を検出。exec_record/command/metadata等の固定原byteからAST注入する名も未定義として表示するので、後続wrapperは認証したdynamic名だけを明示allowlistとし、baseline/owner等を包括除外しない。Production Java静的6module検査の代替ではなく運用工具の追加予防で、現在のnative13680/UNKNOWNを合格化しない。

2026-10-02 PG426/BUG522（隔離VMのみ）：06:35UTCのapt-daily-upgrade/needrestartがPID1 reexecと複数サービスを再起動し、owner/request退役後のExpiryをcredential無し243にした。Source回帰障害ではなく環境外部変更として915/916へ先行起票した。更新終了/job0を照合し、root-private `/var/lib/pgpt-s1-preservation/pg426-environment/timer-before.properties`へ2timerの元ActiveState/UnitFileState/予定をdurable保存、M下で`systemctl stop apt-daily.timer apt-daily-upgrade.timer`。両timerはruntime inactive、installed enablementは不変更、apt2serviceはinactive/MainPID0/Job空。恒久mask/本番設定変更なし。試験再開前にもruntime状態/jobを照合し、VM reboot後のtimer再開を未確認のまま走行しない。長時間PG/PT終了後の復旧は、worker/public全停止・原本/成果保全・M/Aが未所有であることを確認し、保存した元activeのtimerだけ`systemctl start apt-daily.timer apt-daily-upgrade.timer`、enablement不変を照合する（試験中は復旧しない）。予期せぬpackage更新/reexec/DB接続断はUNKNOWNとしてnative合格へ算入しない。

同日16:35 VM実version：Linux7.0.0-34-generic、glibc/libc6 2.43-2ubuntu2.4、systemd259.5-0ubuntu3.4、PostgreSQL18.6-0ubuntu0.26.04.1、OpenSSL/libssl3t64 3.5.5-1ubuntu3.7。更新の入手元はVMのUbuntu signed APT index（libssl3t64のpolicyはarchive.ubuntu.com resolute-updates/main及びsecurity.ubuntu.com resolute-security/main amd64）。取得/変更履歴rawはprivate apt logs、今回導入命令の新発行なし。JDK25.0.4及び署名PG425の全BOM/180artifact61deps25SQLは前後再検証済み。既存host全2878は同Source a3c86daf3だがVM更新後のnative検証の代用にはしない。PG426は旧243/全18/current/Expiry要求・owner/原本222row全14列/Backupを保存し全8kernel・M/A・DB/advisory・同boot/署名の下で未配送要求だけtyped退役、単一Expiry reset-failedをGCとして記録した。過去worker0やfresh結果の捏造なし。工具87独立assert/実nativeexit0、新通常Morningは同Source/同署名で検証継続中。

2026-10-01 PG406/S3実行物独立照合：VM上でAPTのsigned indexを使い`apt-get download util-linux=2.41.3-3ubuntu2.2`（archive.ubuntu.com/resolute-updates/main amd64）→新規`/home/ubuntu/pg406-executable-provenance`へdeb保全→`dpkg-deb -x ... extracted`。APT indexとdeb SHA256は`11fd410b1d3797b1e9127b68302160213c15e1553745fb6982e270b1e32d1f2a`、1070kB/1069858bytes、展開setprivとinstalled `/usr/bin/setpriv`両SHAは`86965a019d37dc11d176ce8cbe9f5f5f8f37027c95e03cb4a8cad4c73d940993`。package install/旧binary変更なし。Javaは既存Ubuntu JRE deb `openjdk-25-jre-headless_25.0.4+7-1~26.04_amd64.deb`（SHA `8ec6ad87cc4692f8a89440879c146adf87ceabe7456db631644ecbf489ee5622`）の元展開とself-contained copy、VM `/opt/jdk-25.0.4/bin/java`の全byte SHAが`c324471f8b7933a3cb401eafbc35a7055443779b438a3ab928bda3867a1b8ab1`で一致。新規単独Java実体採取を信頼基準にせず既存取得元/固定deb/versionを根拠とし、現在APT indexでは旧JRE versionの再取得はできないため旧debを保全する。ELF/hash/profileはSS343/SSC137/PT297へ対応、実native exec/ordinary zeroCapsはまだ未受入。binary/deb/credentialはGit格納しない。

2026-09-28 PG316/SSC098/BUG305: 各roleの局所Maven convergenceに加えて実release GAV版matrixを照合。既存Webで既に採用済みCommons Logging1.4.0/JSpecify1.0.1を親reactorへ集約（新規未使用版の選択ではない）。入手元Maven Centralの`commons-logging/commons-logging/1.4.0/`、SHA256 d175dbd751dd782a63bde28c7a039520e971f25e84b79c19b8435edc3603e0dc、`org/jspecify/jspecify/1.0.1/`、SHA256 070d75f261fe4c5b8202508366715f7f2d4660f88c8ef7e6d3575e48c9683b66。既存隔離repoをoffline使用、Rootにpinし子property/Web管理上書きを除去。再現はJDK25.0.4/Maven3.9.12の全6 clean test/report/static→package/runtime dependency copy/list→test-only AssembleReleaseFixture（fixed Flyway13.4 coreをbuild-side classpath追加）。API runtimeにFlywayを追加しない。source/GAV/実byte独立oracleと全回帰は後続必須。

PG315候補fixture: 169payload/63GAV/23SQL、38,123byte元manifestとOpenSSL3.5.5（Host既存）Ed25519 detached署名。private testkeyはGit外private700/600、pin DER44byte SHA3664698f42d75d702ef98a869241e3ff6cb312bd6d87ee90db0271c3d7a505a1を候補外root0400へ配布。Production pin custody/issuer完成ではない。専用VMの実root/M/A/pin署名まで到達、RW拒否とROでもcross-role版差のため拒否。旧候補/署名/exec保全、新version0.1.0-PG316を使用する。offline QCOW2 snapshot/boot tmpfiles設置→実boot再生成、M/A空root0600/同tmpfsは実観測済み。snapshotを業務backupとしない。

2026-09-28 PG313: 既存Gson2.14.0をShared Bootstrapの固定manifest STRICT parserにも明示compile依存として利用。Maven Central `https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.14.0/`、隔離repositoryのjar SHA256 `2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f`。既存API/Web版と同じでglobal設定不変更。JDK25.0.4 javapでJsonReader.doPeek/checkLenientのinstalled primary bytecodeを照合し、EOF以外はSTRICTが拒否することをPG-D313へ記録。POM共通変更のため全6回帰が必要であり、限定40 PTだけで正式認定しない。

## 2026-09-28 PG311 native027 root DB/run原本接続

同隔離VM Linux7.0.0-31/JDK25.0.4/PostgreSQL18だけで実M/LoadCredential db-batch/fixed role/session advisory71419602/legacy参照不存在→永続run原本を接続。Root credentialはpublic transient Unitでmode0500/0400/root:root/ro tmpfsを先に観測、secret値は出力しない。db-batch source不存在とbatch role passwordNULLを照合後、ProvisionBatchDatabaseでnew-only600初期配備。namespace maintenance/runs/attempts0700もmissing初期配備のみ。既存PG310 testUnitはhash2c527…/inactive/PID0/cgroup不存在を照合しPG311内へ退避後、固定morning名のPG311 testUnitに置換。追加packageなし。再現tool/Unit/command/hash/failed attempt・02:00前の成功時刻は018144～146/provisional PG311。originalはpending、次は同run/activation/cutoffを明示resumeしfresh startを繰り返さない。native後Unit停止、execはprivateに保全、same-byte coverage補完でありfullPGPT/backup/admissionではない。

## 2026-09-28 PG310 native026 root M/Aとcold backup終端

既存隔離VMだけで固定朝controller名のread-only試験Unitをnew installし、Production RootStartupContext/BackupUnitTerminationとM/A能力を実測。source/helper/Unit/command/個別hashは018141/143/provisional PG310。capability空ではPID1 exeを読めず拒否、root-only CAP_SYS_PTRACE＋ProtectSystem=full/NoNewPrivileges/PrivateTmp/Devices/ProtectControlGroupsで読み取り成功。実在しなかったmaintenance.lockだけをNoSuchFile確認後`install -m0600 -o root -g root /dev/null /run/schubert-nk/maintenance.lock`で初期配備、既存lockfile/root/資格情報は変更なし。再現は固定VM marker確認→対象Unit停止/MainPID0/cgroup不存在確認→保全hash照合→helperを固定Unitで起動→sanitized結果とUnit終端→明示stop。初期失敗も保全して合格算入しない。host system Unit/権限変更なし、追加packageなし、普通serviceへのcapability増配なし。root-only試験Unitは停止済みだがVM内artifactを保全する。実親backup/全BOM/業務起動済みではない。

## 2026-09-25 SnakeYAML Engine 3.1.1 Web追加（PG273）

Web moduleにも既存APIと同じ`org.snakeyaml:snakeyaml-engine:3.1.1`を明示依存として追加。入手元・jar SHA-256・Java25/Maven wrapperでの再現手順は直下PG272の記録と同一。追加OS package/daemon/秘密実体はなし。Web15非秘密keyをdefaults→common→Webでmergeし、flat dotted-key、重複/alias/secret/未知/placeholder拒否、16KiB制限を適用。実file属性・env/credential搬送・外部processは未認定。


## 2026-09-25 SnakeYAML Engine 3.1.1（PG272 API非秘密設定）

API Mavenへ`org.snakeyaml:snakeyaml-engine:3.1.1`を明示依存として追加。入手元は[Maven Central](https://central.sonatype.com/artifact/org.snakeyaml/snakeyaml-engine/3.1.1)、設定制限は[project公式説明](https://github.com/snakeyaml/snakeyaml-engine)と導入jarのJava25 `javap`で確認。cache jar `/home/mini/codex/project1/work/toolchain/m2/repository/org/snakeyaml/snakeyaml-engine/3.1.1/snakeyaml-engine-3.1.1.jar` SHA-256 `59d73655cf077f154137e2d6f6f92c041a954c0b1c534c63800047a0d70a6947`。OS package/daemon/secret実体は変更なし。重複key禁止、非scalar key禁止、collection alias0、codepoint上限16384、入力byte上限16384、flat dotted-keyのみの起動前構成とする。再現はJava25/Maven wrapperで同依存を取得後`-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository`を指定し`clean verify`。実fileの権限/identity/credential/env層は後続依存で未認定。

## 2026-09-25 HikariCP 7.1.0（PG271 API/Web DB pool）

Web/API各Maven moduleへ`com.zaxxer:HikariCP:7.1.0`を明示依存として追加。取得元は[Maven Central](https://central.sonatype.com/artifact/com.zaxxer/HikariCP/7.1.0)、設定意味は[project公式README](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)を確認。cache jarは`/home/mini/codex/project1/work/toolchain/m2/repository/com/zaxxer/HikariCP/7.1.0/HikariCP-7.1.0.jar`、SHA-256 `2be45c641b841e81df87292e181f2c203500c5f0e9a1676f135927387f3cf40b`。OS package/daemon/実credentialは変更なし。APIはmax8/min2、Webはmax2/min1、共にconnectionTimeout3000ms、validationTimeout2000ms、initializationFailTimeout正値1msでlazy成功を禁止。実role/URL admission・systemd credential読取・外部process readinessは別依存であり、poolだけでは起動完了ではない。

再現は同Maven依存をCentralから取得後、既存Java25/Maven wrapper・`-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository`で`clean verify`。PTは隔離PostgreSQL18のtemporary cluster/信頼認証を使用し、運用DBや秘密値へ触れない。

## 2026-09-20 Node.js 24.19.0（検索外部JS PT用、導入済・試験組込前）

2026-09-29 PG377再現追補：`ScenarioSearchScriptTest`/`LogSearchScriptTest`は直接`ProcessBuilder("node", …)`を呼ぶため、`-Dnk.pt.node`だけではこの2件を解決しない。Production6の初回clean testはPATHにnodeが無くWebで2 error/Batch not-run、exit1で不認定。固定source `d9a20b97e21227124384e8db32d40083bbca4e35`の再実行では`env PATH=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin:/usr/local/bin:/usr/bin:/bin JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -B -ntp -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch -am clean test`で2,513PT/369suite F/E/S0。全6へ同PATH・JDK・Maven repoで`spotbugs:check jacoco:report`もexit0。今後このdirect JS PTを含むrunではNode binをPATHに明示し、fail/skipを合格扱いしない。既設Node binary/OS PATHは変更していない。018/265/PG377 manifest参照。

07:02追補: PG201選択試験で構文check/Node8case/Production1file全line・function・branch100%が成功、Java wrapper1PTとして実行。正式reactorは未実行。full verify wrapperと006 manifest commandへ `-Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node` を追加し、次正式runから使用する。以下は導入時記録。

入手元はworkspace dependency bundle `26.905.11957` の `/home/mini/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`。PATHにはNodeなし。tool案内で所在を取得しversionを実行確認、Linux x86-64 ELFを `/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node` へ新規copy（`install -D -m 0755`、既存targetなし確認）。元/先SHA256はともに `bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12`。system Node/apt/service変更なし、binaryはGit外。

再現: 同bundleの実行fileのhash/versionを確認し同じ新規pathへinstallするか、既設Node24.19.0を `-Dnk.pt.node=/absolute/path/to/node` でMavenへ指定する。値を省略する場合はPATH上のnodeを使い、存在/version不一致はPT失敗（skipしない）。実運用Javaサービスの依存にはしない。

PG201ではNode組込`--check`、`--test --experimental-test-coverage --test-reporter=tap --test-coverage-lines=100 --test-coverage-functions=100 --test-coverage-branches=100`と明示Production file includeで実行する予定。Node8caseはJavaラッパー1Test IDの内数、二重計上しない。VMのDOM event doubleで実scriptを実行し、実Browser視覚/IT/STの代替とはしない。JSは1Production file全体を対象としline/function/branch100%・対象file実在を照合、Javaの4coverage100%とは区別する。現時点は未実装/未認定。

## 2026-09-20 Caddy 2.11.4検証toolの隔離導入

既存Characterization用2.6.2は変更せず、公式GitHub release APIのlatest=v2.11.4（2026-06-03公開）を確認してlinux_amd64 tarとchecksumsをwgetで取得。導入先`/home/mini/codex/project1/work/toolchain/caddy-2.11.4-pRgVbp/caddy`、表示`v2.11.4 h1:XKxkMTgNSizEvKG6QHue6cAsFOteU2qA61w2tKkCWi0=`。OS package/service/port/CA trustは変更していない。配備採用・template試験完了ではなく、native検証準備のみ。

入手元: [公式release](https://github.com/caddyserver/caddy/releases/tag/v2.11.4)。同release assetsの`caddy_2.11.4_linux_amd64.tar.gz` SHA256=`527fbf917c39189a1e3b31d34fa955601680b2d5c8055d2a87b8b9588dec7bb9`、checksums.txt SHA256=`7bfa272f3ece3ac987c1e06cd3c0acf126749d88110c20d7b83dcea3caaf0080`はAPI asset digest一致。本体SHA256=`b7105518e3ed1c0761f232e44fc09345535533c9cb0abf0e12809416c7ac64d9`。

再現: work/toolchain内でmktemp -dにより新規領域を作り、同versionの2assetをwget -Pで取得。checksumsはSHA512形式なので対象tarの行を`sha512sum -c -`で検証（OK）後`tar -xzf`、`./caddy version`。最初のsha256sum -cはdigest長不一致でexit1、展開前に停止した。形式確認後SHA512で再検証し、checksum無視や既存tool上書きはしていない。binary/archive/生成CA実体はGitへ格納しない。

PG-D-185（2026-09-20）: PT-BAT-110だけ固定4worker・独立PG18.6 cluster/Connectionへ分割。追加tool導入なし、既存1＋追加3のclusterを逐次起動し、各worker終了後try-resourceで全追加clusterを停止する。同一Connection/advisory lockを共有しない。実行機12CPU/RAM15160MiB、/tmp tmpfs7.5GiB・空き7.4GiB（開始前）、project ext4空き162GiB、FD limit524288。実行中swap0、RAM逼迫なし。選択class397.9→178.8秒、単回約55%短縮、全6768 fault位置・期待値・JUnit16を維持。再現commandとhash/制約は017072/073。全JUnit/Mavenを並列化せずMaven1本を維持、正式全reactorは次に確認する。

PG-D-155（2026-09-12）: 既存OSの/usr/bin/getent、Ubuntu GLIBC2.43-2ubuntu2.4を利用（新規導入なし）。実行fileはroot:root0755、SHA256 aa31e99e0818cf40cd6549568397b39e8b907341e715ec733a15842067a45255。配布元はUbuntu libc-bin package。固定`getent group schubert`、PATH=/usr/bin:/bin・LANG=C・LC_ALL=C以外のenvなし、stderr破棄・5秒/65536byte上限、shellなし。再現確認はgetent --version/--help、Linux man-pages6.17 getent(1)（/usr/share/man/man1/getent.1.gz SHA256 de56d08d490d1014e879b0fe65f6e23751b21b74238e905fe2f6abef8164da3b）。当PG/PT hostはschubert group未配備で固定照会exit2、実factoryはこの負例を検証し、正系/opaque fieldは孤立process fixtureだけ。root/group/NSS設定やdaemonを本確認で変更していない。実配備の正系は後続Linux ITで別確認する。

PG-D-147/BUG-142: `com.github.spotbugs:spotbugs-annotations:4.10.4`をBatchのprovided（compile-only）依存へ追加。既存Maven Central cacheのjar SHA-256 `28fa4befaddce5d7b79b07c68e7c12fa27c5d9282c4229528717971606661ea3`、入手元`https://repo.maven.apache.org/maven2/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar`。Java25 javapでSuppressFBWarnings.matchType/EXACTを確認。固定/run移植性警告1件のmethod限定理由記録にだけ使い、runtimeへ配布しない。通常のoffline clean verifyで再現。systemd259.5 tmpfiles.d(5)でfは既存file非truncate、!は--boot時限定を確認し、hostで実行せず固定3行のPTを行う。

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

### 3.2 ShellCheckの作業領域導入（2026-09-09）

専用launcher wrapperのPG/PT準備としてUbuntu resolute/universe amd64のShellCheck `0.11.0-2`（本体表示0.11.0）を`apt-get download shellcheck=0.11.0-2`で取得し、`dpkg-deb -x shellcheck_0.11.0-2_amd64.deb root`でrootless展開した。入手元は`http://jp.archive.ubuntu.com/ubuntu/pool/universe/s/shellcheck/shellcheck_0.11.0-2_amd64.deb`、実行pathは`/home/mini/codex/project1/work/toolchain/shellcheck-0.11.0/root/usr/bin/shellcheck`。OS package登録・daemon・既存toolchainは変更していない。

deb SHA-256 `06990eaf21b5dfa3d855e492f7ca2d6fcacf63b490a73a545850c50cf7af2bce`はapt-cache showの配布indexと一致。binary SHA-256 `311de5f94ecea1d98052ccdc94166591dce89e031e7357debd2f3213b547f7df`、3313918-byte deb。既存libc6/libffi8/libgmp10/libnuma1で`--version`終了0を確認した。download/extractは一時作業directoryで行い、存在しない上記専用directoryへ移動。再現時は同version/hashを照合して展開し、既存toolを上書きしない。実際のscript解析・全分岐PTは次のPG-D-144以降で証明し、導入成功だけをscript品質合格としない。

依存の実測版: libc6 `2.43-2ubuntu2.4`、libffi8 `3.5.2-4`、libgmp10 `2:6.3.0+dfsg-5ubuntu2`、libnuma1 `2.0.19-1build1`。systemd-analyzeはOS既存`259.5-0ubuntu3.4`、更新していない。

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

PG-D-146: /usr/bin/flock --versionはOS既設util-linux2.41.3。/usr/share/man/man2/flock.2.gzはLinux man-pages6.17（2026-02-08）、open-file-description所有・close解除・fcntl非互換・local/NFS/SMB差を照合した。新規導入やhost lock操作はせず、隔離一時fileと子processだけで相互排他PTを実施する。Javaは既存Java25公開FFMで固定libc symbol/ABIに限定し、native-access/解析gateを維持する。

PG-D-144/SSC-053: `/usr/bin/od --version`はOS既設uutils coreutils0.8.0。`-An -v -tx1 -w64`で全byteをASCII hexへ変換する。新規導入なし。PT-OPS-INBOX-002/003は固定receiptの独立byte vector、NUL全位置、変換失敗を検証する。Linux配備では同option/output契約を再確認し、未確認の代替odを推測合格にしない。systemd-analyzeの構文検証は専用一時unit path/ExecStart=/bin/trueだけを用い、OS service・credentialは起動/配布しない。

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

## 追補 2026-09-13 — backup用age隔離toolchain

PG164正式08のsourceを凍結したまま、後続FND-R004用にUbuntu配布age 1.2.1をworkへ隔離展開した。今回08のMaven/PTでは未使用であり、環境導入だけをbackupのPG/PT合格にしない。OS package構成・global PATHは未変更。GNU tarは既存1.35。

- Catalog: Ubuntu resolute/universe、amd64、age=1.2.1-1build1、size1,884,068、libc6>=2.34。apt-cache policy/showで導入前の未導入と候補を確認。
- 配布: [Ubuntu package](http://jp.archive.ubuntu.com/ubuntu/pool/universe/a/age/age_1.2.1-1build1_amd64.deb)、[upstream固定manual](https://raw.githubusercontent.com/FiloSottile/age/v1.2.1/doc/age.1)。
- 隔離先: /home/mini/codex/project1/work/toolchain/age-1.2.1。既存不存在を確認してmkdir、そこでapt-get download age=1.2.1-1build1、sha256sumを下記catalog値と比較後だけdpkg-deb -x age_1.2.1-1build1_amd64.deb rootを実行。
- package SHA256: b6994be61dd9880456c36c13da5392ee4ab406763152cd86e33e430676aa8fb9
- root/usr/bin/age: --version=1.2.1、SHA256 00c07670d548aa01705923fbbecbcd6edb76a65bd73e1b5644fad0c4a60bf678。
- root/usr/bin/age-keygen: SHA256 0cadbef602a8849c9522869ff4007e66df1ec1cd00bc1e7c0b6ab2f08a95643d。
- 後続PTは公開合成dataと一時生成鍵のみを使用し、秘密key/dump/plain archiveはGitへ保存しない。実recipient fingerprintは配備時の非秘密manifestへ記録し、この導入時に本番keyを生成していない。
- root本番導入・更新時の再検証とrestore rehearsal、NAS適合/実子の終端確認は未実施。作業整理はwork/PGPT_R004_backup_artifact_design_draft.md。
## 2026-10-10 PG1127/1128 退役Backupの非変更ディスクからの私有保全

Production依存ではないoperator専用Python読取環境を `work/toolchain/dissect-backup-readonly-20261010/runtime` に隔離。公式PyPI wheelをversion/SHA256固定で取得し、全download314781byte。system/guest/package設定変更0、AGPLライセンスを含む工具をProductionへ組込み0。host Python3.14.4、導入再現は `python3 -B tools/quality/vm/050_s1/pg1127_prepare_disk_reader.py`（既配置には再導入しない）。manifest SHA256 `8b94e5b77a74ff9ea1402152815de92761f81a8b44fb723bd2320a9ae113fea3`。

| package | version | wheel SHA256 |
|---|---|---|
| dissect.hypervisor | 3.21 | fd845a3e7bc20efca575d4cfbb49a21ca53e8d89efb8afeec180de8a6b62fd2f |
| dissect.volume | 3.18 | f8f321adccacbd948c503cf14a14d4a6626d1b86ddcbe55c532b59caad833d79 |
| dissect.extfs | 3.15 | 9c67e64552eedc58ecbbdda82287a6c8fbf8b29d99a7b55073d838233d6dfcab |
| dissect.util | 3.24 | 031f91d7523818a3aced4d17594996bcc39bc4d93ffacc0b15a7b718c9b437cb |
| dissect.cstruct | 4.7 | 0427621ce67baa3106df2dc63a320d0a7f5c2da88ba3faf2ef5886a1a6b458fd |
| defusedxml | 0.7.1 | a352e7e428770286cc899e2542b6cdaedb2b4953ff269a210103ec58f6198a61 |

参照はPyPI公式各version JSON/固定wheel URL、[hypervisor公式](https://github.com/fox-it/dissect.hypervisor)、[API公式](https://github.com/fox-it/dissect-docs/blob/main/docs/source/advanced/api.rst)。QCow2のabsolute backing自動解決を用いず、保持baseとcloud backingの各rb handleを明示結合→GPT root partition→ExtFS inode読取。新VM・mount・device attach・full raw disk copy・snapshot適用0。

PG1128 commandは上記runtimeをPYTHONPATHへ指定して `python3 -B tools/quality/vm/050_s1/pg1128_preserve_retired_backup.py`。一回実施済み、再実行/上書き禁止。旧原本の5entry metadata/四file hashを保持beforeから独立照合、11420273byte/4fileを私有700/600へ保存。manifest SHA256 `511b28d0358d2573cbb1cbb145c04c8ccd3a3bd28d9fd189f91742ba5ff295e4`。元image/backing identityは前後同一、事前認証済みdisk全SHAを今回再測定したとは記録しない。現在VM/DB/Backup変更0、秘密内容/DB dump/暗号credential/file本体はGit外。PG1129はこのpin・file hash/size・link/modeと9field安定性を再照合、atimeを安定性へ混ぜない。PG/PT正式加点0。


## 2026-11-06 CSS静的資源PTの専用parser（BUG2350/YKT2095）

Python host3.14、専用directory `/home/mini/codex/project1/work/toolchain/css-contract-parser-1.4.0/site`。global環境/POM/browser/Java依存不変更。新規pure wheel二つをofficial PyPI metadataのSHA256で検証後、absolute/.. /symlinkを拒否し専用siteへ展開。setup/build scriptは実行しない。

- tinycss2 1.4.0 / https://pypi.org/pypi/tinycss2/1.4.0/json / wheel SHA256 3a49cf47b7675da0b15d0c6e1df8df4ebd96e9394bb905a5775adb0d884c5289 / https://files.pythonhosted.org/packages/e6/34/ebdc18bae6aa14fbee1a08b63c015c72b64868ff7dae68808ab500c492e2/tinycss2-1.4.0-py3-none-any.whl
- webencodings 0.5.1 / https://pypi.org/pypi/webencodings/0.5.1/json / wheel SHA256 a0af1213f3c2226497a97e2b3aa01a7e4bee4f403f95be16fc9acd2947514a78 / https://files.pythonhosted.org/packages/f4/24/2a3e3df732393fed8b3ebf2ec078f05546de641fe1b667ee316ec1dcf3b7/webencodings-0.5.1-py2.py3-none-any.whl

087_install_css_parser.pyとpublic PG20698 toolchain-manifestにsource/全展開file hash/actual日時/Python/reproを記録。再現は同じwheel hashを検証して新しい専用siteへ展開し、`PYTHONPATH=<site> python3 -B .../029_media_css_contracts.py metadata <newOutput>`。実使用tinycss2 1.4.0/APIを独立metadata5件で検証、web docs requestedv1.4 URLは取得時1.5.1表示なのでその版を導入済と誤認しない。parseは構文層のみ、property意味は独立Current62値で比較する。media/master/DB/鍵/VMへaccess無し、実Browser/IT-ST代替ではない。


## 2026-11-06 現1844 Architecture再利用

既ArchUnit1.4.2/SLF4J2.0.18・JDK25.0.4/ModuleDependencyAudit source108e8をそのまま使用し、normal20704六JAR1844を静的import、五規則0/初期化0/独立post0。旧1669/11canaryは歴史参照で再演0。新observer compileと旧保存classの全byte一致を確認。新tool導入・Production POM変更無し。版/入手元/hashの旧記録は保持、再現command/現ソース/結果/範囲は018仕様3594・結果3595/PG20808/20810。全F02/正式451・PT/coverage受入の意味は拡大しない。


## 2026-11-06 独立AES-GCM public oracle（PG20902/20926）

既存host Python 3.14.4 / cryptography 46.0.5 / OpenSSL 3.5.5 27 Jan 2026を利用、導入操作無し。実install入手元は未検証でPyPI由来と推測しない。007/evidence/PG20926へmodule/Rust binding path・hash、version、取得元未確認、再現commandを保存。007/input/013は実施済みinline generatorと同等の再現用sourceを後保存したもので、元source凍結済みと称さず、暗号計算の再演はしない。新規導入が必要なら隔離venvへ同versionを承認済み検証済み入手元から導入する。PUBLIC zero32 key/固定nonce/ASCIIa64/三synthetic ownerだけで、実credential/鍵ファイル/DB/Root無し。既定nonce安全性・実運用鍵/全toolchain provenanceを合格にしない。元golden manifest 19e53c2f86c9dc391b733f1a53621c50d40e98920bbf8e9fbf404a6bea4bbb5cは不変更。

### 2026-11-07 公開SDK mode値の独立参照（追加導入・設定変更なし）

PG22826/22828/22834はhost既設`linux-libc-dev 7.0.0-42.42`、`libc6-dev 2.43-2ubuntu2.4`の公開`/usr/include/linux/stat.h`と`/usr/include/x86_64-linux-gnu/bits/stat.h`をread-onlyで使用した。入手元は当hostの既installed distro SDK packageで、今回download/installはしていない。Versionは`dpkg-query -W -f='${Package} ${Version}\n' linux-libc-dev libc6-dev`、原headerのhash・各site/値の独立式はOPS018 PG22826 manifest/PG22828 integerValueWitnessesに固定する。

再確認は同commandとheaderのS_IFMT/S_IFREG/S_IFDIR/S_IFLNK/S_IRWXU等の定義をread-onlyで照合する。これはtarget guest/kernelやnative syscallの実測ではない。元Test compile/run/Root/VM/権限操作はHOLDのままで、再現の名目で実行しない。JDK25.0.4/既PMD7.28 patch/Checkstyle14.3/GJFとルールのversion・設定は不変、元source/失敗/成功manifestを上書きしない。


2026-11-14 SSC365: JSR3053.0.2の既ローカル公開artifact（com.google.code.findbugs:jsr305:3.0.2、既provided spotbugs-annotations4.10.4のcompile推移依存）を閉鎖scopeのannotation classpathへ明示SHApin。新download/install/Production POM/GAV変更無し。四final COPY型の既deep-immutable契約をjavax.annotation.concurrent.Immutableで宣言し、method/Test body/解析rule/filterを変えずPG31564 rawSpotBugs-Missing-error0と全403で検証。artifact/POM path/version/hash・再現commandはPG31536/562manifest及びI2760profile。class注釈だけを不変性実証やPT合格へ読み替えない。


## 2026-11-15 SSC411 公開annotationを含む限定SDK

Java25.0.4/Maven3.9.12/Root NullAway0.14.1・ErrorProne2.50.0、lint-all/Werrorを維持。初期ADMINの新しいメモリ内JDBC単体試験は既m2のspring-security-crypto7.1.1・commons-logging1.4.0を使用する。crypto公開APIのorg.springframework.lang.Contract依存は通常jdepsのcode参照/POMだけでは不足するため、既reactor採用spring-core7.0.9（/home/mini/codex/project1/work/toolchain/m2/repository/org/springframework/spring-core/7.0.9/spring-core-7.0.9.jar、SHA256 5195f4722699b39878d99a832549fe65df2890b159d063b88fff31b1ca65ae36）を明示classpathへ含める。今回の新規download/導入/role変更は0、入手元は既構築toolchain/m2、取得履歴未確認を今回取得として記載しない。Contract.classは元jarの既entryを確認し抽出代替jarを作らない。

再現はclosed host profileの明示5Main/6physical/SDK exacthashに従い、新しい未使用phase namespaceを作ってprestyle→prepare（Root NullAway/lint-Werror）→static→preflight→固定Unit→post/無filter一exec測定を行う。既phaseの再発行/原証跡上書きはしない。PG33442のMain compile1とPG33458 proc-none診断は品質合格ではなく保存、PG33464はMain Rootcompile0/Testcompile1（JUnit expectedClassの型推論）で未資格。修正後の正規fresh profile3312/PG33484へ追跡する。全SDK SHAは各profile、補正根拠はPG33460/BUG2986/YKT2515、当source/元SQL/期待値を変更せず、抑制/品質緩和0。actual DB/bootstrapMain/credential/native/RootActual4/HOLDは未実行。


2026-11-15 SSC417 source段: 2026-11-15、dev-foundation、source前HEAD7b2f17f40bfff283913a30a6fe4ab8329d9d8031。実行環境/時刻/command/exit/hashはPG33710/source-only-checks-v2.json、独立source判断はsource-only-review-v2.json。整形GJF1.36.1とCheckstyle14.3のJava source parseは終了0・指摘0。旧途中結果も保存し、新24Testを一度も起動していない。

SDK ABI/compile、NullAway、SpotBugs、semantic PMD、全体build、動的PT24、実Driver/DB/nativeはNOT_RUN_HOLD。line/method/class/branch/instruction coverageはすべてnull、PASS数0。旧Coreef461eba/Unita48eec60の全1050は新POM変更前の歴史資格として保持し、新port・新POMへ流用しない。旧105Java source byte不変はレビュー済みだが、新依存グラフ全体の受入を意味しない。

BUG3001/YKT2530は表示escape誤読による誤検知取り下げ、source修正実績0。BUG3002/YKT2531はfuture fixture初期化順をsource是正し型compile/PT待ち。BUG3003/YKT2532はowned capture後の幅検査へsource是正、未来PGCOPY005を追加し、既4Mainの非該当根拠をsource-only水平確認、動的未完OPEN。BUG3004/YKT2533の誤った旧vector異常前提は原・現同値正例と独立合成負例で是正、metadata source review限定で閉鎖し製品PT成功に数えない。

価格1/3/8pp cap9はこのsource製造・PT source・強化レビュー段のみ。未実行SDK/PTの残工数を0としない。後続費用は元P019/全451費用に含む未確定内訳として保留、追加二重課金0、今回段完了を工程完了/工数完成率に換算しない。正式1964PT/53scope、正本184/625、元190新0、工数率nullを維持。

2026-11-15管理工具限定: coverage.py7.17.3 pure wheel219999byteを公式PyPI固定metadata→files.pythonhosted.orgから取得、SHA25621745c08f2835b847a16887b748d3084dddeb0571ae2a0d62e33644413568b99を照合しwork/toolchain/coverage-7.17.3/runtimeへ隔離展開。global pip/SDK導入なし、取得再現3434、URL/hash/時刻/設定はPG33720/coverage-toolchain.json。Python3.14.4、当pure metadata helperのbranch/lineだけ測定しJava/PT/451へ流用しない。vendor attestation自体は未検証。
