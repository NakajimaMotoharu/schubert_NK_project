# Logout期限・再送限定判断

2026-10-03、Source5dbef62f8（API/sessionは6200と同byte）。477/478A明示許可の6.1Sol/ultra read-only1名、親high。再委任/source編集/採番/外部操作/試験実行0。これは実装・PT受入ではなくQA050/UIC009/SSC171/既存SSC045の承認前案。

## 実物と反例

- UI226 §9/UI242 §3.2はlocal破棄＋暗号再送、成功またはAPI期限確認後削除。SS331 §9.2/V003のexpires_atはNN/requested_atより後。現SessionPrincipal/wireには現在API expiryがなく、初回Login/Web expiry/requested_at+8hを転記できない。
- LogoutWireClientはfresh MessageID/相関/context/全payload検査済み。0000/0200は元revoked/time参照を検査するが、同Message別contextのreplay header投影では別context失効を証明できない。毎試行fresh ID/context不変を維持する。
- 古いnowを捕捉した遅延TOUCHがexpiry観測後に実行され得るため、User→session lock下のexpired fence・同監査/ERROR snapshot commitが必要。fence案は一般0102の永久証明化とは別。
- reply喪失→V013の24h auth_session物理削除→再開ではunknown0102となり、元失効を再取得できない。hash UKは存在中rowだけを保護し、物理削除/復元後の不再生成保証はない。一般0102の証明化、新退役receipt保存object/保持期間は今回案に混ぜない。

## 利用者判断として切り出した最小案

QA050は、期限未知NULL・検証済0000/0200だけ自動DELETE・一般0102/未知/復号不能は保持警告・attempt100飽和後も15m retry・旧鍵のrow/borrower保全を確認する。有限自動回収を保証せず正規復旧/運用処置へ引継ぐことをUI226/242へ明示する。現wire/画面/8h idle/権限/Current baseline/DIFを変更しない。承認前の正本/DDL/oracle変更0、SS331物理差分は承認後append-only migration。

## 同Web組立への必要接続と独立PT

WebApplication→同encrypted repository→CSRF後Logout coordinator。短TX queue INSERT＋旧row DELETE、登録rollback後も独立invalidateを試み未成立503。ContextRevocationRetrierはclaimTX→commit→既存LOG/JMS→CAS更新TX、JMS待ちDB connection/lock0。CASはrow UUID＋唯一claim token＋lease_until、同worker名だけに依存しない。専用AES-GCM AADはtable/row/requested_at/format/key ID、鍵退役は再暗号化・旧version残row/borrower0の実証後のみ。停止はHTTP drain→worker join→reply consumer→外側DB/JMS/鍵。

独立Clock/latch/実JMS・DBでexpiry±1µs/旧nowTOUCH/fence後、同Message別context/保存ERROR、commit後reply喪失/cleanup/長停止、attempt100/lease takeover/旧遅延reply、A→B→C鍵/登録・再暗号化競合、DB/JMS/commit/close不明を検査する。不明rowの期待値は保持警告であり成功DELETEではない。詳細read-only所見はGit外WorkPG379/pg440-logout-expiry-review.mdにも保全。未実装workerをBUGとして偽起票せず、独立User入力等は継続する。
