# Canonical起動proof PT仕様書（PG295・未認定）

Program NK-OPS-001 / Bootstrap StartupProofFrame.fromFields/parse/encode/value/fields、RD SYS-002/004・OPS-009、UI212/251、SS341～343/SSC086/087、D04/05。
公開packetだけで権限・flock・freshnessを証明しない。root native属性/seal/A/current bindingの上位admissionは別必須。proof自身FDはseal後採番のためpacketへ入れず推定しない。

| Test ID（PT-OPS-PROOF） | 独立oracle・入力/操作 |
|---|---|
| 001 | 固定NKSTART1＋17行の独立ASCII golden、順序/最終LF、fields/encode一致、redacted表示 |
| 002 | 各欠落/追加/重複/未知/順序/ヘッダ/EOFの拒否 |
| 003 | null契約、byte長0/8192/8193、control/非ASCII、元input保持 |
| 004 | PID2..intMAX/start1..longMAX/FD128..65535/devino1..U64/UIDGID1..4294967294の境界、overflow/非canonical拒否 |
| 005 | group1..16、昇順/重複なし、ID境界/空/0/降順/17件拒否 |
| 006 | API/WEBのみ、lowercase非zeroUUID・Invocation32hex・SHA64hex、異常ドメイン拒否 |
| 007 | inputMap/byte変更から独立、不変返却Map・新byte所有 |
| 008 | 8thread/32 frame、独立期待bytes、不変共有snapshot |

fixture/goldenはTestのliteralでproduction schema/encoderをexpected生成に呼ばない。正常/境界/異常/例外/null/並行を対象、業務再送は対象外。checksumは108/provisional PG295。Map.copyOf内部は不変だが静的解析EI_EXPOSE_REP指摘をsuppressionせず新HashMapのunmodifiable snapshotで解消する（実際の可変公開障害ではない）。全root/native/現在permit/fixed Unit受入は未実行。

