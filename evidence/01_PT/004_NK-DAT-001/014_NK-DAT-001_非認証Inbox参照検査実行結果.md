# NK-DAT-001 非認証Inbox参照検査実行結果

最新正式判定: PT-WEB-20260909-30/source15cb454a、2026-09-09 14:30:10～14:36:41 JST、dev-foundation、exit0、全967件・6 Java module全4種coverage100%・静的解析0。当scope全Test ID成功、evidence/non-authentication-inspection/manifest.json SHA-256 `5d9be531de8ba66657a9d721b7062b42e3e4b3c6e1498f7b8b8bacea5189b243`。全27scope同時点性/hash/参照と017の1件・019の4件負canary成功。DB19部品160件＋batch repository17件確定。BUG-109～111/YKT-096/097再試験完了。BUG-104/SSC-051のSQL永続走査・親repository読取は成功、全件走査service/OS/main/backup gate/7参照/全Program完了は残件。本slice合格と工程全体の合格は区別する。以下は旧正式・探索履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/non-authentication-inspection/manifest.jsonの現行SHA-256は `dcd5b7377a716717cf826b4cb259ada0d5aa48b1b0f89513f7e0c683d55fa18e`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

## 1. 現在の判定

正式PT-WEB-20260909-18、source56935aa0、2026-09-09 09:44:09 JST完了、exit0。全838件（Protocol80/Storage34/API442/Web241/CHR41）PASS、failed/error/skipped0、5対象moduleのline/method/class/branch100%、NullAway/Spotless/Enforcer成功、SpotBugs0。NonAuthenticationInboxInspectorの22応答参照検査だけが本slice対象であり、専用SQL権限/lock/削除/oneshot、Question/通知7応答、BUG-014完了は未証明。関連QA-046/SSC-049、PG-D-123、013仕様/PT-DB-INBOX-041～048は全件PASS。

探索2（2026-09-09 09:37:34 JST）で追加8件＋関連45件=53件PASS、failed/error/skipped0。追加classはline98/method5/class1/branch50/instruction539、全missed0。NullAway/Spotless/SpotBugs0。正式root clean verifyの代用にはしない。

## 2. 障害・横展開の再試験範囲

- BUG-085/YKT-076: UI232のerror B=spaceとN=0を独立TSV fixtureで分離。PT041の22×12=264 profileを構造有効と確認してから独立保存code表と比較。ANM正常B0/error spaceを通し、PT048のerror B0負canaryを構造検査と本検査が拒否。既存PayloadCodec.errorFillerはB spaceを明示、認証fixtureはBなし。既存Protocol PTも正式reactorで再確認する。
- BUG-086/YKT-077: game_id smallintをSQL `cast(game_id as bigint)`でJava Longへ明示projection。Userのbigint versionとScenarioの2game、NULL/欠落/重複/上下限を実DDL/driverで確認。全API `getObject(..., Long.class)`を照合し、認証のid/user_id/owner_user_id/result_ref_id、Scenarioのprevious_id/next_id（script_files.id由来）/audio_file_id、LogQueryのduration_msは全てbigint。ScenarioRepository.numberは既にgetLong+wasNull（BUG-030/YKT-027）で非該当。再発のため411へ物理型照合・実DDL PTを明文化。型付きJDBC mockだけで合格にしない。

## 3. 検証観点・範囲

PT041は22×全12codeとquery/error参照不正。PT042はUser5種とULK0200、参照型/id、保存version0/1/9/10/999999999、後続name/role/status、欠落。PT043はSCN Iの0/1record、Fの両game、参照違い/欠落。PT044はNULL/匿名/対象外/AAD/欠落/暗号破損/検査間鍵close。PT045は公開JDBC全故障点/NULL/重複/欠落/範囲とaborted transaction 25P02。PT046は状態前後一致・commit/rollback/close/SAVEPOINT/DELETE0・caller所有継続。PT047は100futureを全件回収しtrue/false期待各50を厳密比較。PT048はF1/10000境界、日付/UUID/path/hash/4800×count矛盾、保存後User変更と100回反復、実体未作成かつraw master hash別値でもDB参照検査成功を確認する。

Source/環境/実行日時/command/exit/各Test ID/期待根拠/coverageは `evidence/non-authentication-inspection/manifest.json`、sanitizeしたresults.xml、checksumsへ確定済み。manifest SHA-256は `57c78b8031463d1605264de71faaa86cda18c7e239ac79d34f4659f9aab13480`。追加classは正式runでもline98/method5/class1/branch50/instruction539、全missed0。8collector/13scopeのhash、base manifest相対traceとnegative canary、Current baselineとV001～009不変更、秘密pattern非検出を確認。生wire/context/暗号key/DB dumpは保存しない。BUG-085/086・YKT-076/077の再試験を本runで完了する。IT/ST・実NK CHR gateは未実施。
