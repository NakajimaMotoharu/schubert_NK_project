# NK-WEB-002 Web依存接続単体テスト仕様書

PG221、RD SYS-001/002/004・MQ-001/002・AUT-001・TST-001～005、UI211/212/231/252、SS311 §5/321 §4/342 §4、YKT-154/162。対象`WebDependencyReadiness.verify`。WebをHTTP readyとする前の技術DBおよび承認済みreply宛先へのArtemis接続だけを検査する。JMS consumer生成成功はQueue実在証明ではないため、SS321 management APIによるAddress/Queue実効設定readinessは別必須gate。WebApplication親、role/credential取得、Log replay、実NK CHR-L01は別未完了。

| Test ID | fixture・入力/操作 | 独立期待値 |
|---|---|---|
| PT-SCR-113 | 隔離PostgreSQL18/Flyway schema・Web role、SS321 `broker.xml`の組込みArtemis、実JMS connection。verify | DB接続の`isValid(2)`と固定reply宛先のJMS context/consumer生成が成功。Queue存在・権限・実効設定の証明とは区別。message送受信・DB更新・credential出力はしない |
| PT-SCR-114 | null DataSource/factory、DataSourceがnull connectionまたは`isValid=false`を返す | nullはconstructorでfail-fast、DB異常ならJMSへ進まず固定`WebStartupException`。例外文に秘密値なし |
| PT-SCR-115 | JDBC取得/検査/closeのSQL障害、JMS context open/consumer attach/closeのprovider障害 | 起動失敗。JDBC/Artemis provider本文・credentialを外部例外へ出さない。取得済資源はcloseする |
| PT-SCR-116 | broker未起動、SS321固定reply宛先literal | provider接続が失敗した場合は固定messageで起動拒否。Queue欠落をconsumer生成だけで検出したと主張しない。Queue実在は後続management gateで独立検査 |

実行command/JDK・OS/source commit/終了code/coverage/実結果/関連障害/証跡path・SHA-256は正式run後の030へ記録。失敗/skip/flakyはPASSへ含めず、全Java4coverage・静的解析・全41scopeで認定する。検査が成功してもProduction credential/readiness全体やIT/ST完了を意味しない。
