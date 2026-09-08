# RERUN-001 Logout再送キューの安全な削除期限

2026-09-08、dev-web/source57efcbb。NK-AUT-001/NK-WEB-001、SSC-045。状態: 再走待ち。推論設定は変更しない。独立したHTTP・業務PG/PTは継続する。

## 1. 観測事実と根拠

- UI226 §9とSS314 §10はAPI/Broker停止時にもlocal Web sessionを即時破棄し、別鍵でcontextを暗号化した技術キューを再送し、成功または保存済API session expiry経過確認後に削除する。
- SS331 §9.2 / V003はexpires_at必須、requested_atより後、attempt_count 0..100。Backoffは5秒/30秒/5分/以後15分（SS314）。
- SessionPrincipal/閉属性JSONはusername/role/context/loginAtで、現在API expiryを持たない。Login応答のexpiryは初回snapshotであり再送では凍結される。
- API AuthenticationContextVerifier.TOUCHは認証ごとにexpires_atを最大値で8h idle延長する。PT-WEB-065は初回期限経過後でも現在context確認が成功する場合を既に検証している。
- Web row expiryはWebアクセスでも延長される。Web rowの削除後、先行してprincipalを読んだ処理のAPI検証まで取り消せる契約はない。古いWeb saveによるrow再作成は既存PTで拒否済みだが、API idle延長の取消しとは異なる。
- V005/V006のWeb session cleanupはpending_context_revocationsを削除する実装ではない。本件キューworkerは未実装であり、実装済み障害としてBUGを偽起票しない。

調査方法: 上記SSとsrcのSessionPrincipal、AuthenticationContextVerifier、V003/V005/V006をread-only検索・照合。これは実行済みの競合PTではない。

## 2. 論理反例（未実行）

T0で業務要求がWeb principalを読む。T1でLogoutのAPI呼出が失敗しlocal rowを削除、再送を登録する。T2>T1で先行業務要求がAPIのcontextを検証し、expiryをT2+8hへ延長する。requested_at+8hを削除期限にすると、APIでcontextが有効な間に再送を捨てる可能性がある。

これは入力・順序からの論理検討であり、再現実行PASS/FAILを主張しない。実JMS/DBでの制御Clock・latch試験は再走の必須作業。

## 3. 採用しなかった仮説

| 仮説 | 不足する根拠 |
|---|---|
| Login時expiryまたはloginAt+8h | 以後のAPI idle延長を反映しない |
| Web row expiry | APIとWebのアクセス時刻・寿命は同一でない |
| Logout requested_at+8h | 上記進行中requestの遅延延長を含まない |
| 任意の余裕時間を加算 | 全配送TTL/処理待ち/DB timeout/停止再開を通じた上限の証明がない |
| 成功応答まで保持しローカル期限を無視 | 安全性候補だがSS314の期限契約、NN expires_at、attempt100上限、鍵世代保持と整合する設計が未確定 |

## 4. 再走時の検討と合格条件

1. 既存IF-002の確定失効応答/期限確認で安全な削除を証明できるか、または進行中要求の終了境界を既存仕様内で定義できるかを調べる。wire追加やUIの保存・削除条件変更を先に採用しない。
2. API expiryの取得源・遅延更新・時計精度、queue登録失敗時のlocal破棄、attempt100、lease、backoff、current/previous鍵寿命を一貫して確定する。
3. SS内補足で足りればSSC-045でSS/code/PTを横断反映。RD/UI変更または利用者判断が必要になった時だけRDF/UIC/QAを先行起票する。
4. 初回expiry経過・Logoutと遅延業務要求・応答喪失・長時間停止・鍵rotation・期限一致前後を独立Clock/JMS/DB後条件で再現し、孤立した有効contextを残したままqueueを削除しないことを検証する。
5. Program PT/coverage/静的解析/実NK CHRと関連台帳の完了まで、未実装・保留を合格算入しない。

## 5. 独立して進める対象

HTTP共通header/認可/handler、画面、質問・回答・通知・非同期、batchの非依存部分、設定・migration。全体走行後にRERUN-001と依存範囲を利用者へ報告する。単なる未着手は再走項目へ追加しない。
