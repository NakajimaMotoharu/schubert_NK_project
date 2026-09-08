# Spring Login provider・現在context確認探索

2026-09-08 JST/dev-web。SSC-043/PG-D-102/PT-WEB-060～067、先行仕様6d68f35。FUN-001/AUT-001～004/MQ-004、UI226/232/234、SS314 §3.1/324 §6.1/352。JDK25.0.4/Maven3.9.12/Spring Security7.1.1/JMS Artemis2.56.0/JUnit5.13.4/JaCoCo0.8.15。追加tool/jarなし。421既存toolchainとlocal Maven release jarのjavapでAuthenticationProvider/UsernamePasswordAuthenticationToken/各例外の実APIを確認した。

| 探索（/tmp/PT-WEB-provider-） | 終了JST | exit/結果 | raw log SHA256（Gitへraw非格納） |
|---|---|---|---|
| explore-01 | 22:29:05 | 0、新8件＋Login6件PASS、新4class100%・静的解析0。SessionPrincipal変更classの全再試験は02へ | 4c54f13c3e0db295f9e187215e12edc09715be04b44aa9aa91484d4d86888f8d |
| explore-02 | 22:31:14 | 0、新8件＋Login6/属性7件PASS、新4class＋変更Principal全coverage100%・静的解析0。100並行を独立password/role/contextへ強化 | 9bd1152ebe047e26fde25b1fc702720c2607a602ed630174a33a72555094cb0d |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=MqLoginContextProbeTest,MqAuthenticationProviderTest,MqLoginClientTest,SessionAttributeCodecTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

探索01はSessionAttributeCodecTestを除いたcommand。新規BUGなし。正式はclean verifyで全module/既存APIを含め、探索の累積coverageを合格へ流用しない。

## 独立期待・実装判断

IF-003期待wireはUI232/234 offsetを手書き配置。GAMREQは256byte/contextあり・DATA0・新UUID、GAMRSPは265＋272×0/1/10byte、DATA Total countと各Game code/Title/order/Reservedを検査。Source metadata/encoderをexpectedへ使わない。応答layout/correlation/context/全長/record境界/順序/不正UTF8と不正error fillerを対照する。元Login snapshotの初回expiryが過ぎても現在API idleは延長され得るため、0200は新IF-003成功を正として確認し、元日時から現在認証を推測しない。

Providerは0000のUSER/ADMINまたは0200＋正常probeだけを認証済Spring tokenへ写す。SessionPrincipalはjava.security.Principalを実装し、getNameはusername、toStringは従来どおりredacted。DB JSON/allowlistの形式は変えない。0101/入力不正、0106、9000/通信を分離、lock秒0..900だけ公開。元wire userMessage/診断causeは例外へ保存しない。char[]を消費・zeroし、標準input tokenのcredentials参照をeraseする。型不正/null/既認証/非対象classも検査し、Caddy由来IP信頼をnumeric型だけで成立したとは扱わない。

100並行providerでは異なるusername/password/USER・ADMIN/contextを与え、Login100＋probe100で200 fresh UUID、各返却identity/秘密消去/pending0を確認する。公開monitorをcallerが保持しても進む。Probe単体も100異なるcontextを確認する。HTTP/DB保存はproviderに存在せず、custom fixation strategy/SecurityContextRepository/handlerは後続gate。

## YKT-056 残対象の確認

既存Login/Media/JMS decoderはlogin-exploration.mdの全対象表と正式Web10で確認済み。残るMqAuthenticationProviderに実MqLoginContextProbeを接続し、PT065で0200→新GAM成功だけgrant、0102/9000/不正/通信障害はgrantなしを確認する。確認後も業務ごとのAPI最新認証を省略しない。API AuthenticationContextVerifierのUser→session lock/ACTIVE/revoked/expiry/最新roleと、UserCommandServiceのrole/status/password変更時全session失効は既存実PG PTを正式全回帰する。ゲーム応答を利用者へ表示したり永続cacheへ保存しない。

## 正式gate

正式PT-WEB-20260908-11、sourceb295b3153056a6dc87eb6c76052e725dfc44f395、22:33:30～22:37:56 JST、exit0。全692件（Protocol80/Storage34/API394/Web143/CHR41）、Web67件、新8件を含めfailed/error/skipped0。全5対象module line/method/class/branch各100%、NullAway/Enforcer/format PASS、SpotBugs0。全7collector/manifest/hash更新。SSC-043/YKT-056の当該provider範囲と全既存API認証・管理失効非回帰を完了、新BUGなし。最終chain/HTTP handler/fixation保存/Caddy trust/全layout登録・API実起動/実NK CHR、IT/STは未完了。
