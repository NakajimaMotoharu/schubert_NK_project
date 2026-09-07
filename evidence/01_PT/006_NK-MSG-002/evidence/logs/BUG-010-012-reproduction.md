# Outbox独立レビューで確認した障害（修正前）

- 発見日: 2026-09-05、工程: PT、branch: dev-messaging
- 対象commit: `80d6ea05e758154689e2f96ac616facfaf2a9ad2`
- 対象Test ID: PT-IDEM-010/011
- 証跡種別: source/SS照合と既存実行済みJUnitの後条件。修正後の再試験結果ではない。

## BUG-010: 必須payload欠落の見逃し

`OutboxJmsSender.validateWireIdentity`は`HeaderCodec.peek`とrow/header一致だけを検査する。
`OutboxDispatcherTest.eventWire`はbody全体をASCII spaceで初期化しheaderだけ設定している。
SS 323 QWKREQ01 data offset 0/26/38（長さ26/12/12）の必須受付ID・Question ID・Async job IDはspaceのままである。
既存実broker testはこのbodyを送信し、SENT/queue後条件をPASSさせた。
同じdataのfield decodeはmandatory違反となるため、正常oracleの不備でもある。

## BUG-011: 送信前の時刻を結果時刻として保存

`dispatch(worker, now, limit)`の同じ`now`をclaim、markFailure、markSentへ渡している。
独立時刻例: claim=T、JMS失敗=T+3秒、初回retry=T+1秒。
期待は失敗確定時からbase 1秒（SS 332 jitter適用時0.9～1.1秒）後であり、既にdueとなる実装は不一致。
送信成功時もcommit確認前のTをsent_atへ保存する。

## BUG-012: jitter欠落

`OutboxRetrySchedule.nextAttemptAt`はbase delayをそのまま加算し、repositoryも同methodを呼ぶ。
SS 332 §7.2が要求する±10% jitterは生成/注入/適用のいずれも存在しない。
base delay自体の1/5/30/60/300秒とattempt 100飽和は別の既存正常条件である。

## 合否の扱い

既存88件成功・coverage 100%は上記欠落を検出していない。PT-IDEM-010/011およびProgram全体のPASSへ算入しない。
本記録にはbody実体、credential、token、session ID、秘密key、DB dumpを含めない。
