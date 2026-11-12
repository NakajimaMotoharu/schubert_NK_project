# P00705 Logout期限fence・replay・管理失効

Program NK-AUT-001、AUT-001～004/MON-004/MQ-006～010、UI226/232/234/241、SS312 §4.2/314 §6.3/324 §6.2。AuthSessionRevocationService.logout/logoutCurrent/revokeAll、LogoutInboxService.execute/owner、LogoutReplayService.capture/restore/validateSession/wireを対象。独立入力/期待値・Test IDは [PG26762 manifest](../018_NK-OPS-001/evidence/PG26762-logout-contract-v2/manifest.json) checksへ対応。

PT-AUT-008-R01～04/原synthetic JDBC8: CallerTX、User→sessionlock後Clock採時、expiry一致はEXPIRED＋0102重要監査を同TXへstageし、callerが保存fenceを確定。既失効は元revokedAt/0200・時刻/reason不変、未失効ACTIVE有効だけLOGOUT0000、idle延長/actor発行なし。管理失効は新鮮ADMIN認可、targetN12、閉reason3、targetUser→未失効sessionUUID順lock、各update1/audit1。

PT-AUT-LOGOUT-INBOX001～006/whole追加境界: knownowner-only lookupは認可でない。未知context0102/Inboxなし、knownowner/no token/LOGREQ01/001/targetREQUEST:LOGREQ01/data0・7日保持、NEWだけ失効。sameowner同Message再送は別contextを追加失効しない。snapshot初回280byte/24DATA、state/ref/code/correlation/全semanticを検査、参照sessionUUID/owner/hash/revoked=true/元日時へ結合。fresh headerのcurrent request contextを使い、成功replayだけ0200、失敗0102保持。再失効/touch/認可付与なし。

元PG20958/20964の8件は対象Main/Test/sourceとnormal physical/CRC同一を照合し、原L110M7C1B36allmiss0を**原source限定・target1の証拠**として保存。再実行0、whole依存/実DBへの転用なし。2候補whole fixtureは実DB/actual snapshot/HMAC等HOLD、部分method選択しない。

metadata command: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1334_logout_contract_audit.py` exit0、製品PT0。BUG2674/YKT2354は修正前PG26760へ起票・保存。SS314主設計とSS324補足を取り違えた条件を、両設計commit/hash/固有句の正2/負2で是正。初回assert1と補足保存不足の26756v1も保持、製品source/Test/期待値を変更しない。

原/1準備のみ完了。原/2、actualDB期限fence commit/Inbox/snapshot、終了依存、451/元190は未受入。Main/Test変更0/新定義0/追加費0、正式1964PT/53scope/工数null。
