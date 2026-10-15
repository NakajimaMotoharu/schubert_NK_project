# Broker設定全scope独立照合仕様・結果

WBS-C04 / NK-OPS-001 / MQ-011～013 / UI231 / SS321。対象は`src/deployment/artemis/etc/broker.xml`一件のみ。正本RD131/SS321はfresh origin/mainと全文同byte（SHAは公開PG3392 manifest）。新Main/設定の製造や成功済みRoot/Broker起動を行わず、実四methodの原3372結果と設定・schemaを照合する。全体正式受入ではない。

## 対象・独立期待値

SS321 §2～5/10/SSC075076から、global24値、六Address/ANYCAST/Queue、各26policy値、十三ACLの全role/permissionと未列挙拒否をliteral oracleへ転記。`pg3390_broker_config_oracle.py`はProductionの定数/encoder/parserを期待値生成へ呼ばず、XMLを独立に読む。global要素数・全policy/ACL重複・余分/欠落・6Queue順/属性まで検査。durableは固定Artemis2.56.0の実parseでtrueを確認し、設定schemaの既定値を固定依存とともに検証する。

| 一意Test ID | 実入力/操作・期待値 | 実結果/証跡 |
|---|---|---|
| PT-CFG3390-A | 原3372 `ArtemisBrokerConfigurationTest#globalBrokerAndJournalSettingsMatchTheIndependentOracle`、SS321 §2/3の全明示globalとjournal | 原JUnit成功、元XML SHA87fe6cf1c81bf9a1623ca3f290cc5f135031f3533b69ece4bf695460c8506370 |
| PT-CFG3390-B | 同`#topologyAndTransportAreClosedToTheApprovedSet`、六durable ANYCAST/固定queue/loopback CORE一acceptor | 原JUnit成功。XML4ケースは新PTに加点しない |
| PT-CFG3390-C | 同`#addressPoliciesMatchTheIndependentCapacityMatrix`、SS321 §5.1～5.4/QA041042の全六容量・1/5/25・PAGE/FAIL/BLOCK/auto false | 原JUnit成功。閾値のIT性能合格は非主張 |
| PT-CFG3390-D | 同`#securityRolesMatchTheIndependentAclMatrix`、SS321 §10/SSC075076の全十三ACL/role、durableQueue create/delete無し | 原JUnit成功。従来DisplayNameのPT-JMS-002はB/Dで共有されるため、この表ではclass#methodと異なる一意aliasを使う |
| PT-QUALITY3390-001 | 公式固定2.56.0 JarのXSD/xml.xsdを抽出、JDK25 secure JAXPで元coreを前後validate。未知要素/journal不正型/数値不正/boolean不正の四独立DOMだけを変更 | compile0/full lint/Werror、実exec92422 actual0/run0。正常前後合格・四SAXParseException拒否。原XML変更なし・Broker start0 |
| PT-QUALITY3390-002 | 全24global/6address/6×26policy/13ACLを独立literal照合。別copyに外部0.0.0.0 bind、再配送5回、APIへの不許可send付与 | 正常維持・三反例すべてValueError拒否、元木の再照合一致。source/設定を書換えない |
| PT-QUALITY3392-001 | 原3372 wrapper/Maven0/3706、configとTest input/source/hash・原XML4/FES-flaky-rerun0、現artifact/a9、schema Jar hash、全前後inputのjoin | pg3392 collector exec26249 actual0、公開manifest35fe251ae838ec4c27be401d244b80b9c459a599bb6b020a1e20a4ceda09645d |

## 要求責務と終了依存の境界

- MQ-011：本設定はCORE acceptor/固定Queueのみを定義し、Java serialized objectを設定・電文へ埋込まない。Body型の禁止はAPI `JmsMessageGuard`、Web `JmsReplyDecoder`のBytesMessage限定境界とsender側のBytesMessage生成（別Pの責務）へ明示参照する。C04だけで全app Body/業務互換の受入を主張しない。設定からRMI/Object RPCや別protocolを追加していない。
- MQ-012：当外部XMLに接続先/Address/Queue/閾値/timeoutを定義し、credential実値を含まない。個別接続factoryのcredential/timeout/profile読取り・LoadCredential/認証は別owner、同費用を本設定監査へ再課金しない。例外・欠落・未知parameterは当XSD/全許可値oracleで拒否、実connectionの再送・並行はこのnon-executable artifactのscope外として別PTへ残る。
- MQ-013：当acceptorは127.0.0.1:61616/COREのみ、追加acceptor0。管理console/Jolokia/Unit/Caddyのbindと実socketはC05等の別設定/実native gateであり、C04でインターネット到達性/ITST完了を宣言しない。自身のbindを外部へ変えた独立反例を拒否できる。

C04のownedArtifactsは上記XML一件、sharedClassReferences/終了dependencies/childrenは空。設定自体にJava/JS executable classはなく、line/method/class/branchは非該当。既849Java/1643Mainをcoverageから除外する意味ではなく、global601L115M0C466BとF03の未分類PMD2220/Checkstyle645は未完のまま維持する。本設定のXSD/実parse/独立全許可値・負系が該当品質条件である。

## 実行環境・再現・保全

原四JUnitはPG3372 fixed6b98f5930/source a9、Linux7.0.0-38-generic/JDK25.0.4/Maven3.9.12/Artemis2.56.0。四method/全source/exit/hashはPG3392公開manifest、原XML/ログはaru runs/PG3372-six-v1。元Maven全回帰を再実行せず原完了証跡をRO参照した。

schema/private outputは`work/pgpt-runs/PG379/pg3390-broker-schema-v1`、Java helperは`tools/quality/vm/050_s1/ArtemisConfigurationSchemaCanary.java`。固定Jar SHA4bc0bb2d74e340fbb54d84121f2c52708e00bdad0a84751b9bd4f4b21e03c358（aru同byte）から二XSDをnew-onlyで抽出。固定JDK25 `javac --release 25 -Xlint:all -Werror`、`java -cp <classes> ArtemisConfigurationSchemaCanary <broker.xml> <xsd>`。公式schemaは同隣接file importのみ、外部network/DTDを解決しない。controlled stdoutとraw log/hashを保持する。

`python3 -B tools/quality/pg3390_broker_config_oracle.py`、`PYTHONPATH=tools/quality python3 -B tools/quality/pg3392_broker_contract_collect.py`。後者はnew-only output、原source/key/XML/propertyの必要非秘密値だけを収集し、原property全体/stdout/credentialを公開しない。最初のRO調査で便宜上`failed`と出した値は全child要素数であり、実failures数ではなかった。正式collectorはfailure/error/skipped/flaky/rerunのtagだけを明示計数し全0、system-outを失敗とも成功数とも加算しない。

関連未解決BUGは当一設定scopeには発見なし。独立反例は私有copyへの意図的negativeで障害起票対象ではない。C04個別レビュー適用・strict前候補後auditは本結果保存後に別実行し、適用前は未受入。正式1964PT/53scope、個別16/190、工数率null、QA051final保留をこの文書作成だけで更新しない。
