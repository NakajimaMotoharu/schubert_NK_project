# Caddy client・Login form・Spring filter接続探索

2026-09-08 JST/dev-web。PG-D-105/PT-WEB-082～089、実装前仕様a7118c6。FUN-001/AUT-001～004、UI226/232/234、SS313/314/342/352。421既存Java25.0.4/Maven3.9.12/Spring Security7.1.1/Session4.1.1/PostgreSQL18.6、追加tool/dependencyなし。421記録のrelease sourceからAbstractAuthenticationProcessingFilterの公開setAuthenticationConverter/custom strategy/saveの順を確認した。別AuthenticationFilterの無条件changeSessionIdや標準UsernamePasswordAuthenticationFilterのString credentials/標準raw-session detailsは使用しない。

| 探索 /tmp/PT-WEB-form-filter- | 終了JST | 結果 | raw log SHA256（raw非格納） |
|---|---|---|---|
| explore-01 | 23:34:57 | Spring例外cause overloadのnonnull契約2件、compile失敗/PT未実行。BUG066、非合格 | e505bc8ec5b1107285a560c9580470ad7cabbeebccb2e7cfb1f94d777a0dd8b8 |
| explore-02 | 23:36:47 | 新8＋既存13=Web21件PASS、新5class＋匿名framework subclass全coverage100%、静的解析0 | 77500b4eeea148a4d386971449b97603230c7b99c4a03602e2652226ad8ea7fe |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=SessionFormLoginTest,SessionSecurityContextTest,MqAuthenticationProviderTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

01はMqAuthenticationProviderTestを除く。探索累積coverageは正式の代用にしない。

## 独立期待・実接続の範囲

Numeric IPv4/IPv6 peerとclientを明示fixtureで対照し、loopback transport peerだけを信頼。XFF/proto単一、https、Forwarded混在拒否、null/空/重複/hostname/zone/chain/Servlet故障を検査する。ResolverはIP責務だけであり、全requestの前段filter、authority/外部origin、CaddyによるForwarded除去、UTF8 filterの配置は後続gate。Forwarded wrapperでremoteを先に変えてからresolverを呼んではならない。

Formはbody単一fieldとUTF8/Content-Type/charsetを検査し、query側の同名username/password/_csrf・encoded名、不正query keyを拒否。Servlet temporary String以外にpasswordを保持せずchar[]をproviderへ消費移管する。NFC/trim・64byte username（İ×32）/password1..256byteは既存clientへ接続し、257byte/control/trailing spaceはMQ送信0を確認。標準WebAuthenticationDetailsやraw Cookie/session IDを作らない。

実SessionRepositoryFilter→SecurityContextHolderFilter→CsrfFilter→実AbstractAuthenticationProcessingFilter/具体MqAuthenticationProviderを、隔離PGとUI232/234手書きoffset合成JMS応答で接続。CSRFは別session/欠落/不一致でMQ0、0000/0200・USER/ADMINはstrategy→save→handlerの順、新ID/CSRF更新は一度だけ。SavedRequest/token移管と次GETの同一principal復元、旧row消失、ThreadLocal clearを確認。

Bad credentials/lock0・900/9000/通信/replay失効/form/proxy/DBを分離し、成功Cookie/権限付与なし。status/Location/Retry-Afterは明示PT callbackで検査するもので、最終production failure/success handler・画面・監査の完成を主張しない。DB commit faultと最後のfilter save failureは503/no CookieとDB旧匿名rowの保持を確認。非Login/GET/HEADは一回だけ下流へ渡し、controller/各handler例外時もHolderをclearする。孤立した本chainの下流はURL認可をまだ実装しておらず、保護URLの認可合格には数えない。

100並行Loginはusername/password/contextとUSER/ADMINを独立させ、8workerでMQ上限12以内、各new Cookie/CSRF・旧row失効・DB100件・pending0・buffer消去を検査。Fixtureのbyte sequenceが200回発行で周回する影響を避け、この試験だけ本物SecureRandom/UUID supplierをpackage-levelの公開注入契約へ渡す。実装のrandomを弱めず、private reflectionなし。

## BUG066/YKT058 全対象

| 対象 | 修正・非該当根拠 | 再発防止 |
|---|---|---|
| CaddyRequestRejectedException | Springのnonnull二引数causeへnullを渡す呼出をString-onlyへ修正 | PT082/083/085/087、固定message/cause null/suppressed空 |
| LoginFormRejectedException | 同上、静的解析抑止なし | PT085/087、型/charset/query/null等の固定診断 |
| MqLoginLockedException | 既存String-only constructorで非該当、0..900秒だけ保持 | 既存PT063/066、新PT087 |
| MqAuthenticationProvider | BadCredentials/AuthenticationServiceは既存String-only、元cause非保持で非該当 | 既存PT064～067、新PT084/086～089 |
| EncryptedSessionAuthenticationStrategy | 既存String-only SessionAuthenticationException、非該当 | 既存PT072/075、新DB故障PT087 |
| MqLoginExchangeException/他RuntimeException直接継承 | Java Throwable自身のnullable cause契約、Spring overloadと異なるため変更しない | 既存client/暗号/DBの固定診断negativeを正式全回帰 |

de9b73fで修正前起票。全対象の修正または非該当根拠と独立再試験を記録し、検索だけで完了扱いしない。上位仕様/Current baseline/正常oracle不変更。

## 正式gate

正式PT-WEB-20260908-14、source57efcbbc8f5c11f6140c63a0f23cdba18c48c2b5、23:38:50～23:43:21 JST。root clean verify全714件（Protocol80/Storage34/API394/Web165/CHR41）、Web001～089、failed/error/skipped0、5対象module line/method/class/branch100%、NullAway/Enforcer/format PASS・SpotBugs0、全7collector成功。BUG066/YKT058の全対象再試験完了。CHR41はrunner単体試験で実NK互換ではない。最終HTTP handler/監査/logger固定/entrypoint/URL role/全request Caddy・encoding・security header、Logout/全画面/実API/JMS/実NK CHR、IT/STは未完了。
