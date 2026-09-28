# NK-OPS-001 親Backup所有値受渡し単体テスト仕様（PG377）

対象 `MorningBackupStage.executeOwned`と既存`execute`互換。RD OPS-009/BAK-001、UI251、SS341§5–6/343§6.15、SSC092/094/104/105/107/108、471 R1/D04/05。Production source変更前に作成。`OwnedWork`はpackage内で、同M/A/原本/DB callbackに限り`MaintenanceRunState`、同`MorningDatabaseSession.Access`、公開済み`BackupWorkerRequest`、committed両`BackupBegins`、同じpart UUIDを借用する。これらの値だけでUnit start/retire・許可発行を承認しない。

| Test ID | Fixture・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MBSTAGE005 | 固定run/activation/part、所有中flag付き合成Scope/DB、固定UTC Clock、publisherを用い`executeOwned` fresh | 固定順M/A enter→両DB begin commit→同part request publish→所有中のwork→close。workのstate/DBは同scopeからのidentical object、request.run/part/stepはfixture literal。借用値はscope外で成功利用しない |
| PT-OPS-MBSTAGE006 | recover=trueの同fixture | DBへtrueが一度渡り、state/partが改変されない。既存`execute`の二引数workも従来順で稼働 |
| PT-OPS-MBSTAGE007 | DB begin失敗又はrequest publication失敗 | OwnedWork呼出0、scope close1、原因を成功に変換しない。外部Unit起動0 |
| PT-OPS-MBSTAGE008 | Scope/Publisher/Clock/part/workのnull、work null返却 | nullを仕事開始前又はborrowed callback内で拒否。成功値なし、既に入ったscopeはcloseされる |

JUnit期待順・UUID・時刻・stepはSSと固定fixtureから作り、productionの返値をexpected生成に使わない。全分岐/例外/null/所有scopeの結果、JDK/Maven、対象commit/command/exit、JaCoCo 4指標、静的解析、sanitized evidence/hashを265/manifestへ記録。実root M/A/Backup Unit/同原本再読・archive/issuer/親外部main/実CHRは別未受入。security/owner境界変更につき451どおり影響suite後にProduction6全回帰を固定sourceで実施する。
