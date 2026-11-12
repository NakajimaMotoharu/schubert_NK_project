# P00702 最大2session・3件目最古revoke：原3sourceの契約対応

- Program NK-AUT-001、WBS-P007-02、AUT-004、DIF-016、UI225/226/234/241、origin/main SS314 §6.1（commit/設計hashはmanifest）。
- 対象: AuthSessionService.issue/constructor、SessionAuditWriter.write、SessionRevocationReason全6値。
- Test IDと独立期待値: PT-AUT-ISS001～008、AUT-SESSION-AUDIT001～009、PT-AUT-005-I/006。各目的/入力/SQL/値/資源/例外/並行観点は下記manifestのchecksおよび既存全Testソースへ対応。
- 発行はapp_users lock→INSERT→有効行のlast_accessed_at,id順lock→size-2件のREPLACED＋同TX重要監査。期限一致は有効外、同owner最大2。SQL、固定日時、独立AES-GCM vector、固定hash、ログの閉fieldを期待値とする。
- 原発行8件・監査9件は対象Main/Test sourceSHA・normal physicalSHA/CRC一致を確認。**原runの限定成功を保持し、新規実行0、whole依存や現DB実績へ転用しない。**監査原本SDK review未設定等の制限も保持。
- AuthSessionServiceTest全6件/576行は公開source読取のみ。実DB/100同時発行/commit・rollback等を含むwhole fixtureはHOLD。部分method選択や別経路で実行しない。
- 正常/境界/NULL/SQL/affected-count/close/再送契約を記録。未知runtimeの元試験はIllegalStateExceptionであり、provider起点AuthenticationContextException等の全例外行列を確認済みにしない。実DB競合・same-source全依存・451/終了依存は未受入。
- metadata実行command: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1319_two_sessions_contract_audit.py`。exit0、新規PT0。対象branch/source/設計/証跡hash/独立期待値はmanifest。
- 証跡: [PG26724 manifest](../018_NK-OPS-001/evidence/PG26724-two-session-contract-v1/manifest.json)。BUG修正なし、Main/Test変更なし、元190新受入0、正式1964PT/53scope維持、工数完成率null。
