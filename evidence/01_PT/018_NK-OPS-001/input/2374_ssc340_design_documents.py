"""Design-only SSC340 clarification in an isolated sparse worktree; no source/DB operations."""
from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path.cwd();w=r.parent/'ssc340-null-check-design-20261113';paths=['documents/300_SS/330_データ・ファイル/331_DB物理・DDL・index・権限設計.md','documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md','documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md'];base='ba94f093a03f439423f2a8e4c94716c0358ee7d9';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','-C',str(w),'rev-parse','HEAD'],text=True).strip()==base
for path in paths:assert (w/path).read_bytes()==subprocess.check_output(['git','show',base+':'+path],cwd=r)
ss331='''
## SSC340 nullable複合CHECKのTRUE確定・V029追補（2026-11-13）

BUG2846/YKT2405、WBS-P004-01.01～03、DAT001～009/UI241242243、PT-DB-NULL340-001～015。既承認の条件付きNN・ペアNULL・状態/参照整合をSQLへ落とす詳細補足であり、列・table・role/grant・index・wire・業務状態・保持期限を追加/変更しない。[PostgreSQL18 CHECK仕様](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS)では条件のNULLも通過するため、単にnullable値をIN/比較/正規表現/byte長へ渡しただけで条件付きNNを証明してはならない。

次の五制約は正規条件全体のTRUEだけを許可し、FALSE及びNULL/UNKNOWNは23514として拒否する。`IS TRUE`又は同じ三値論理を確実に二値化する明示NN条件を用いる。既存の正常値・正常なNULL組合せと境界は保持する。

|Table / constraint|正規条件・条件付きNN|半端NULLの独立拒否例|
|---|---|---|
|`auth_sessions.ck_auth_sessions_revocation`|未失効はrevoked_at/revoke_reasonともNULL。失効済はrevoked_at NN、revoke_reasonは既6値LOGOUT/DISABLED/PASSWORD_RESET/ADMIN/EXPIRED/REPLACEDのNN。|revoked=true、revoked_at有、revoke_reason=NULL|
|`media_assets.ck_media_assets_pair`|VIDEOはpair_key/pair_roleともNULL。MUSICはpair_role NNでM/I/Nだけ。M/Iはpair_key NNかつ1～256 UTF-8 byte、Nはpair_key NULL。|MUSIC＋M/I＋keyNULL、MUSIC＋roleNULL|
|`notifications.ck_notifications_error`|ERRORは既5値error_code NNとerror_message NN。他stateは両NULL。|ERROR＋codeNULL＋message有|
|`request_inbox.ck_request_inbox_response_snapshot_pair`|body/keyともNULL、又はbody NNで29～1,050,000 byteかつkey NN/既ID format。再構成不可結果のsnapshot必須は324/352の既規則を維持。|ciphertext有＋keyNULL|
|`request_inbox.ck_request_inbox_result_reference`|PROCESSING用の全NULL、NONE＋両refNULL、AUTH_SESSION＋UUIDだけNN、USER/QUESTION/JOB/SCENARIO_FILE＋N12 bigint IDだけNN。state側の条件も従来どおり適用。|USER等type有＋idNULL＋uuidNULL|

V001～028とprovisioning/001_roles.sqlのbyte/checksumを保持し、`V029__strict_nullable_compound_checks.sql`で同名五CHECKをFlyway所有の同一migration transaction内に置換・検証する。NOT VALIDで既データを見逃さず、既存不整合でvalidationが失敗した場合はtransactionをrollbackして旧定義/旧行を保全する。値の推測、理由の補完、半端pairの削除/正規化、既migrationの書換えを行わない。制約数159/24 table、FK/UK/index/role/grant・既成功応答は不変更とし、版29の正常適用・拒否・旧checksum・schema履歴を独立照合する。

NULLを明示的に許すoptional条件、特にQA050のpending_context_revocations.expires_at=NULL（未知期限）は本是正の対象外であり、NULLから削除許可や認可を作らない。SQL外の参照実在/暗号/owner検査もこのCHECKで代替しない。DDL作成/公開・静的確認はDB適用やDB PT合格を意味せず、既存実DB/権限/VM等HOLDは維持する。

'''
ss354='''
## SSC340 条件付きNN・複合CHECK NULL負例PG/PT（2026-11-13）

BUG2846/YKT2405、SS331 SSC340、WBS-P004-01.01～03。独立期待値は次表の正常/拒否結果とSS331に置き、production SQL式やproduction methodをexpected生成器にしない。各負例は他のNN/FK/state/size条件を満たした合成rowを使い、SQLSTATE23514に加えて対象constraint名を確認する。他制約やFKによる拒否を当条件の再試験成功へ算入しない。

|Test ID|入力・操作と独立期待値|
|---|---|
|PT-DB-NULL340-001|MUSIC M/IのkeyNULLと空/257byteを拒否、1/256byteを許容。|
|PT-DB-NULL340-002|MUSIC roleNULL/未知値を拒否。M/I/Nごとの正規組合せを固定literalで許容。|
|PT-DB-NULL340-003|VIDEO両NULLを許容、どちらか一方又は両方の非NULLを拒否。|
|PT-DB-NULL340-004|MUSIC N/keyNULLを許容、N/key非NULLを拒否。|
|PT-DB-NULL340-005|失効済sessionのreasonNULL/未知値又はrevoked_atNULLを拒否、既6値reason＋時刻を許容。|
|PT-DB-NULL340-006|未失効session両NULLを許容、時刻又は理由が残る組合せを拒否。|
|PT-DB-NULL340-007|Notification ERRORのcodeNULL/message有及びcode有/messageNULLを拒否、既5code＋messageを許容。|
|PT-DB-NULL340-008|非ERRORのerror pair両NULLを許容、片方/両方有を拒否。|
|PT-DB-NULL340-009|Inbox ciphertext有/keyNULL及び逆片方NULLを拒否、両NULLの許容は既state/sensitive-result条件も同時に確認。|
|PT-DB-NULL340-010|snapshot両NNでbyte29/1,050,000を許容、28/1,050,001/不正keyを拒否。暗号実体ではなく非秘密合成byteでDB長/ペア条件だけを試験。|
|PT-DB-NULL340-011|USER/QUESTION/JOB/SCENARIO_FILEでidNULL又はuuid有を拒否、N12 min/maxとUUID NULLを許容。|
|PT-DB-NULL340-012|AUTH_SESSIONはUUIDだけNN、NONEは両refNULL、PROCESSINGは全関連NULL。半端/未知type/範囲外を拒否。|
|PT-DB-NULL340-013|版28の不整合rowを保全したupgradeは版29validation失敗・rollback、旧row/旧constraint/旧checksumを保持し、成功履歴を捏造しない。失敗履歴の有無は実DB/Flyway契約に従い観測する。|
|PT-DB-NULL340-014|正常upgrade/validate/冪等再適用、旧28resource byte/checksum不変、24table/159CHECK/FK/UK/index/rolegrantとschema履歴六列の不変を照合する。|
|PT-DB-NULL340-015|明示optional NULL/QA050未知expiryの保全、既state/lease/operationtoken/owner/参照・暗号/保持の他gateを退行させない。|

PGではappend-only DDL・主担当artifact・版一覧・独立SQL fixture・TestID・rollback手順/traceを一貫させる。実DB PTは固定source/run・必要権限/所有が成立した後に行い、whole候補の抽出・fake authority/DB・無許可SQL実行をしない。HOLD中のPG強化review/許可静的代替はNOT_RUNのDB PT、未測定coverage/null及び残存リスクと分離して記録し、PASS/四counter100/正式451/IT-STへ混ぜない。全体の既coverage100%・同source全scope/run・CHR/DIF・終了依存は緩和しない。

'''
ledger='''
## SSC-340 nullable複合CHECKの三値論理と条件付きNNの内部具体化（2026-11-13、PG、設計記述確定）

状態：設計補足確定・main公開前、DDL/製品PT未完。関連BUG2846/YKT2405、WBS-P004-01.01～03。既承認SS331§4.2/5/6.4/7.1の条件付きNN、snapshot pair、参照type別排他を、CHECKのNULL/UNKNOWN通過で失わせないことを明文化した。auth_sessionsも既revoked/time/reason条件を、未失効は両NULL・失効済はtimestampと既6値reasonの両NNとして具体化した。RD/UI/外部wire・列/状態/暗号profileの変更はなく、SS内で合理的に確定できるため新QA/RDF/UICは不要。

確定内容：SS331 SSC340に五constraintのTRUE必須/許容NULL・V001～028及びrolesの不変/append-only V029・不整合legacyを推測補修せずrollbackする条件を記載。SS354 SSC340にPT-DB-NULL340-001～015の独立正常/NULL/境界/拒否/対象constraint名/upgrade rollback/hash/schema・権限後条件を具体化。role/grant/table/column/index/保持・既成功値を変更しない。Source資源・版/BOM/影響Test/traceと実DB再試験は後続PG/PTで未完のまま追跡する。

main公開はorigin/main起点の隔離sparse worktreeでSS331/354/914の三mdだけを通常commit/pushし、未受入code/config/tool/evidenceを含めない。適用commitは三fileのGit履歴とremote照合記録を正とする。実DB/SQL/migration/権限・VM・原本/鍵/nativeHOLDは維持し、静的代替をDB PT/PASS/coverage/正式1964PT/53scope/全PGPT完了へ加算しない。[PostgreSQL18公式CHECK仕様](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS)もNULL semanticsの独立根拠とした。

'''
for path,addition in zip(paths,[ss331,ss354,ledger]):
 p=w/path;old=p.read_text();head,rest=old.split('\n',1);assert ('SSC340 nullable' not in old if path!=paths[2] else '## SSC-340' not in old);new=head+'\n'+addition+rest;assert new.replace(addition,'',1)==old;p.write_text(new)
changed=subprocess.check_output(['git','-C',str(w),'diff','--name-only','-z'],text=True).split('\0');assert set(x for x in changed if x)==set(paths)
o=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG29674-ssc340-design-candidate-v1';o.mkdir();(o/'manifest.json').write_text(json.dumps(dict(actualExit=0,baseMain=base,worktree=str(w),designOnlyPaths=[dict(path=p,sha256=sha(w/p)) for p in paths],existingTextInverseEqual=True,newSsc='SSC-340',newTestViewpoints=15,MainSourceChanged=False,sourceCodeChanged=False,SQLExecuted=0,actualRootDbNativeOperations=0,protectedSourceMaterialized=False,published=False,stage='DESIGN_REVIEW_CANDIDATE_NOT_REMOTE_ACCEPTANCE'),ensure_ascii=False,indent=2)+'\n');print('3design docs candidate completed; exactscope/inverse verified, no implementation or DB action')
