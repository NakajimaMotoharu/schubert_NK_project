# NK-DAT-001 非認証Inbox参照検査実行結果

## 1. 現在の判定

正式reactor証跡確定前。NonAuthenticationInboxInspectorの22応答参照検査だけが対象であり、専用SQL権限/lock/削除/oneshot、Question/通知7応答、BUG-014完了は未証明。関連QA-046/SSC-049、PG-D-123、013仕様/PT-DB-INBOX-041～048。

探索2（2026-09-09 09:37:34 JST）で追加8件＋関連45件=53件PASS、failed/error/skipped0。追加classはline98/method5/class1/branch50/instruction539、全missed0。NullAway/Spotless/SpotBugs0。正式root clean verifyの代用にはしない。

## 2. 障害・横展開の再試験範囲

- BUG-085/YKT-076: UI232のerror B=spaceとN=0を独立TSV fixtureで分離。PT041の22×12=264 profileを構造有効と確認してから独立保存code表と比較。ANM正常B0/error spaceを通し、PT048のerror B0負canaryを構造検査と本検査が拒否。既存PayloadCodec.errorFillerはB spaceを明示、認証fixtureはBなし。既存Protocol PTも正式reactorで再確認する。
- BUG-086/YKT-077: game_id smallintをSQL `cast(game_id as bigint)`でJava Longへ明示projection。Userのbigint versionとScenarioの2game、NULL/欠落/重複/上下限を実DDL/driverで確認。全API `getObject(..., Long.class)`を照合し、認証のid/user_id/owner_user_id/result_ref_id、Scenarioのprevious_id/next_id（script_files.id由来）/audio_file_id、LogQueryのduration_msは全てbigint。ScenarioRepository.numberは既にgetLong+wasNull（BUG-030/YKT-027）で非該当。再発のため411へ物理型照合・実DDL PTを明文化。型付きJDBC mockだけで合格にしない。

## 3. 検証観点・範囲

PT041は22×全12codeとquery/error参照不正。PT042はUser5種とULK0200、参照型/id、保存version0/1/9/10/999999999、後続name/role/status、欠落。PT043はSCN Iの0/1record、Fの両game、参照違い/欠落。PT044はNULL/匿名/対象外/AAD/欠落/暗号破損/検査間鍵close。PT045は公開JDBC全故障点/NULL/重複/欠落/範囲とaborted transaction 25P02。PT046は状態前後一致・commit/rollback/close/SAVEPOINT/DELETE0・caller所有継続。PT047は100futureを全件回収しtrue/false期待各50を厳密比較。PT048はF1/10000境界、日付/UUID/path/hash/4800×count矛盾、保存後User変更と100回反復、実体未作成かつraw master hash別値でもDB参照検査成功を確認する。

Source/環境/実行日時/command/exit/各Test ID/期待根拠/coverageは正式run後に `evidence/non-authentication-inspection/manifest.json`、sanitizeしたresults.xml、checksumsへ確定する。生wire/context/暗号key/DB dumpは保存しない。
