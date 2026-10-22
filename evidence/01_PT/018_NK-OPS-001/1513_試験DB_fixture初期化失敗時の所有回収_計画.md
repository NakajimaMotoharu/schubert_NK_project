# 試験DB fixture初期化失敗時の所有回収（実再現前）

BUG1633/YKT1386、既Web BUG552/YKT396を参照。SS354/451の資源後条件と開発環境規約の内部実装判断であり、Production DB/SS仕様の変更ではない。全Main/旧Test assertion/build/gatesを固定する。対象変更はbatch/Bootstrapの二Test fixtureと新各三Testだけ、旧Web FixtureTest三件は同source回帰する。

予定PT_DEFAULT scopeは毎caseの自己生成@TempDir、既PostgreSQL18 binary、loopback・新ephemeral port・trust合成role/production DDLの専用clusterだけ。原本DB/実配備/VM/Root/cohort/Backup/鍵/credential/permit/Unit・失敗cohort回収には触れない。constructorへtest-only repository引数を追加し、public既定入口は元propertyを読む。全体propertyを変更せず、他classのfixtureへ干渉しない。

| Test ID | 独立期待値と後条件 |
|---|---|
| PT-DBFIX-1633-B01/A01 | null/empty/blank repositoryは固定IllegalArgumentException、initdb/start0・TempDir空。 |
| PT-DBFIX-1633-B02/A02 | 自己生成repositoryのprovisioning/001_roles.sqlにSELECT 1/0を固定。known start0後SQLSTATE22012、元SQLException/正常stopならsuppressed0、当dataDir/postmaster.pid無し。旧実装redで残る場合だけ当TempDirのPID・command/dataDir一致を確認して通常pg_ctl fast stopし、結果は失敗のまま保全する。原本/他jobのPIDや旧sessionは使わない。 |
| PT-DBFIX-1633-B03/A03 | 通常fixtureで各schubert_batch/schubert_appへ接続、DDLの全24表を独立SQL後条件で確認。明示stop0後PID file無し。 |

wrapper/stopは各command30秒以内、raw logは当private TempDirだけ、Gitへはredacted XML/manifest/hashと検証結果のみ保存する。停止の失敗/所有不明は成功化しない。constructor ownership公開前の負経路を先に実証してからcatch/stop/元例外・割込保全へ是正し、同oracle bytesのgreenと関連fixture再試験を行う。新Test数は六method/二suiteでありnull三vector等を件数へ足さない。必要全体は関連変更群と束ね、同成功確認の全回帰反復をしない。

着手前予算の候補.4/1.2/3pp。481/484実leafの責務照合から、主をWBS-F02（6module buildを支える試験用toolchain/fixtureの内部依存）へ確定する。初稿の仮F03は静的gateそのものと異なり訂正、Root未分類11の迂回/受入に使わない。他対象/後続全回帰K01.01へ準備費を重複計上しない。新発見の内部品質依存として記録し、原見積/v4・完成率を減額/加算しない。現時点は仕様準備・静的発見のみ、当実再現/修正/新PT0。F03/正式/canonical17/工数null/全実環境HOLD/PTALT代替0は不変更。利用枠fresh>10%と前群原資格の保存後に着手する。
