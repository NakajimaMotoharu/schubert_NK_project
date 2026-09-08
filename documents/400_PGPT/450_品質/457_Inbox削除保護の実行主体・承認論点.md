# Inbox削除保護の実行主体・承認論点

## 1. 状態・対象

2026-09-09にQA-046承認済み。利用者は整合性チェックの実装と、修正台帳先行・設計書反映後の実装を指示。UIC-006/SSC-049は対応中、既存BUG-014/YKT-012は未完了。以下の案に基づき段階的に設計・code・PTを反映する。承認だけで試験合格・障害完了とはしない。
領域: 基盤/NK-DAT-001、依存NK-MSG-002/NK-AUT-001/NK-BAT-001/NK-OPS-001。
RDの通常service起動順、backup成功後削除、冪等性、秘密情報の非公開は変更しない提案である。
新しい保守用の実行主体とcredential利用境界の追加はQA-046で承認。通常serviceの起動順やbatch権限を無断で拡張しない。

## 2. 確認した正本・実装

| 根拠 | 規定/観測 |
|---|---|
| RD171 OPS-009 | PostgreSQL→backup→業務data削除→transfer→Artemis→API→Web→入口の依存順 |
| UI212 §3/5、QA-043/UIC-003 | batchはbatch_runsと限定保守functionだけ。ciphertextの閲覧・APIの鍵をbatchへ追加しない |
| UI251 §4/6 | 通常API起動はBroker後。backup成功後だけ削除、結果不整合Inboxは削除しない |
| SS324 §12/332 §11.4 | PROCESSING、復号/結果参照不整合はInbox削除禁止 |
| SS341 §7 | cleanup時にAPI/Web inactive必須、batch roleはallowlist function実行だけ |
| SS343 §6 | api-inbox-response-aes、api-context-aesはAPI用。unknown keyはdeny closed |
| V006 maintenance_cleanup_message_stores | Inbox候補はprocessing_stateとexpires_atだけで、復号・参照整合を検証していない。既存BUG-014の未修正部分 |
| LoginReplayService.restore | 暗号snapshotに加えauth_sessionsのowner/message/context/issued_at等の参照を検査する。SQL expiry判定だけでは同等の検査にならない |

現在の仕様は保護義務を示すが、停止中の削除直前に鍵を使う検証を誰が行うかを定義していない。
これは全ての実現方法が不可能と証明したという意味ではない。必要な境界追加は承認済みとなり、詳細な競合保護・最小権限の実装と検証を進める。

## 3. 検討した代替案

| 候補 | 評価 |
|---|---|
| expires_at/stateのみで削除 | 復号不能・参照不整合を検知しない。既存BUGを継続するため不採用 |
| batchへAPI AES key/業務SELECTを与える | UI212/QA-043の最小権限と分離に反する。不採用 |
| 通常API serviceをcleanup前に起動 | RD OPS-009/UI251の順序を変える。今回の提案に含めない |
| 過去のreplay成功、既知error flagだけで判定 | 以後の暗号文・鍵・参照変化を検知できない。削除直前の完全な根拠にはしない |
| 停止前の検証済印/attestation | 印から削除までのInbox/参照/key変化と先行session/question削除を考慮する必要がある。単なる印だけでは成立せず、現時点では安全性未証明 |
| Inboxを全件永久保持 | 誤削除防止にはなるが、正常期限到達行のcleanup・容量管理を実装したことにならない。完了扱い不可 |
| 通常API serviceとは別の非公開oneshot検査処理 | 推奨提案。backup成功後・通常service inactiveのまま、削除直前の検査を実行。追加credential利用主体と起動関係の承認が必要 |

## 4. 推奨提案の承認範囲

通常API/Web/Brokerの起動順は維持し、backup成功後のcleanup内部に、外部接続を受け付けない検査専用processを追加する。
HTTP listener/JMS Consumerは作らず、Webから呼び出せるendpoint・新しい業務電文は追加しない。
検査processだけがInboxと参照先を読み、必要なAPI暗号鍵を限定して使用する。batch自体へ鍵・ciphertext・業務SELECTを渡さない。
DBは検査用最小権限roleと限定functionを設計し、汎用API更新権限・DDLを不用意に配布しない。独立OS identity/credential配布・unit hardeningをUI212/251、SS331/342/343/352へ明記する。

検査済みの正確な対象だけを既存batchの限定functionが削除できるようにする。検査と削除の間の対象変更をrow lock/CAS等で拒否する方式は承認後に詳細化し、単なるboolean flagを信頼しない。
欠落/unknown key、復号不能、snapshot/ref不整合、検査process失敗・timeoutの場合は未検証行を削除せず件数と固定理由だけ記録する。平文・鍵・token・ciphertextをログやbatch応答へ出さない。
保護による残留・容量は運用警告対象として扱い、失敗を成功へ書き換えない。

## 5. 承認後に必要な設計・独立PT（未実施）

1. 正常期限到達行を実際に削除し、破損暗号・unknown key・欠落/不一致の参照行は保持する。期限未到達/PROCESSINGも保持する。
2. SS332の先行session/question削除により参照がなくなる場合は推測で整合扱いせず保持する。保持増加を記録する。削除順・保持規則を変える必要が判明したら別途上位feedbackを行う。
3. 固定run/cutoff、backup gate、API/Web inactive検査、advisory lock、row lock順、chunk上限、再実行/中断を一貫させる。
4. 検査後の暗号文・owner/ref・key version変更、別runへの検証印の流用、追加候補、同Message再送/更新、DB commit失敗を独立scheduleで検証する。
5. 追加role・function・OS userの権限を負試験する。batchからciphertext/key/任意tableを読めないことを維持する。
6. 終了code、timeout、異常行の件数、secret scan、暗号平文buffer消去、line/method/class/branch 100%を確認する。
7. YKT-012の全cleanup対象も再確認し、単に検索しただけでは完了にしない。

## 6. 利用者への質問（QA-046）

朝の削除前に、暗号化された処理結果が壊れていないかを調べる専用の検査処理を追加してよいか。
通常のAPI/Webは停止したまま、batchへ秘密鍵を渡さず、検査処理だけに必要最小限の鍵と読取り権限を持たせる。
検査できないデータは削除せず警告する。通常サービスの起動順・利用者画面・電文は変更しない。

承認はこの境界追加の可否であって、未実装方式の安全性試験を免除するものではない。
