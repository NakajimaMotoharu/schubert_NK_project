# P00704 Login Inbox・暗号replay・応答再構成

Program NK-AUT-001、UI222/226/232/234/241、SS312/314/323/324 §6.1。対象AuthenticationResponseMapper/LoginInboxService/LoginReplayService各constructor/method。独立期待値・入力/状態/例外/資源とTest IDは [PG26750 manifest](../018_NK-OPS-001/evidence/PG26750-login-inbox-contract-v1/manifest.json) checksへ対応。

PT-AUT-WIRE001～003のLGNRSP432byte/LOGRSP24byte goldenはUI234 offsetから手組し、JST17桁・millis・固定message・blank/paddingを照合。元3件のMain/Test/source/normal physical同一を確認し、L34M6C1B6allmiss0は**原runの対象1限定測定**として保存。現在の全依存には移さず再実行0。Testの100future無制限待ち/Executor closeは有限owner是正後でなければfresh実行しない。

PT-AUT-INBOX001～009: anonymous/no token・NFC/password/IP canonical、requestMessage/correlation/7日保持、NEW時だけ認証/counter/session/audit、IN_PROGRESS非保存9000、同ID異metadata恒久error、callerTX/passwordとcanonical消去。PT-AUT-REPLAY001～005: 初回688byte snapshot/state/ref/code/相関/全DATAを検証し、成功context/hash/sessionUUID/owner/createdMessage/immutable issued+初回8hへ束縛。成功再送だけ0200、失敗code/retry/message保持。freshHeaderだけ再構築し、replayで認証/発行/touch/失効解除/監査をしない。現権限は別DBverify。

実Inbox/Replayのwhole fixtureはDB/actual ResponseSnapshotCodec/FingerprintKeyRing等HOLDで未実行。部分選択・別経路で実行しない。公開source読取/metadata command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1331_login_inbox_contract_audit.py` exit0、PT0。branch/source/設計commit/hash/元proof/hash/不足はmanifest。Main/Test変更0、BUG修正0、原/1準備のみ完了、原/2・451・終了依存/元190は未受入、正式1964PT/53scope・工数null。
