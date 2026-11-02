# SS条件とケースの契約binding

自動生成。原文条件はconditions.json、assertion本文はcases.json。内部詳細はPT、ここでは実結合契約の範囲を示す。候補が同じ節は共通bindingを使用し、実行済み/網羅性認定を意味しない。

<a id="b2-itc-tx-040"></a>
## B2-ITC-TX-040

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |

<a id="b2-itc-sec-020"></a>
## B2-ITC-SEC-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-sec-021"></a>
## B2-ITC-SEC-021

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-021](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-021) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-WIRE |

<a id="b2-itc-tx-041"></a>
## B2-ITC-TX-041

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-041](../520_ケース/522_トランザクション・データ.md#it-tx-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-WIRE |

<a id="b2-itc-sec-022"></a>
## B2-ITC-SEC-022

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |

<a id="b2-itc-tx-042"></a>
## B2-ITC-TX-042

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |

<a id="b2-itc-tx-043"></a>
## B2-ITC-TX-043

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-043](../520_ケース/522_トランザクション・データ.md#it-tx-043) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |

<a id="b2-itc-asy-020"></a>
## B2-ITC-ASY-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-020](../520_ケース/526_MQ・非同期・容量.md#it-asy-020) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-asy-021"></a>
## B2-ITC-ASY-021

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-021](../520_ケース/526_MQ・非同期・容量.md#it-asy-021) | R-ASYNC | A01,A02 | O-DB,O-TIME,O-WIRE |

<a id="b2-itc-asy-022"></a>
## B2-ITC-ASY-022

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-022](../520_ケース/526_MQ・非同期・容量.md#it-asy-022) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-WIRE |

<a id="b2-itc-db-001"></a>
## B2-ITC-DB-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |

<a id="b2-itc-db-002"></a>
## B2-ITC-DB-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b2-itc-db-003"></a>
## B2-ITC-DB-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |

<a id="b2-itc-mq-030"></a>
## B2-ITC-MQ-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-030](../520_ケース/526_MQ・非同期・容量.md#it-mq-030) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-OS,O-TIME |

<a id="b2-itc-mq-031"></a>
## B2-ITC-MQ-031

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-031](../520_ケース/526_MQ・非同期・容量.md#it-mq-031) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |

<a id="b2-itc-net-001"></a>
## B2-ITC-NET-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-NET-001](../520_ケース/522_トランザクション・データ.md#it-net-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-file-050"></a>
## B2-ITC-FILE-050

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-050](../520_ケース/524_ファイル・メディア・Range.md#it-file-050) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-OS,O-WIRE |

<a id="b2-itc-file-051"></a>
## B2-ITC-FILE-051

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-051](../520_ケース/524_ファイル・メディア・Range.md#it-file-051) | R-FILE | A01,A02 | O-DB,O-FS,O-WIRE |

<a id="b2-itc-file-052"></a>
## B2-ITC-FILE-052

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-053"></a>
## B2-ITC-FILE-053

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-053](../520_ケース/524_ファイル・メディア・Range.md#it-file-053) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS |

<a id="b2-itc-file-054"></a>
## B2-ITC-FILE-054

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-054](../520_ケース/524_ファイル・メディア・Range.md#it-file-054) | R-MEDIA | A01,A02 | O-FS,O-HTTP,O-WIRE |

<a id="b2-itc-file-055"></a>
## B2-ITC-FILE-055

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-055](../520_ケース/524_ファイル・メディア・Range.md#it-file-055) | R-MEDIA | A01,A02 | O-FS,O-HTTP |

<a id="b2-itc-ops-020"></a>
## B2-ITC-OPS-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-020](../520_ケース/525_運用・復旧・監視.md#it-ops-020) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-OS |

<a id="b2-itc-ops-021"></a>
## B2-ITC-OPS-021

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-021](../520_ケース/525_運用・復旧・監視.md#it-ops-021) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b2-itc-ops-022"></a>
## B2-ITC-OPS-022

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-022](../520_ケース/525_運用・復旧・監視.md#it-ops-022) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |

<a id="b2-itc-ops-023"></a>
## B2-ITC-OPS-023

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-023](../520_ケース/525_運用・復旧・監視.md#it-ops-023) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |

<a id="b2-itc-ops-024"></a>
## B2-ITC-OPS-024

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-024](../520_ケース/525_運用・復旧・監視.md#it-ops-024) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |

<a id="b2-itc-ops-025"></a>
## B2-ITC-OPS-025

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-025](../520_ケース/525_運用・復旧・監視.md#it-ops-025) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-TIME |

<a id="b2-itc-ops-026"></a>
## B2-ITC-OPS-026

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-026](../520_ケース/525_運用・復旧・監視.md#it-ops-026) | R-OPS | A01,A02 | O-DB,O-TIME |

<a id="b2-itc-ops-027"></a>
## B2-ITC-OPS-027

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-027](../520_ケース/525_運用・復旧・監視.md#it-ops-027) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-LOG |

<a id="b2-itc-ops-028"></a>
## B2-ITC-OPS-028

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-028](../520_ケース/525_運用・復旧・監視.md#it-ops-028) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-TIME |

<a id="b2-itc-ops-029"></a>
## B2-ITC-OPS-029

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |

<a id="b2-itc-sec-023"></a>
## B2-ITC-SEC-023

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b2-itc-log-020"></a>
## B2-ITC-LOG-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-020](../520_ケース/525_運用・復旧・監視.md#it-log-020) | R-WLOG | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-data-020"></a>
## B2-ITC-DATA-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-020](../520_ケース/522_トランザクション・データ.md#it-data-020) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-sec-024"></a>
## B2-ITC-SEC-024

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-024](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-024) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-range-001"></a>
## B2-ITC-RANGE-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-RANGE-001](../520_ケース/524_ファイル・メディア・Range.md#it-range-001) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60 | O-FS,O-HTTP,O-METRIC |

<a id="b2-itc-perf-030"></a>
## B2-ITC-PERF-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-030](../520_ケース/527_性能・資源・Logout混在.md#it-perf-030) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-031"></a>
## B2-ITC-PERF-031

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-031](../520_ケース/527_性能・資源・Logout混在.md#it-perf-031) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-032"></a>
## B2-ITC-PERF-032

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-032](../520_ケース/527_性能・資源・Logout混在.md#it-perf-032) | R-SYNC | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-033"></a>
## B2-ITC-PERF-033

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-033](../520_ケース/527_性能・資源・Logout混在.md#it-perf-033) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME |

<a id="b2-itc-perf-034"></a>
## B2-ITC-PERF-034

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-034](../520_ケース/527_性能・資源・Logout混在.md#it-perf-034) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b2-itc-perf-035"></a>
## B2-ITC-PERF-035

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-035](../520_ケース/527_性能・資源・Logout混在.md#it-perf-035) | R-OPS | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b2-itc-perf-036"></a>
## B2-ITC-PERF-036

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-036](../520_ケース/527_性能・資源・Logout混在.md#it-perf-036) | R-SYNC | A01,A02 | O-DB,O-METRIC,O-TIME,O-WIRE |

<a id="b2-itc-retry-100-集中-なし"></a>
## B2-ITC-RETRY-100-集中-なし

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-mq-010"></a>
## B2-ITC-MQ-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |

<a id="b2-itc-perf-010"></a>
## B2-ITC-PERF-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-010](../520_ケース/527_性能・資源・Logout混在.md#it-perf-010) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-020"></a>
## B2-ITC-PERF-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-020](../520_ケース/527_性能・資源・Logout混在.md#it-perf-020) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-tx-030"></a>
## B2-ITC-TX-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b2-itc-req-001"></a>
## B2-ITC-REQ-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-REQ-001](../520_ケース/526_MQ・非同期・容量.md#it-req-001) | R-ASYNC | A01,A02,A03 | O-DB,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-tx-044"></a>
## B2-ITC-TX-044

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-044](../520_ケース/522_トランザクション・データ.md#it-tx-044) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-LOCK,O-WIRE |

<a id="b2-itc-data-021"></a>
## B2-ITC-DATA-021

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-021](../520_ケース/522_トランザクション・データ.md#it-data-021) | R-SYNC | A01,A02,A03 | O-DB,O-TIME,O-WIRE |

<a id="b2-itc-sec-025"></a>
## B2-ITC-SEC-025

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-wire-001"></a>
## B2-ITC-WIRE-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b2-itc-http-001"></a>
## B2-ITC-HTTP-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-001](../520_ケース/523_認証・権限・セキュリティ.md#it-http-001) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-log-021"></a>
## B2-ITC-LOG-021

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-021](../520_ケース/525_運用・復旧・監視.md#it-log-021) | R-WLOG | A01,A02,A03,A04 | O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-ops-030"></a>
## B2-ITC-OPS-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |

<a id="b2-itc-ops-031"></a>
## B2-ITC-OPS-031

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-031](../520_ケース/525_運用・復旧・監視.md#it-ops-031) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |

<a id="b2-itc-asy-023"></a>
## B2-ITC-ASY-023

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-023](../520_ケース/526_MQ・非同期・容量.md#it-asy-023) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |

<a id="b2-itc-tx-001"></a>
## B2-ITC-TX-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-002"></a>
## B2-ITC-TX-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-002](../520_ケース/522_トランザクション・データ.md#it-tx-002) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-003"></a>
## B2-ITC-TX-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-003](../520_ケース/522_トランザクション・データ.md#it-tx-003) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-004"></a>
## B2-ITC-TX-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-004](../520_ケース/522_トランザクション・データ.md#it-tx-004) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-005"></a>
## B2-ITC-TX-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-006"></a>
## B2-ITC-TX-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-006](../520_ケース/522_トランザクション・データ.md#it-tx-006) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-007"></a>
## B2-ITC-TX-007

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-007](../520_ケース/522_トランザクション・データ.md#it-tx-007) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-008"></a>
## B2-ITC-TX-008

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-008](../520_ケース/522_トランザクション・データ.md#it-tx-008) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-009"></a>
## B2-ITC-TX-009

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-009](../520_ケース/522_トランザクション・データ.md#it-tx-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-tx-050"></a>
## B2-ITC-TX-050

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b2-itc-tx-051"></a>
## B2-ITC-TX-051

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-051](../520_ケース/522_トランザクション・データ.md#it-tx-051) | R-FILE | A01,A02 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-tx-052"></a>
## B2-ITC-TX-052

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-052](../520_ケース/522_トランザクション・データ.md#it-tx-052) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b2-itc-tx-053"></a>
## B2-ITC-TX-053

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-053](../520_ケース/522_トランザクション・データ.md#it-tx-053) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-WIRE |

<a id="b2-itc-tx-010"></a>
## B2-ITC-TX-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-tx-011"></a>
## B2-ITC-TX-011

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-011](../520_ケース/522_トランザクション・データ.md#it-tx-011) | R-SYNC | A01,A02 | O-DB,O-MQ,O-WIRE |

<a id="b2-itc-tx-012"></a>
## B2-ITC-TX-012

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-012](../520_ケース/522_トランザクション・データ.md#it-tx-012) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b2-itc-tx-013"></a>
## B2-ITC-TX-013

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-013](../520_ケース/522_トランザクション・データ.md#it-tx-013) | R-SYNC | A01,A02 | O-DB,O-LOG,O-WIRE |

<a id="b2-itc-tx-014"></a>
## B2-ITC-TX-014

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-014](../520_ケース/522_トランザクション・データ.md#it-tx-014) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-tx-015"></a>
## B2-ITC-TX-015

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-015](../520_ケース/522_トランザクション・データ.md#it-tx-015) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b2-itc-tx-016"></a>
## B2-ITC-TX-016

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |

<a id="b2-itc-tx-017"></a>
## B2-ITC-TX-017

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-017](../520_ケース/522_トランザクション・データ.md#it-tx-017) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOG,O-WIRE |

<a id="b2-itc-tx-018"></a>
## B2-ITC-TX-018

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-018](../520_ケース/522_トランザクション・データ.md#it-tx-018) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-tx-019"></a>
## B2-ITC-TX-019

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-data-001"></a>
## B2-ITC-DATA-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-data-030"></a>
## B2-ITC-DATA-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-030](../520_ケース/522_トランザクション・データ.md#it-data-030) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-data-031"></a>
## B2-ITC-DATA-031

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-031](../520_ケース/522_トランザクション・データ.md#it-data-031) | R-SYNC | A01,A02 | O-DB,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-data-002"></a>
## B2-ITC-DATA-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-002](../520_ケース/522_トランザクション・データ.md#it-data-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-data-032"></a>
## B2-ITC-DATA-032

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-032](../520_ケース/522_トランザクション・データ.md#it-data-032) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-MQ,O-WIRE |

<a id="b2-itc-data-003"></a>
## B2-ITC-DATA-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-asy-001"></a>
## B2-ITC-ASY-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-001](../520_ケース/526_MQ・非同期・容量.md#it-asy-001) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-asy-002"></a>
## B2-ITC-ASY-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-002](../520_ケース/526_MQ・非同期・容量.md#it-asy-002) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-asy-003"></a>
## B2-ITC-ASY-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-003](../520_ケース/526_MQ・非同期・容量.md#it-asy-003) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-asy-004"></a>
## B2-ITC-ASY-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-004](../520_ケース/526_MQ・非同期・容量.md#it-asy-004) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-asy-005"></a>
## B2-ITC-ASY-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-005](../520_ケース/526_MQ・非同期・容量.md#it-asy-005) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-asy-006"></a>
## B2-ITC-ASY-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-006](../520_ケース/526_MQ・非同期・容量.md#it-asy-006) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |

<a id="b2-itc-asy-007"></a>
## B2-ITC-ASY-007

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-007](../520_ケース/526_MQ・非同期・容量.md#it-asy-007) | R-ASYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-asy-008"></a>
## B2-ITC-ASY-008

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-008](../520_ケース/526_MQ・非同期・容量.md#it-asy-008) | R-ASYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b2-itc-asy-009"></a>
## B2-ITC-ASY-009

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-009](../520_ケース/526_MQ・非同期・容量.md#it-asy-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-MQ,O-WIRE |

<a id="b2-itc-mq-001"></a>
## B2-ITC-MQ-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-mq-002"></a>
## B2-ITC-MQ-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b2-itc-mq-003"></a>
## B2-ITC-MQ-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |

<a id="b2-itc-mq-004"></a>
## B2-ITC-MQ-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-004](../520_ケース/526_MQ・非同期・容量.md#it-mq-004) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b2-itc-mq-005"></a>
## B2-ITC-MQ-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-mq-006"></a>
## B2-ITC-MQ-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-mq-020"></a>
## B2-ITC-MQ-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b2-itc-mq-033"></a>
## B2-ITC-MQ-033

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |

<a id="b2-itc-mq-034"></a>
## B2-ITC-MQ-034

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-mq-035"></a>
## B2-ITC-MQ-035

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-sec-001"></a>
## B2-ITC-SEC-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-001](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |

<a id="b2-itc-sec-002"></a>
## B2-ITC-SEC-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-002](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-002) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-sec-003"></a>
## B2-ITC-SEC-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-003](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-003) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-TIME,O-WIRE |

<a id="b2-itc-sec-004"></a>
## B2-ITC-SEC-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-sec-005"></a>
## B2-ITC-SEC-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-sec-006"></a>
## B2-ITC-SEC-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-sec-007"></a>
## B2-ITC-SEC-007

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-sec-008"></a>
## B2-ITC-SEC-008

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-008](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-008) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-sec-009"></a>
## B2-ITC-SEC-009

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-sec-010"></a>
## B2-ITC-SEC-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-010](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-010) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-sec-011"></a>
## B2-ITC-SEC-011

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-sec-012"></a>
## B2-ITC-SEC-012

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-bound-001"></a>
## B2-ITC-BOUND-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-BOUND-001](../520_ケース/523_認証・権限・セキュリティ.md#it-bound-001) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-bound-002"></a>
## B2-ITC-BOUND-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-BOUND-002](../520_ケース/523_認証・権限・セキュリティ.md#it-bound-002) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-sec-013"></a>
## B2-ITC-SEC-013

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-013](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-013) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-sec-030"></a>
## B2-ITC-SEC-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-030](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-030) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-sec-031"></a>
## B2-ITC-SEC-031

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-031](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-031) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-sec-032"></a>
## B2-ITC-SEC-032

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-032](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-032) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-LOG,O-TIME,O-WIRE |

<a id="b2-itc-perf-040"></a>
## B2-ITC-PERF-040

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-040](../520_ケース/527_性能・資源・Logout混在.md#it-perf-040) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-file-001"></a>
## B2-ITC-FILE-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-file-002"></a>
## B2-ITC-FILE-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-file-003"></a>
## B2-ITC-FILE-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-file-004"></a>
## B2-ITC-FILE-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-file-005"></a>
## B2-ITC-FILE-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-file-006"></a>
## B2-ITC-FILE-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-file-010"></a>
## B2-ITC-FILE-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-010](../520_ケース/524_ファイル・メディア・Range.md#it-file-010) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-011"></a>
## B2-ITC-FILE-011

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-011](../520_ケース/524_ファイル・メディア・Range.md#it-file-011) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-012"></a>
## B2-ITC-FILE-012

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-012](../520_ケース/524_ファイル・メディア・Range.md#it-file-012) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-020"></a>
## B2-ITC-FILE-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-020](../520_ケース/524_ファイル・メディア・Range.md#it-file-020) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-021"></a>
## B2-ITC-FILE-021

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-021](../520_ケース/524_ファイル・メディア・Range.md#it-file-021) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-022"></a>
## B2-ITC-FILE-022

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-022](../520_ケース/524_ファイル・メディア・Range.md#it-file-022) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-023"></a>
## B2-ITC-FILE-023

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-023](../520_ケース/524_ファイル・メディア・Range.md#it-file-023) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-024"></a>
## B2-ITC-FILE-024

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-025"></a>
## B2-ITC-FILE-025

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-027"></a>
## B2-ITC-FILE-027

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-027](../520_ケース/524_ファイル・メディア・Range.md#it-file-027) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-028"></a>
## B2-ITC-FILE-028

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-028](../520_ケース/524_ファイル・メディア・Range.md#it-file-028) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-029"></a>
## B2-ITC-FILE-029

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-029](../520_ケース/524_ファイル・メディア・Range.md#it-file-029) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-030"></a>
## B2-ITC-FILE-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-030](../520_ケース/524_ファイル・メディア・Range.md#it-file-030) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-031"></a>
## B2-ITC-FILE-031

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-031](../520_ケース/524_ファイル・メディア・Range.md#it-file-031) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-026"></a>
## B2-ITC-FILE-026

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-026](../520_ケース/524_ファイル・メディア・Range.md#it-file-026) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |

<a id="b2-itc-file-040"></a>
## B2-ITC-FILE-040

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |

<a id="b2-itc-range-020"></a>
## B2-ITC-RANGE-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-RANGE-020](../520_ケース/524_ファイル・メディア・Range.md#it-range-020) | R-MEDIA | A01,A02,A03,A04,A05 | O-FS,O-HTTP,O-LOG,O-METRIC,O-OS,O-WIRE |

<a id="b2-itc-file-060"></a>
## B2-ITC-FILE-060

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-060](../520_ケース/524_ファイル・メディア・Range.md#it-file-060) | R-FILE | A01,A02,A03 | O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-file-061"></a>
## B2-ITC-FILE-061

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |

<a id="b2-itc-file-062"></a>
## B2-ITC-FILE-062

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-062](../520_ケース/524_ファイル・メディア・Range.md#it-file-062) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-file-063"></a>
## B2-ITC-FILE-063

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-063](../520_ケース/524_ファイル・メディア・Range.md#it-file-063) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-file-064"></a>
## B2-ITC-FILE-064

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-064](../520_ケース/524_ファイル・メディア・Range.md#it-file-064) | R-OPS | A01,A02,A03,A04,A05,A06 | O-FS,O-HTTP,O-LOG,O-OS |

<a id="b2-itc-if-001"></a>
## B2-ITC-IF-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-002"></a>
## B2-ITC-IF-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-002](../520_ケース/521_インターフェース.md#it-if-002) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-003"></a>
## B2-ITC-IF-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-003](../520_ケース/521_インターフェース.md#it-if-003) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-004"></a>
## B2-ITC-IF-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-004](../520_ケース/521_インターフェース.md#it-if-004) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-005"></a>
## B2-ITC-IF-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-005](../520_ケース/521_インターフェース.md#it-if-005) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-006"></a>
## B2-ITC-IF-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-006](../520_ケース/521_インターフェース.md#it-if-006) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-007"></a>
## B2-ITC-IF-007

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-007](../520_ケース/521_インターフェース.md#it-if-007) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-008"></a>
## B2-ITC-IF-008

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-008](../520_ケース/521_インターフェース.md#it-if-008) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-009"></a>
## B2-ITC-IF-009

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-009](../520_ケース/521_インターフェース.md#it-if-009) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-010"></a>
## B2-ITC-IF-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-010](../520_ケース/521_インターフェース.md#it-if-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-011"></a>
## B2-ITC-IF-011

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-011](../520_ケース/521_インターフェース.md#it-if-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-012"></a>
## B2-ITC-IF-012

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-012](../520_ケース/521_インターフェース.md#it-if-012) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-013"></a>
## B2-ITC-IF-013

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-013](../520_ケース/521_インターフェース.md#it-if-013) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-014"></a>
## B2-ITC-IF-014

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-014](../520_ケース/521_インターフェース.md#it-if-014) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-015"></a>
## B2-ITC-IF-015

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-015](../520_ケース/521_インターフェース.md#it-if-015) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-016"></a>
## B2-ITC-IF-016

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-016](../520_ケース/521_インターフェース.md#it-if-016) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-017"></a>
## B2-ITC-IF-017

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-018"></a>
## B2-ITC-IF-018

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-018](../520_ケース/521_インターフェース.md#it-if-018) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-019"></a>
## B2-ITC-IF-019

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-020"></a>
## B2-ITC-IF-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-020](../520_ケース/521_インターフェース.md#it-if-020) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-021"></a>
## B2-ITC-IF-021

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-022"></a>
## B2-ITC-IF-022

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-023"></a>
## B2-ITC-IF-023

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-024"></a>
## B2-ITC-IF-024

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-025"></a>
## B2-ITC-IF-025

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-026"></a>
## B2-ITC-IF-026

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-026](../520_ケース/521_インターフェース.md#it-if-026) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-027"></a>
## B2-ITC-IF-027

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-027](../520_ケース/521_インターフェース.md#it-if-027) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-028"></a>
## B2-ITC-IF-028

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-028](../520_ケース/521_インターフェース.md#it-if-028) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-029"></a>
## B2-ITC-IF-029

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-029](../520_ケース/521_インターフェース.md#it-if-029) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-030"></a>
## B2-ITC-IF-030

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-030](../520_ケース/521_インターフェース.md#it-if-030) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-031"></a>
## B2-ITC-IF-031

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-031](../520_ケース/521_インターフェース.md#it-if-031) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-032"></a>
## B2-ITC-IF-032

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-032](../520_ケース/521_インターフェース.md#it-if-032) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-if-033"></a>
## B2-ITC-IF-033

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-http-010"></a>
## B2-ITC-HTTP-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-010](../520_ケース/521_インターフェース.md#it-http-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-http-011"></a>
## B2-ITC-HTTP-011

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-011](../520_ケース/521_インターフェース.md#it-http-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |

<a id="b2-itc-http-012"></a>
## B2-ITC-HTTP-012

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-012](../520_ケース/521_インターフェース.md#it-http-012) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-WIRE |

<a id="b2-itc-http-013"></a>
## B2-ITC-HTTP-013

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-http-014"></a>
## B2-ITC-HTTP-014

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b2-itc-log-001"></a>
## B2-ITC-LOG-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-001](../520_ケース/525_運用・復旧・監視.md#it-log-001) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-MQ,O-WIRE |

<a id="b2-itc-log-002"></a>
## B2-ITC-LOG-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-002](../520_ケース/525_運用・復旧・監視.md#it-log-002) | R-WLOG | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-log-003"></a>
## B2-ITC-LOG-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-003](../520_ケース/525_運用・復旧・監視.md#it-log-003) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |

<a id="b2-itc-log-004"></a>
## B2-ITC-LOG-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-004](../520_ケース/525_運用・復旧・監視.md#it-log-004) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b2-itc-log-005"></a>
## B2-ITC-LOG-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-005](../520_ケース/525_運用・復旧・監視.md#it-log-005) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-METRIC,O-MQ,O-OS |

<a id="b2-itc-log-006"></a>
## B2-ITC-LOG-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |

<a id="b2-itc-log-010"></a>
## B2-ITC-LOG-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-010](../520_ケース/525_運用・復旧・監視.md#it-log-010) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-001"></a>
## B2-ITC-OPS-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-002"></a>
## B2-ITC-OPS-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-002](../520_ケース/525_運用・復旧・監視.md#it-ops-002) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-003"></a>
## B2-ITC-OPS-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-003](../520_ケース/525_運用・復旧・監視.md#it-ops-003) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-004"></a>
## B2-ITC-OPS-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |

<a id="b2-itc-ops-005"></a>
## B2-ITC-OPS-005

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-005](../520_ケース/525_運用・復旧・監視.md#it-ops-005) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-006"></a>
## B2-ITC-OPS-006

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-006](../520_ケース/525_運用・復旧・監視.md#it-ops-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-007"></a>
## B2-ITC-OPS-007

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-008"></a>
## B2-ITC-OPS-008

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |

<a id="b2-itc-ops-009"></a>
## B2-ITC-OPS-009

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |

<a id="b2-itc-ops-010"></a>
## B2-ITC-OPS-010

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-010](../520_ケース/525_運用・復旧・監視.md#it-ops-010) | R-OPS | A01,A02,A03 | O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-ops-011"></a>
## B2-ITC-OPS-011

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-011](../520_ケース/525_運用・復旧・監視.md#it-ops-011) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b2-itc-ops-012"></a>
## B2-ITC-OPS-012

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-012](../520_ケース/525_運用・復旧・監視.md#it-ops-012) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-013"></a>
## B2-ITC-OPS-013

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-014"></a>
## B2-ITC-OPS-014

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-014](../520_ケース/525_運用・復旧・監視.md#it-ops-014) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-ops-015"></a>
## B2-ITC-OPS-015

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-015](../520_ケース/525_運用・復旧・監視.md#it-ops-015) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS |

<a id="b2-itc-ops-016"></a>
## B2-ITC-OPS-016

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-016](../520_ケース/525_運用・復旧・監視.md#it-ops-016) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-TIME |

<a id="b2-itc-restore-001"></a>
## B2-ITC-RESTORE-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-config-001"></a>
## B2-ITC-CONFIG-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |

<a id="b2-itc-perf-001"></a>
## B2-ITC-PERF-001

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-002"></a>
## B2-ITC-PERF-002

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-003"></a>
## B2-ITC-PERF-003

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b2-itc-perf-041"></a>
## B2-ITC-PERF-041

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-042"></a>
## B2-ITC-PERF-042

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-042](../520_ケース/527_性能・資源・Logout混在.md#it-perf-042) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-043"></a>
## B2-ITC-PERF-043

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-043](../520_ケース/527_性能・資源・Logout混在.md#it-perf-043) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-perf-044"></a>
## B2-ITC-PERF-044

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-perf-045"></a>
## B2-ITC-PERF-045

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-045](../520_ケース/527_性能・資源・Logout混在.md#it-perf-045) | R-FILE | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-ops-040"></a>
## B2-ITC-OPS-040

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-041"></a>
## B2-ITC-OPS-041

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-042"></a>
## B2-ITC-OPS-042

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-043"></a>
## B2-ITC-OPS-043

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-043](../520_ケース/525_運用・復旧・監視.md#it-ops-043) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30 | O-DB,O-FS,O-LOCK,O-LOG,O-OS |

<a id="b2-itc-ops-044"></a>
## B2-ITC-OPS-044

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-045"></a>
## B2-ITC-OPS-045

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-046"></a>
## B2-ITC-OPS-046

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-047"></a>
## B2-ITC-OPS-047

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-048"></a>
## B2-ITC-OPS-048

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-049"></a>
## B2-ITC-OPS-049

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |

<a id="b2-itc-ops-050"></a>
## B2-ITC-OPS-050

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-050](../520_ケース/525_運用・復旧・監視.md#it-ops-050) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-ops-051"></a>
## B2-ITC-OPS-051

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-051](../520_ケース/525_運用・復旧・監視.md#it-ops-051) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-tx-054"></a>
## B2-ITC-TX-054

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b2-itc-ops-052"></a>
## B2-ITC-OPS-052

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-053"></a>
## B2-ITC-OPS-053

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |

<a id="b2-itc-ops-054"></a>
## B2-ITC-OPS-054

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |

<a id="b2-itc-ops-055"></a>
## B2-ITC-OPS-055

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b2-itc-ops-056"></a>
## B2-ITC-OPS-056

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b2-itc-db-004"></a>
## B2-ITC-DB-004

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |

<a id="b2-itc-ops-057"></a>
## B2-ITC-OPS-057

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-057](../520_ケース/525_運用・復旧・監視.md#it-ops-057) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b2-itc-perf-046"></a>
## B2-ITC-PERF-046

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b2-itc-log-022"></a>
## B2-ITC-LOG-022

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-022](../520_ケース/525_運用・復旧・監視.md#it-log-022) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-130c897e3cdda3"></a>
## B3-130c897e3cdda3

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-d422b5ba029a07"></a>
## B3-d422b5ba029a07

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-032](../520_ケース/521_インターフェース.md#it-if-032) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |

<a id="b3-44d73171e6911a"></a>
## B3-44d73171e6911a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-002](../520_ケース/525_運用・復旧・監視.md#it-log-002) | R-WLOG | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b3-2365207e32f130"></a>
## B3-2365207e32f130

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b3-cf3bf5fe418ff2"></a>
## B3-cf3bf5fe418ff2

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-021](../520_ケース/525_運用・復旧・監視.md#it-ops-021) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-6130f591c41e08"></a>
## B3-6130f591c41e08

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-010](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-010) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-704144740dffa2"></a>
## B3-704144740dffa2

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-008](../520_ケース/526_MQ・非同期・容量.md#it-asy-008) | R-ASYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b3-41773a9f284e11"></a>
## B3-41773a9f284e11

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-007](../520_ケース/526_MQ・非同期・容量.md#it-asy-007) | R-ASYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-032](../520_ケース/521_インターフェース.md#it-if-032) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-REQ-001](../520_ケース/526_MQ・非同期・容量.md#it-req-001) | R-ASYNC | A01,A02,A03 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b3-906917398bf548"></a>
## B3-906917398bf548

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-003](../520_ケース/526_MQ・非同期・容量.md#it-asy-003) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-004](../520_ケース/526_MQ・非同期・容量.md#it-asy-004) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-005](../520_ケース/526_MQ・非同期・容量.md#it-asy-005) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-009](../520_ケース/526_MQ・非同期・容量.md#it-asy-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-MQ,O-WIRE |
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b3-20ab6084f979b7"></a>
## B3-20ab6084f979b7

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-001](../520_ケース/526_MQ・非同期・容量.md#it-asy-001) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b3-dd9a84bb657826"></a>
## B3-dd9a84bb657826

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-REQ-001](../520_ケース/526_MQ・非同期・容量.md#it-req-001) | R-ASYNC | A01,A02,A03 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-002](../520_ケース/522_トランザクション・データ.md#it-tx-002) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-003](../520_ケース/522_トランザクション・データ.md#it-tx-003) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-004](../520_ケース/522_トランザクション・データ.md#it-tx-004) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-051](../520_ケース/522_トランザクション・データ.md#it-tx-051) | R-FILE | A01,A02 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-TX-053](../520_ケース/522_トランザクション・データ.md#it-tx-053) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-WIRE |

<a id="b3-8d901907559fa2"></a>
## B3-8d901907559fa2

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-002](../520_ケース/521_インターフェース.md#it-if-002) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-001](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-SEC-002](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-002) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |
| [IT-SEC-032](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-032) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-LOG,O-TIME,O-WIRE |

<a id="b3-996f1f9e6849e7"></a>
## B3-996f1f9e6849e7

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-031](../520_ケース/522_トランザクション・データ.md#it-data-031) | R-SYNC | A01,A02 | O-DB,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-IF-003](../520_ケース/521_インターフェース.md#it-if-003) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-005](../520_ケース/521_インターフェース.md#it-if-005) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-TX-051](../520_ケース/522_トランザクション・データ.md#it-tx-051) | R-FILE | A01,A02 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |

<a id="b3-eed7bfc00762c7"></a>
## B3-eed7bfc00762c7

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-002](../520_ケース/522_トランザクション・データ.md#it-tx-002) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-003](../520_ケース/522_トランザクション・データ.md#it-tx-003) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-004](../520_ケース/522_トランザクション・データ.md#it-tx-004) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-052](../520_ケース/522_トランザクション・データ.md#it-tx-052) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-4962fea17cd4a8"></a>
## B3-4962fea17cd4a8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-TX-052](../520_ケース/522_トランザクション・データ.md#it-tx-052) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-c52423e62867e9"></a>
## B3-c52423e62867e9

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-TX-012](../520_ケース/522_トランザクション・データ.md#it-tx-012) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-014](../520_ケース/522_トランザクション・データ.md#it-tx-014) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-TX-052](../520_ケース/522_トランザクション・データ.md#it-tx-052) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-cca77af8c96b76"></a>
## B3-cca77af8c96b76

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-TX-050](../520_ケース/522_トランザクション・データ.md#it-tx-050) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-052](../520_ケース/522_トランザクション・データ.md#it-tx-052) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-a452a2c6e05823"></a>
## B3-a452a2c6e05823

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-TX-015](../520_ケース/522_トランザクション・データ.md#it-tx-015) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-052](../520_ケース/522_トランザクション・データ.md#it-tx-052) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-6be67408882dfb"></a>
## B3-6be67408882dfb

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-032](../520_ケース/522_トランザクション・データ.md#it-data-032) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-MQ,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-REQ-001](../520_ケース/526_MQ・非同期・容量.md#it-req-001) | R-ASYNC | A01,A02,A03 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-TX-006](../520_ケース/522_トランザクション・データ.md#it-tx-006) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-007](../520_ケース/522_トランザクション・データ.md#it-tx-007) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-008](../520_ケース/522_トランザクション・データ.md#it-tx-008) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-009](../520_ケース/522_トランザクション・データ.md#it-tx-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-af9f3cc0ac9c37"></a>
## B3-af9f3cc0ac9c37

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-007](../520_ケース/526_MQ・非同期・容量.md#it-asy-007) | R-ASYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-DATA-032](../520_ケース/522_トランザクション・データ.md#it-data-032) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-MQ,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-REQ-001](../520_ケース/526_MQ・非同期・容量.md#it-req-001) | R-ASYNC | A01,A02,A03 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-TX-006](../520_ケース/522_トランザクション・データ.md#it-tx-006) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-007](../520_ケース/522_トランザクション・データ.md#it-tx-007) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-008](../520_ケース/522_トランザクション・データ.md#it-tx-008) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-009](../520_ケース/522_トランザクション・データ.md#it-tx-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-4075157092d427"></a>
## B3-4075157092d427

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-001](../520_ケース/526_MQ・非同期・容量.md#it-asy-001) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-002](../520_ケース/526_MQ・非同期・容量.md#it-asy-002) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-003](../520_ケース/526_MQ・非同期・容量.md#it-asy-003) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-004](../520_ケース/526_MQ・非同期・容量.md#it-asy-004) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-005](../520_ケース/526_MQ・非同期・容量.md#it-asy-005) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-006](../520_ケース/526_MQ・非同期・容量.md#it-asy-006) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-ASY-008](../520_ケース/526_MQ・非同期・容量.md#it-asy-008) | R-ASYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-ASY-020](../520_ケース/526_MQ・非同期・容量.md#it-asy-020) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-MQ,O-TIME,O-WIRE |

<a id="b3-079a50c40c47e4"></a>
## B3-079a50c40c47e4

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-001](../520_ケース/526_MQ・非同期・容量.md#it-asy-001) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-002](../520_ケース/526_MQ・非同期・容量.md#it-asy-002) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-003](../520_ケース/526_MQ・非同期・容量.md#it-asy-003) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-004](../520_ケース/526_MQ・非同期・容量.md#it-asy-004) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-005](../520_ケース/526_MQ・非同期・容量.md#it-asy-005) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-006](../520_ケース/526_MQ・非同期・容量.md#it-asy-006) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-ASY-008](../520_ケース/526_MQ・非同期・容量.md#it-asy-008) | R-ASYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-ASY-020](../520_ケース/526_MQ・非同期・容量.md#it-asy-020) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-048a96856b514b"></a>
## B3-048a96856b514b

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-021](../520_ケース/526_MQ・非同期・容量.md#it-asy-021) | R-ASYNC | A01,A02 | O-DB,O-TIME,O-WIRE |
| [IT-ASY-022](../520_ケース/526_MQ・非同期・容量.md#it-asy-022) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-WIRE |
| [IT-IF-026](../520_ケース/521_インターフェース.md#it-if-026) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-027](../520_ケース/521_インターフェース.md#it-if-027) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-028](../520_ケース/521_インターフェース.md#it-if-028) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-029](../520_ケース/521_インターフェース.md#it-if-029) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-030](../520_ケース/521_インターフェース.md#it-if-030) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-031](../520_ケース/521_インターフェース.md#it-if-031) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-f6a0d6c0d0f933"></a>
## B3-f6a0d6c0d0f933

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-001](../520_ケース/525_運用・復旧・監視.md#it-log-001) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-LOG-002](../520_ケース/525_運用・復旧・監視.md#it-log-002) | R-WLOG | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-LOG-003](../520_ケース/525_運用・復旧・監視.md#it-log-003) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-LOG-020](../520_ケース/525_運用・復旧・監視.md#it-log-020) | R-WLOG | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-LOG-021](../520_ケース/525_運用・復旧・監視.md#it-log-021) | R-WLOG | A01,A02,A03,A04 | O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b3-bc3975cd13138e"></a>
## B3-bc3975cd13138e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-LOG-001](../520_ケース/525_運用・復旧・監視.md#it-log-001) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-LOG-002](../520_ケース/525_運用・復旧・監視.md#it-log-002) | R-WLOG | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-LOG-003](../520_ケース/525_運用・復旧・監視.md#it-log-003) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-LOG-020](../520_ケース/525_運用・復旧・監視.md#it-log-020) | R-WLOG | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-LOG-021](../520_ケース/525_運用・復旧・監視.md#it-log-021) | R-WLOG | A01,A02,A03,A04 | O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b3-952186f9c8b9a9"></a>
## B3-952186f9c8b9a9

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-001](../520_ケース/523_認証・権限・セキュリティ.md#it-http-001) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-TX-053](../520_ケース/522_トランザクション・データ.md#it-tx-053) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-WIRE |
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b3-3fc8626df85acb"></a>
## B3-3fc8626df85acb

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-751e63dd961d63"></a>
## B3-751e63dd961d63

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-cab38af680ff78"></a>
## B3-cab38af680ff78

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |

<a id="b3-682c9ea3bdb06a"></a>
## B3-682c9ea3bdb06a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-010](../520_ケース/521_インターフェース.md#it-http-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-011](../520_ケース/521_インターフェース.md#it-http-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-HTTP-012](../520_ケース/521_インターフェース.md#it-http-012) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-WIRE |
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-f1faa251178489"></a>
## B3-f1faa251178489

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-010](../520_ケース/521_インターフェース.md#it-http-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-011](../520_ケース/521_インターフェース.md#it-http-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-HTTP-012](../520_ケース/521_インターフェース.md#it-http-012) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-WIRE |
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-003](../520_ケース/521_インターフェース.md#it-if-003) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-006](../520_ケース/521_インターフェース.md#it-if-006) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-007](../520_ケース/521_インターフェース.md#it-if-007) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-721b817745fe9d"></a>
## B3-721b817745fe9d

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-010](../520_ケース/521_インターフェース.md#it-http-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-011](../520_ケース/521_インターフェース.md#it-http-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-HTTP-012](../520_ケース/521_インターフェース.md#it-http-012) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-WIRE |
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-4d038e0d8628ac"></a>
## B3-4d038e0d8628ac

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-BOUND-002](../520_ケース/523_認証・権限・セキュリティ.md#it-bound-002) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-010](../520_ケース/521_インターフェース.md#it-http-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-011](../520_ケース/521_インターフェース.md#it-http-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-HTTP-012](../520_ケース/521_インターフェース.md#it-http-012) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-WIRE |
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-2475d36dfa3282"></a>
## B3-2475d36dfa3282

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-BOUND-001](../520_ケース/523_認証・権限・セキュリティ.md#it-bound-001) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-010](../520_ケース/521_インターフェース.md#it-http-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-011](../520_ケース/521_インターフェース.md#it-http-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-HTTP-012](../520_ケース/521_インターフェース.md#it-http-012) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-WIRE |
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-1a76f82a3c68c2"></a>
## B3-1a76f82a3c68c2

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-013](../520_ケース/521_インターフェース.md#it-http-013) | R-FILE | A01,A02 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-7ceb67b95a79fd"></a>
## B3-7ceb67b95a79fd

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-002](../520_ケース/522_トランザクション・データ.md#it-data-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-WIRE |
| [IT-HTTP-001](../520_ケース/523_認証・権限・セキュリティ.md#it-http-001) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-8dc92879a3617b"></a>
## B3-8dc92879a3617b

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-002](../520_ケース/522_トランザクション・データ.md#it-data-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-032](../520_ケース/522_トランザクション・データ.md#it-data-032) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-MQ,O-WIRE |
| [IT-HTTP-001](../520_ケース/523_認証・権限・セキュリティ.md#it-http-001) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-b07075f04651ff"></a>
## B3-b07075f04651ff

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-040](../520_ケース/527_性能・資源・Logout混在.md#it-perf-040) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-010](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-010) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-a2f7d68bd95f1e"></a>
## B3-a2f7d68bd95f1e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-010](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-010) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-7cb671a341c7af"></a>
## B3-7cb671a341c7af

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-001](../520_ケース/523_認証・権限・セキュリティ.md#it-http-001) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-024](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-024) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-WIRE |

<a id="b3-174df802c790ad"></a>
## B3-174df802c790ad

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-001](../520_ケース/523_認証・権限・セキュリティ.md#it-http-001) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-024](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-024) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-WIRE |

<a id="b3-a4a54b81158062"></a>
## B3-a4a54b81158062

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-BOUND-002](../520_ケース/523_認証・権限・セキュリティ.md#it-bound-002) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-WIRE |
| [IT-PERF-040](../520_ケース/527_性能・資源・Logout混在.md#it-perf-040) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-001](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-SEC-013](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-013) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-2e6fe84741481a"></a>
## B3-2e6fe84741481a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-BOUND-002](../520_ケース/523_認証・権限・セキュリティ.md#it-bound-002) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-WIRE |
| [IT-PERF-040](../520_ケース/527_性能・資源・Logout混在.md#it-perf-040) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-001](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-SEC-013](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-013) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-024](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-024) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-WIRE |

<a id="b3-6544491feef95b"></a>
## B3-6544491feef95b

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-002](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-002) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-003](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-003) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-TIME,O-WIRE |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |
| [IT-SEC-032](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-032) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-LOG,O-TIME,O-WIRE |

<a id="b3-c1cf425bcc5902"></a>
## B3-c1cf425bcc5902

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-008](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-008) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-030](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-030) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-031](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-031) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b3-037f88959e7022"></a>
## B3-037f88959e7022

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-008](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-008) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-024](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-024) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-030](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-030) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-031](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-031) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |

<a id="b3-ed088f4092710a"></a>
## B3-ed088f4092710a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-b53ed2f098db8c"></a>
## B3-b53ed2f098db8c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-026](../520_ケース/521_インターフェース.md#it-if-026) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-027](../520_ケース/521_インターフェース.md#it-if-027) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-028](../520_ケース/521_インターフェース.md#it-if-028) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-029](../520_ケース/521_インターフェース.md#it-if-029) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-030](../520_ケース/521_インターフェース.md#it-if-030) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-031](../520_ケース/521_インターフェース.md#it-if-031) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-025caf25873641"></a>
## B3-025caf25873641

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-010](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-010) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-032](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-032) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-LOG,O-TIME,O-WIRE |

<a id="b3-fc20c1db6f379f"></a>
## B3-fc20c1db6f379f

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-5dead0bc8fdd14"></a>
## B3-5dead0bc8fdd14

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-SEC-013](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-013) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-37026f978a0f79"></a>
## B3-37026f978a0f79

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-002](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-002) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-d0c07a4e98ed79"></a>
## B3-d0c07a4e98ed79

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-BOUND-001](../520_ケース/523_認証・権限・セキュリティ.md#it-bound-001) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-010](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-010) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-5a25e5ca6ac107"></a>
## B3-5a25e5ca6ac107

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-010](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-010) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-032](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-032) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOCK,O-LOG,O-TIME,O-WIRE |

<a id="b3-976102bb319f39"></a>
## B3-976102bb319f39

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-5a746a8dfbb886"></a>
## B3-5a746a8dfbb886

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |

<a id="b3-68da5522a7df59"></a>
## B3-68da5522a7df59

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |

<a id="b3-dea3c7e5565390"></a>
## B3-dea3c7e5565390

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-f3712368414546"></a>
## B3-f3712368414546

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-OPS-011](../520_ケース/525_運用・復旧・監視.md#it-ops-011) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |

<a id="b3-edae87aa2e944f"></a>
## B3-edae87aa2e944f

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-4d982ae6a700d8"></a>
## B3-4d982ae6a700d8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |
| [IT-NET-001](../520_ケース/522_トランザクション・データ.md#it-net-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-MQ,O-TIME,O-WIRE |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-3781a0bbe4f243"></a>
## B3-3781a0bbe4f243

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-021](../520_ケース/525_運用・復旧・監視.md#it-ops-021) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-baaecccaa47ac7"></a>
## B3-baaecccaa47ac7

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-031](../520_ケース/526_MQ・非同期・容量.md#it-mq-031) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-c53f6c7d21efa4"></a>
## B3-c53f6c7d21efa4

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-f3e6a90667d905"></a>
## B3-f3e6a90667d905

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b3-f446dbdb365ae4"></a>
## B3-f446dbdb365ae4

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-033](../520_ケース/526_MQ・非同期・容量.md#it-mq-033) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-MQ-034](../520_ケース/526_MQ・非同期・容量.md#it-mq-034) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-035](../520_ケース/526_MQ・非同期・容量.md#it-mq-035) | R-OPS | A01,A02,A03,A04 | O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-021](../520_ケース/525_運用・復旧・監視.md#it-ops-021) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-010](../520_ケース/522_トランザクション・データ.md#it-tx-010) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-b8dee476b5c2bd"></a>
## B3-b8dee476b5c2bd

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-005](../520_ケース/521_インターフェース.md#it-if-005) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-032](../520_ケース/521_インターフェース.md#it-if-032) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b3-7096f1ffa622ab"></a>
## B3-7096f1ffa622ab

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-005](../520_ケース/521_インターフェース.md#it-if-005) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-032](../520_ケース/521_インターフェース.md#it-if-032) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-002](../520_ケース/526_MQ・非同期・容量.md#it-mq-002) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-MQ-003](../520_ケース/526_MQ・非同期・容量.md#it-mq-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-MQ,O-OS,O-WIRE |
| [IT-PERF-045](../520_ケース/527_性能・資源・Logout混在.md#it-perf-045) | R-FILE | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b3-5cdc89feecf552"></a>
## B3-5cdc89feecf552

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-a941f017da2c19"></a>
## B3-a941f017da2c19

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-027](../520_ケース/521_インターフェース.md#it-if-027) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-028](../520_ケース/521_インターフェース.md#it-if-028) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-6ae545307006e0"></a>
## B3-6ae545307006e0

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-005](../520_ケース/521_インターフェース.md#it-if-005) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-2f15242afd714c"></a>
## B3-2f15242afd714c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-020](../520_ケース/524_ファイル・メディア・Range.md#it-file-020) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-021](../520_ケース/524_ファイル・メディア・Range.md#it-file-021) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-022](../520_ケース/524_ファイル・メディア・Range.md#it-file-022) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-023](../520_ケース/524_ファイル・メディア・Range.md#it-file-023) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-027](../520_ケース/524_ファイル・メディア・Range.md#it-file-027) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-028](../520_ケース/524_ファイル・メディア・Range.md#it-file-028) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-029](../520_ケース/524_ファイル・メディア・Range.md#it-file-029) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-030](../520_ケース/524_ファイル・メディア・Range.md#it-file-030) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-031](../520_ケース/524_ファイル・メディア・Range.md#it-file-031) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-IF-008](../520_ケース/521_インターフェース.md#it-if-008) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-9d4c69b701bd66"></a>
## B3-9d4c69b701bd66

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-008](../520_ケース/521_インターフェース.md#it-if-008) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-6319fd2fcbdb8c"></a>
## B3-6319fd2fcbdb8c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-027](../520_ケース/521_インターフェース.md#it-if-027) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-78f982354ac4cc"></a>
## B3-78f982354ac4cc

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-028](../520_ケース/521_インターフェース.md#it-if-028) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-487fb3e9884fd0"></a>
## B3-487fb3e9884fd0

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-003](../520_ケース/521_インターフェース.md#it-if-003) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-005](../520_ケース/521_インターフェース.md#it-if-005) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-032](../520_ケース/521_インターフェース.md#it-if-032) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-TX-017](../520_ケース/522_トランザクション・データ.md#it-tx-017) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOG,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |

<a id="b3-1a50a46d63f5e6"></a>
## B3-1a50a46d63f5e6

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-002](../520_ケース/521_インターフェース.md#it-if-002) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-ed64d59c7f98e4"></a>
## B3-ed64d59c7f98e4

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-003](../520_ケース/521_インターフェース.md#it-if-003) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-b421956381b27c"></a>
## B3-b421956381b27c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-004](../520_ケース/521_インターフェース.md#it-if-004) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-5c62e1b927d561"></a>
## B3-5c62e1b927d561

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-006](../520_ケース/521_インターフェース.md#it-if-006) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-b7d658d6ef8776"></a>
## B3-b7d658d6ef8776

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-007](../520_ケース/521_インターフェース.md#it-if-007) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-20c75d80ed5c51"></a>
## B3-20c75d80ed5c51

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-009](../520_ケース/521_インターフェース.md#it-if-009) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-cce0387b4ae734"></a>
## B3-cce0387b4ae734

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-010](../520_ケース/521_インターフェース.md#it-if-010) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-b2eaa10c9523b0"></a>
## B3-b2eaa10c9523b0

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-011](../520_ケース/521_インターフェース.md#it-if-011) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-b226c1b5cdfdd9"></a>
## B3-b226c1b5cdfdd9

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-012](../520_ケース/521_インターフェース.md#it-if-012) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-962a0855646d3c"></a>
## B3-962a0855646d3c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-013](../520_ケース/521_インターフェース.md#it-if-013) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-ed08518dbfefec"></a>
## B3-ed08518dbfefec

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-014](../520_ケース/521_インターフェース.md#it-if-014) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-bdf6a0e115731c"></a>
## B3-bdf6a0e115731c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-015](../520_ケース/521_インターフェース.md#it-if-015) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-e2d2943c6ab882"></a>
## B3-e2d2943c6ab882

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-016](../520_ケース/521_インターフェース.md#it-if-016) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-d930cec42c6aa9"></a>
## B3-d930cec42c6aa9

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-668dbc3f82a76a"></a>
## B3-668dbc3f82a76a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-018](../520_ケース/521_インターフェース.md#it-if-018) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-9270f0c431f77e"></a>
## B3-9270f0c431f77e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-019](../520_ケース/521_インターフェース.md#it-if-019) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-bf96f948edd2f0"></a>
## B3-bf96f948edd2f0

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-020](../520_ケース/521_インターフェース.md#it-if-020) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-ba030c4a76ae0e"></a>
## B3-ba030c4a76ae0e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-021](../520_ケース/521_インターフェース.md#it-if-021) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-d687ca48a4483a"></a>
## B3-d687ca48a4483a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-022](../520_ケース/521_インターフェース.md#it-if-022) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-d02b119eb0f0f7"></a>
## B3-d02b119eb0f0f7

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-023](../520_ケース/521_インターフェース.md#it-if-023) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-b2f8b175e1c976"></a>
## B3-b2f8b175e1c976

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-024](../520_ケース/521_インターフェース.md#it-if-024) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-18cf3e6f657947"></a>
## B3-18cf3e6f657947

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-025](../520_ケース/521_インターフェース.md#it-if-025) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-79b43eedd72259"></a>
## B3-79b43eedd72259

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-026](../520_ケース/521_インターフェース.md#it-if-026) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-6d086443fee1ff"></a>
## B3-6d086443fee1ff

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-029](../520_ケース/521_インターフェース.md#it-if-029) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-e80b192c7a9b4d"></a>
## B3-e80b192c7a9b4d

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-030](../520_ケース/521_インターフェース.md#it-if-030) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-8f8244de95cc99"></a>
## B3-8f8244de95cc99

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-031](../520_ケース/521_インターフェース.md#it-if-031) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-e86764c3cf7c31"></a>
## B3-e86764c3cf7c31

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-032](../520_ケース/521_インターフェース.md#it-if-032) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-3bc18383871055"></a>
## B3-3bc18383871055

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-c8cbde71b3dd5e"></a>
## B3-c8cbde71b3dd5e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-018](../520_ケース/521_インターフェース.md#it-if-018) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-026](../520_ケース/521_インターフェース.md#it-if-026) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |

<a id="b3-0ec81e35b30d6c"></a>
## B3-0ec81e35b30d6c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-043](../520_ケース/522_トランザクション・データ.md#it-tx-043) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-952e9df429bed9"></a>
## B3-952e9df429bed9

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-450c04715bbdee"></a>
## B3-450c04715bbdee

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-008](../520_ケース/522_トランザクション・データ.md#it-tx-008) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-b6a89d17feeb42"></a>
## B3-b6a89d17feeb42

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-021](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-021) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-WIRE |
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-643fdc199fb782"></a>
## B3-643fdc199fb782

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-4a4678bcf6a8de"></a>
## B3-4a4678bcf6a8de

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-021](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-021) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-WIRE |
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |
| [IT-TX-011](../520_ケース/522_トランザクション・データ.md#it-tx-011) | R-SYNC | A01,A02 | O-DB,O-MQ,O-WIRE |
| [IT-TX-012](../520_ケース/522_トランザクション・データ.md#it-tx-012) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-013](../520_ケース/522_トランザクション・データ.md#it-tx-013) | R-SYNC | A01,A02 | O-DB,O-LOG,O-WIRE |
| [IT-TX-014](../520_ケース/522_トランザクション・データ.md#it-tx-014) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-017](../520_ケース/522_トランザクション・データ.md#it-tx-017) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOG,O-WIRE |
| [IT-TX-018](../520_ケース/522_トランザクション・データ.md#it-tx-018) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |
| [IT-TX-041](../520_ケース/522_トランザクション・データ.md#it-tx-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-WIRE |
| [IT-TX-044](../520_ケース/522_トランザクション・データ.md#it-tx-044) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-LOCK,O-WIRE |

<a id="b3-53e90dc5b65d3f"></a>
## B3-53e90dc5b65d3f

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-021](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-021) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-WIRE |
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |
| [IT-TX-011](../520_ケース/522_トランザクション・データ.md#it-tx-011) | R-SYNC | A01,A02 | O-DB,O-MQ,O-WIRE |
| [IT-TX-012](../520_ケース/522_トランザクション・データ.md#it-tx-012) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-013](../520_ケース/522_トランザクション・データ.md#it-tx-013) | R-SYNC | A01,A02 | O-DB,O-LOG,O-WIRE |
| [IT-TX-014](../520_ケース/522_トランザクション・データ.md#it-tx-014) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-017](../520_ケース/522_トランザクション・データ.md#it-tx-017) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOG,O-WIRE |
| [IT-TX-018](../520_ケース/522_トランザクション・データ.md#it-tx-018) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |
| [IT-TX-041](../520_ケース/522_トランザクション・データ.md#it-tx-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-WIRE |
| [IT-TX-044](../520_ケース/522_トランザクション・データ.md#it-tx-044) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-LOCK,O-WIRE |
| [IT-TX-053](../520_ケース/522_トランザクション・データ.md#it-tx-053) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-WIRE |

<a id="b3-fe8eebb7237acb"></a>
## B3-fe8eebb7237acb

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-021](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-021) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-WIRE |
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |
| [IT-TX-011](../520_ケース/522_トランザクション・データ.md#it-tx-011) | R-SYNC | A01,A02 | O-DB,O-MQ,O-WIRE |
| [IT-TX-012](../520_ケース/522_トランザクション・データ.md#it-tx-012) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-013](../520_ケース/522_トランザクション・データ.md#it-tx-013) | R-SYNC | A01,A02 | O-DB,O-LOG,O-WIRE |
| [IT-TX-014](../520_ケース/522_トランザクション・データ.md#it-tx-014) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-017](../520_ケース/522_トランザクション・データ.md#it-tx-017) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOG,O-WIRE |
| [IT-TX-018](../520_ケース/522_トランザクション・データ.md#it-tx-018) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |
| [IT-TX-041](../520_ケース/522_トランザクション・データ.md#it-tx-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-WIRE |
| [IT-TX-044](../520_ケース/522_トランザクション・データ.md#it-tx-044) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-LOCK,O-WIRE |

<a id="b3-f187523419f230"></a>
## B3-f187523419f230

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-PERF-045](../520_ケース/527_性能・資源・Logout混在.md#it-perf-045) | R-FILE | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-021](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-021) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-WIRE |
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |
| [IT-TX-011](../520_ケース/522_トランザクション・データ.md#it-tx-011) | R-SYNC | A01,A02 | O-DB,O-MQ,O-WIRE |
| [IT-TX-012](../520_ケース/522_トランザクション・データ.md#it-tx-012) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-013](../520_ケース/522_トランザクション・データ.md#it-tx-013) | R-SYNC | A01,A02 | O-DB,O-LOG,O-WIRE |
| [IT-TX-014](../520_ケース/522_トランザクション・データ.md#it-tx-014) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-017](../520_ケース/522_トランザクション・データ.md#it-tx-017) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOG,O-WIRE |
| [IT-TX-018](../520_ケース/522_トランザクション・データ.md#it-tx-018) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |
| [IT-TX-041](../520_ケース/522_トランザクション・データ.md#it-tx-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-WIRE |
| [IT-TX-044](../520_ケース/522_トランザクション・データ.md#it-tx-044) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-LOCK,O-WIRE |

<a id="b3-456f866d5fadda"></a>
## B3-456f866d5fadda

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-SEC-020](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-020) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-WIRE |
| [IT-SEC-021](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-021) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-WIRE |
| [IT-SEC-022](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-022) | R-SESSION | A01,A02,A03 | O-DB,O-WIRE |
| [IT-TX-011](../520_ケース/522_トランザクション・データ.md#it-tx-011) | R-SYNC | A01,A02 | O-DB,O-MQ,O-WIRE |
| [IT-TX-012](../520_ケース/522_トランザクション・データ.md#it-tx-012) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-TX-013](../520_ケース/522_トランザクション・データ.md#it-tx-013) | R-SYNC | A01,A02 | O-DB,O-LOG,O-WIRE |
| [IT-TX-014](../520_ケース/522_トランザクション・データ.md#it-tx-014) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-017](../520_ケース/522_トランザクション・データ.md#it-tx-017) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOG,O-WIRE |
| [IT-TX-018](../520_ケース/522_トランザクション・データ.md#it-tx-018) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |
| [IT-TX-041](../520_ケース/522_トランザクション・データ.md#it-tx-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-WIRE |
| [IT-TX-044](../520_ケース/522_トランザクション・データ.md#it-tx-044) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-LOCK,O-WIRE |

<a id="b3-b30214b64a383a"></a>
## B3-b30214b64a383a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-TX-006](../520_ケース/522_トランザクション・データ.md#it-tx-006) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-007](../520_ケース/522_トランザクション・データ.md#it-tx-007) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-008](../520_ケース/522_トランザクション・データ.md#it-tx-008) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-009](../520_ケース/522_トランザクション・データ.md#it-tx-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |
| [IT-TX-043](../520_ケース/522_トランザクション・データ.md#it-tx-043) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-fe5670767fbdfe"></a>
## B3-fe5670767fbdfe

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-043](../520_ケース/527_性能・資源・Logout混在.md#it-perf-043) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-006](../520_ケース/522_トランザクション・データ.md#it-tx-006) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-007](../520_ケース/522_トランザクション・データ.md#it-tx-007) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-008](../520_ケース/522_トランザクション・データ.md#it-tx-008) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-009](../520_ケース/522_トランザクション・データ.md#it-tx-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |
| [IT-TX-043](../520_ケース/522_トランザクション・データ.md#it-tx-043) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-bec15db8748ea1"></a>
## B3-bec15db8748ea1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-030](../520_ケース/526_MQ・非同期・容量.md#it-mq-030) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-OS,O-TIME |
| [IT-TX-006](../520_ケース/522_トランザクション・データ.md#it-tx-006) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-007](../520_ケース/522_トランザクション・データ.md#it-tx-007) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-008](../520_ケース/522_トランザクション・データ.md#it-tx-008) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-009](../520_ケース/522_トランザクション・データ.md#it-tx-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |
| [IT-TX-043](../520_ケース/522_トランザクション・データ.md#it-tx-043) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-24a91992aa6660"></a>
## B3-24a91992aa6660

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-001](../520_ケース/525_運用・復旧・監視.md#it-log-001) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-LOG-020](../520_ケース/525_運用・復旧・監視.md#it-log-020) | R-WLOG | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-LOG-021](../520_ケース/525_運用・復旧・監視.md#it-log-021) | R-WLOG | A01,A02,A03,A04 | O-HTTP,O-LOG,O-OS,O-WIRE |

<a id="b3-74d8ef067b7b2e"></a>
## B3-74d8ef067b7b2e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-001](../520_ケース/526_MQ・非同期・容量.md#it-asy-001) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-002](../520_ケース/526_MQ・非同期・容量.md#it-asy-002) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-003](../520_ケース/526_MQ・非同期・容量.md#it-asy-003) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-004](../520_ケース/526_MQ・非同期・容量.md#it-asy-004) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-005](../520_ケース/526_MQ・非同期・容量.md#it-asy-005) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-006](../520_ケース/526_MQ・非同期・容量.md#it-asy-006) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-ASY-008](../520_ケース/526_MQ・非同期・容量.md#it-asy-008) | R-ASYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-ASY-020](../520_ケース/526_MQ・非同期・容量.md#it-asy-020) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-023](../520_ケース/526_MQ・非同期・容量.md#it-asy-023) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |

<a id="b3-972cc58054a1ee"></a>
## B3-972cc58054a1ee

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-009](../520_ケース/526_MQ・非同期・容量.md#it-asy-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-MQ,O-WIRE |
| [IT-DATA-003](../520_ケース/522_トランザクション・データ.md#it-data-003) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-009](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-009) | R-SESSION | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-011](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-011) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-207a26a1cab1a1"></a>
## B3-207a26a1cab1a1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |
| [IT-OPS-027](../520_ケース/525_運用・復旧・監視.md#it-ops-027) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-LOG |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-043](../520_ケース/525_運用・復旧・監視.md#it-ops-043) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30 | O-DB,O-FS,O-LOCK,O-LOG,O-OS |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |

<a id="b3-17df50d0066cb1"></a>
## B3-17df50d0066cb1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-009](../520_ケース/526_MQ・非同期・容量.md#it-asy-009) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-MQ,O-WIRE |
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |
| [IT-OPS-027](../520_ケース/525_運用・復旧・監視.md#it-ops-027) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-LOG |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-043](../520_ケース/525_運用・復旧・監視.md#it-ops-043) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30 | O-DB,O-FS,O-LOCK,O-LOG,O-OS |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |

<a id="b3-ae56385da99ab8"></a>
## B3-ae56385da99ab8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-020](../520_ケース/526_MQ・非同期・容量.md#it-asy-020) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-LOG-010](../520_ケース/525_運用・復旧・監視.md#it-log-010) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-3139ab0df22d99"></a>
## B3-3139ab0df22d99

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-020](../520_ケース/526_MQ・非同期・容量.md#it-asy-020) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-LOG-010](../520_ケース/525_運用・復旧・監視.md#it-log-010) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-a025e93b948247"></a>
## B3-a025e93b948247

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-028](../520_ケース/525_運用・復旧・監視.md#it-ops-028) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-TIME |

<a id="b3-0060ca2cd250d8"></a>
## B3-0060ca2cd250d8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |

<a id="b3-135a0b004b2b4c"></a>
## B3-135a0b004b2b4c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-4d3747d8d15b29"></a>
## B3-4d3747d8d15b29

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-OPS-015](../520_ケース/525_運用・復旧・監視.md#it-ops-015) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS |
| [IT-OPS-016](../520_ケース/525_運用・復旧・監視.md#it-ops-016) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-025](../520_ケース/525_運用・復旧・監視.md#it-ops-025) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-TIME |
| [IT-OPS-026](../520_ケース/525_運用・復旧・監視.md#it-ops-026) | R-OPS | A01,A02 | O-DB,O-TIME |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-a550b8e22f3a67"></a>
## B3-a550b8e22f3a67

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-c14db5b8039764"></a>
## B3-c14db5b8039764

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-025](../520_ケース/525_運用・復旧・監視.md#it-ops-025) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-6633216ae7e938"></a>
## B3-6633216ae7e938

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-021](../520_ケース/522_トランザクション・データ.md#it-data-021) | R-SYNC | A01,A02,A03 | O-DB,O-TIME,O-WIRE |
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-3d51aaf9d68b17"></a>
## B3-3d51aaf9d68b17

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-021](../520_ケース/522_トランザクション・データ.md#it-data-021) | R-SYNC | A01,A02,A03 | O-DB,O-TIME,O-WIRE |
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-TX-015](../520_ケース/522_トランザクション・データ.md#it-tx-015) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-1100e00b83eac8"></a>
## B3-1100e00b83eac8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-021](../520_ケース/522_トランザクション・データ.md#it-data-021) | R-SYNC | A01,A02,A03 | O-DB,O-TIME,O-WIRE |
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-2a92eca4a9cedf"></a>
## B3-2a92eca4a9cedf

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-021](../520_ケース/522_トランザクション・データ.md#it-data-021) | R-SYNC | A01,A02,A03 | O-DB,O-TIME,O-WIRE |
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-053](../520_ケース/522_トランザクション・データ.md#it-tx-053) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-WIRE |

<a id="b3-4b34df06b32c36"></a>
## B3-4b34df06b32c36

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-020](../520_ケース/522_トランザクション・データ.md#it-data-020) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-030](../520_ケース/522_トランザクション・データ.md#it-data-030) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-031](../520_ケース/522_トランザクション・データ.md#it-data-031) | R-SYNC | A01,A02 | O-DB,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-IF-009](../520_ケース/521_インターフェース.md#it-if-009) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-016](../520_ケース/521_インターフェース.md#it-if-016) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-TX-051](../520_ケース/522_トランザクション・データ.md#it-tx-051) | R-FILE | A01,A02 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |

<a id="b3-cf55cfa18ade39"></a>
## B3-cf55cfa18ade39

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-030](../520_ケース/522_トランザクション・データ.md#it-data-030) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-031](../520_ケース/522_トランザクション・データ.md#it-data-031) | R-SYNC | A01,A02 | O-DB,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-IF-009](../520_ケース/521_インターフェース.md#it-if-009) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-016](../520_ケース/521_インターフェース.md#it-if-016) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-TX-051](../520_ケース/522_トランザクション・データ.md#it-tx-051) | R-FILE | A01,A02 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |

<a id="b3-0f526a0e6e7190"></a>
## B3-0f526a0e6e7190

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-030](../520_ケース/522_トランザクション・データ.md#it-data-030) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-031](../520_ケース/522_トランザクション・データ.md#it-data-031) | R-SYNC | A01,A02 | O-DB,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-IF-009](../520_ケース/521_インターフェース.md#it-if-009) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-016](../520_ケース/521_インターフェース.md#it-if-016) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-TX-051](../520_ケース/522_トランザクション・データ.md#it-tx-051) | R-FILE | A01,A02 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |

<a id="b3-35f956ab46e248"></a>
## B3-35f956ab46e248

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DATA-001](../520_ケース/522_トランザクション・データ.md#it-data-001) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-030](../520_ケース/522_トランザクション・データ.md#it-data-030) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-WIRE |
| [IT-DATA-031](../520_ケース/522_トランザクション・データ.md#it-data-031) | R-SYNC | A01,A02 | O-DB,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-050](../520_ケース/524_ファイル・メディア・Range.md#it-file-050) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-OS,O-WIRE |
| [IT-IF-009](../520_ケース/521_インターフェース.md#it-if-009) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-016](../520_ケース/521_インターフェース.md#it-if-016) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-TX-051](../520_ケース/522_トランザクション・データ.md#it-tx-051) | R-FILE | A01,A02 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |

<a id="b3-c1ce1e3db0fa1d"></a>
## B3-c1ce1e3db0fa1d

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-SEC-001](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-SEC-006](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-006) | R-SYNC | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-SEC-007](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-007) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-052](../520_ケース/522_トランザクション・データ.md#it-tx-052) | R-SYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-WIRE |

<a id="b3-e8e15a2f22a76d"></a>
## B3-e8e15a2f22a76d

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-REQ-001](../520_ケース/526_MQ・非同期・容量.md#it-req-001) | R-ASYNC | A01,A02,A03 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |
| [IT-TX-043](../520_ケース/522_トランザクション・データ.md#it-tx-043) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-e36d41cc971c55"></a>
## B3-e36d41cc971c55

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-REQ-001](../520_ケース/526_MQ・非同期・容量.md#it-req-001) | R-ASYNC | A01,A02,A03 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-TX-011](../520_ケース/522_トランザクション・データ.md#it-tx-011) | R-SYNC | A01,A02 | O-DB,O-MQ,O-WIRE |
| [IT-TX-040](../520_ケース/522_トランザクション・データ.md#it-tx-040) | R-SYNC | A01,A02 | O-DB,O-WIRE |
| [IT-TX-042](../520_ケース/522_トランザクション・データ.md#it-tx-042) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-MQ,O-TIME |
| [IT-TX-043](../520_ケース/522_トランザクション・データ.md#it-tx-043) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-TX-054](../520_ケース/522_トランザクション・データ.md#it-tx-054) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |

<a id="b3-3fe59bdde6a4ad"></a>
## B3-3fe59bdde6a4ad

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-002](../520_ケース/526_MQ・非同期・容量.md#it-asy-002) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-021](../520_ケース/526_MQ・非同期・容量.md#it-asy-021) | R-ASYNC | A01,A02 | O-DB,O-TIME,O-WIRE |
| [IT-ASY-022](../520_ケース/526_MQ・非同期・容量.md#it-asy-022) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-WIRE |
| [IT-ASY-023](../520_ケース/526_MQ・非同期・容量.md#it-asy-023) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-IF-029](../520_ケース/521_インターフェース.md#it-if-029) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-031](../520_ケース/521_インターフェース.md#it-if-031) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-14fd9b40884ec4"></a>
## B3-14fd9b40884ec4

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-002](../520_ケース/526_MQ・非同期・容量.md#it-asy-002) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-020](../520_ケース/526_MQ・非同期・容量.md#it-asy-020) | R-ASYNC | A01,A02,A03,A04,A05 | O-DB,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-021](../520_ケース/526_MQ・非同期・容量.md#it-asy-021) | R-ASYNC | A01,A02 | O-DB,O-TIME,O-WIRE |
| [IT-ASY-022](../520_ケース/526_MQ・非同期・容量.md#it-asy-022) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-WIRE |
| [IT-ASY-023](../520_ケース/526_MQ・非同期・容量.md#it-asy-023) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-IF-029](../520_ケース/521_インターフェース.md#it-if-029) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-031](../520_ケース/521_インターフェース.md#it-if-031) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-23aa7937176f47"></a>
## B3-23aa7937176f47

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-002](../520_ケース/526_MQ・非同期・容量.md#it-asy-002) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-ASY-003](../520_ケース/526_MQ・非同期・容量.md#it-asy-003) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-004](../520_ケース/526_MQ・非同期・容量.md#it-asy-004) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-005](../520_ケース/526_MQ・非同期・容量.md#it-asy-005) | R-ASYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-ASY-021](../520_ケース/526_MQ・非同期・容量.md#it-asy-021) | R-ASYNC | A01,A02 | O-DB,O-TIME,O-WIRE |
| [IT-ASY-022](../520_ケース/526_MQ・非同期・容量.md#it-asy-022) | R-ASYNC | A01,A02 | O-DB,O-LOCK,O-WIRE |
| [IT-ASY-023](../520_ケース/526_MQ・非同期・容量.md#it-asy-023) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-IF-029](../520_ケース/521_インターフェース.md#it-if-029) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-031](../520_ケース/521_インターフェース.md#it-if-031) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-8e14f35554b3e8"></a>
## B3-8e14f35554b3e8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |
| [IT-OPS-005](../520_ケース/525_運用・復旧・監視.md#it-ops-005) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-025](../520_ケース/525_運用・復旧・監視.md#it-ops-025) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-TIME |
| [IT-OPS-026](../520_ケース/525_運用・復旧・監視.md#it-ops-026) | R-OPS | A01,A02 | O-DB,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-37287b19677e66"></a>
## B3-37287b19677e66

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |
| [IT-OPS-005](../520_ケース/525_運用・復旧・監視.md#it-ops-005) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-025](../520_ケース/525_運用・復旧・監視.md#it-ops-025) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-TIME |
| [IT-OPS-026](../520_ケース/525_運用・復旧・監視.md#it-ops-026) | R-OPS | A01,A02 | O-DB,O-TIME |
| [IT-OPS-027](../520_ケース/525_運用・復旧・監視.md#it-ops-027) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-LOG |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-88362af08eb4ed"></a>
## B3-88362af08eb4ed

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-016](../520_ケース/525_運用・復旧・監視.md#it-ops-016) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-PERF-036](../520_ケース/527_性能・資源・Logout混在.md#it-perf-036) | R-SYNC | A01,A02 | O-DB,O-METRIC,O-TIME,O-WIRE |
| [IT-PERF-042](../520_ケース/527_性能・資源・Logout混在.md#it-perf-042) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-043](../520_ケース/527_性能・資源・Logout混在.md#it-perf-043) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-8df27d7357d54e"></a>
## B3-8df27d7357d54e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-053](../520_ケース/522_トランザクション・データ.md#it-tx-053) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-WIRE |
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b3-ae7524374f1ae8"></a>
## B3-ae7524374f1ae8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-4fd41e66cfdff1"></a>
## B3-4fd41e66cfdff1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |

<a id="b3-f87a885e1ab90a"></a>
## B3-f87a885e1ab90a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-010](../520_ケース/524_ファイル・メディア・Range.md#it-file-010) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-011](../520_ケース/524_ファイル・メディア・Range.md#it-file-011) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-012](../520_ケース/524_ファイル・メディア・Range.md#it-file-012) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-020](../520_ケース/524_ファイル・メディア・Range.md#it-file-020) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-021](../520_ケース/524_ファイル・メディア・Range.md#it-file-021) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-022](../520_ケース/524_ファイル・メディア・Range.md#it-file-022) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-023](../520_ケース/524_ファイル・メディア・Range.md#it-file-023) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-026](../520_ケース/524_ファイル・メディア・Range.md#it-file-026) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-027](../520_ケース/524_ファイル・メディア・Range.md#it-file-027) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-028](../520_ケース/524_ファイル・メディア・Range.md#it-file-028) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-029](../520_ケース/524_ファイル・メディア・Range.md#it-file-029) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-030](../520_ケース/524_ファイル・メディア・Range.md#it-file-030) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-031](../520_ケース/524_ファイル・メディア・Range.md#it-file-031) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-050](../520_ケース/524_ファイル・メディア・Range.md#it-file-050) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-OS,O-WIRE |
| [IT-FILE-051](../520_ケース/524_ファイル・メディア・Range.md#it-file-051) | R-FILE | A01,A02 | O-DB,O-FS,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-FILE-053](../520_ケース/524_ファイル・メディア・Range.md#it-file-053) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-060](../520_ケース/524_ファイル・メディア・Range.md#it-file-060) | R-FILE | A01,A02,A03 | O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-062](../520_ケース/524_ファイル・メディア・Range.md#it-file-062) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-FILE-064](../520_ケース/524_ファイル・メディア・Range.md#it-file-064) | R-OPS | A01,A02,A03,A04,A05,A06 | O-FS,O-HTTP,O-LOG,O-OS |

<a id="b3-b003478510de01"></a>
## B3-b003478510de01

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-010](../520_ケース/524_ファイル・メディア・Range.md#it-file-010) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-011](../520_ケース/524_ファイル・メディア・Range.md#it-file-011) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-012](../520_ケース/524_ファイル・メディア・Range.md#it-file-012) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-020](../520_ケース/524_ファイル・メディア・Range.md#it-file-020) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-021](../520_ケース/524_ファイル・メディア・Range.md#it-file-021) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-022](../520_ケース/524_ファイル・メディア・Range.md#it-file-022) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-023](../520_ケース/524_ファイル・メディア・Range.md#it-file-023) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-026](../520_ケース/524_ファイル・メディア・Range.md#it-file-026) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-027](../520_ケース/524_ファイル・メディア・Range.md#it-file-027) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-028](../520_ケース/524_ファイル・メディア・Range.md#it-file-028) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-029](../520_ケース/524_ファイル・メディア・Range.md#it-file-029) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-030](../520_ケース/524_ファイル・メディア・Range.md#it-file-030) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-031](../520_ケース/524_ファイル・メディア・Range.md#it-file-031) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-050](../520_ケース/524_ファイル・メディア・Range.md#it-file-050) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-OS,O-WIRE |
| [IT-FILE-051](../520_ケース/524_ファイル・メディア・Range.md#it-file-051) | R-FILE | A01,A02 | O-DB,O-FS,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-FILE-053](../520_ケース/524_ファイル・メディア・Range.md#it-file-053) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-060](../520_ケース/524_ファイル・メディア・Range.md#it-file-060) | R-FILE | A01,A02,A03 | O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-062](../520_ケース/524_ファイル・メディア・Range.md#it-file-062) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-FILE-064](../520_ケース/524_ファイル・メディア・Range.md#it-file-064) | R-OPS | A01,A02,A03,A04,A05,A06 | O-FS,O-HTTP,O-LOG,O-OS |
| [IT-RANGE-001](../520_ケース/524_ファイル・メディア・Range.md#it-range-001) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60 | O-FS,O-HTTP,O-METRIC |

<a id="b3-bdcac479a6e00f"></a>
## B3-bdcac479a6e00f

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-010](../520_ケース/524_ファイル・メディア・Range.md#it-file-010) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-011](../520_ケース/524_ファイル・メディア・Range.md#it-file-011) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-012](../520_ケース/524_ファイル・メディア・Range.md#it-file-012) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-020](../520_ケース/524_ファイル・メディア・Range.md#it-file-020) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-021](../520_ケース/524_ファイル・メディア・Range.md#it-file-021) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-022](../520_ケース/524_ファイル・メディア・Range.md#it-file-022) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-023](../520_ケース/524_ファイル・メディア・Range.md#it-file-023) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-026](../520_ケース/524_ファイル・メディア・Range.md#it-file-026) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-027](../520_ケース/524_ファイル・メディア・Range.md#it-file-027) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-028](../520_ケース/524_ファイル・メディア・Range.md#it-file-028) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-029](../520_ケース/524_ファイル・メディア・Range.md#it-file-029) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-030](../520_ケース/524_ファイル・メディア・Range.md#it-file-030) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-031](../520_ケース/524_ファイル・メディア・Range.md#it-file-031) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-050](../520_ケース/524_ファイル・メディア・Range.md#it-file-050) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-OS,O-WIRE |
| [IT-FILE-051](../520_ケース/524_ファイル・メディア・Range.md#it-file-051) | R-FILE | A01,A02 | O-DB,O-FS,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-FILE-053](../520_ケース/524_ファイル・メディア・Range.md#it-file-053) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-060](../520_ケース/524_ファイル・メディア・Range.md#it-file-060) | R-FILE | A01,A02,A03 | O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-062](../520_ケース/524_ファイル・メディア・Range.md#it-file-062) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-FILE-064](../520_ケース/524_ファイル・メディア・Range.md#it-file-064) | R-OPS | A01,A02,A03,A04,A05,A06 | O-FS,O-HTTP,O-LOG,O-OS |
| [IT-PERF-045](../520_ケース/527_性能・資源・Logout混在.md#it-perf-045) | R-FILE | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-47e62092bbfdf5"></a>
## B3-47e62092bbfdf5

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-010](../520_ケース/524_ファイル・メディア・Range.md#it-file-010) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-011](../520_ケース/524_ファイル・メディア・Range.md#it-file-011) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-012](../520_ケース/524_ファイル・メディア・Range.md#it-file-012) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-020](../520_ケース/524_ファイル・メディア・Range.md#it-file-020) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-021](../520_ケース/524_ファイル・メディア・Range.md#it-file-021) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-022](../520_ケース/524_ファイル・メディア・Range.md#it-file-022) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-023](../520_ケース/524_ファイル・メディア・Range.md#it-file-023) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-026](../520_ケース/524_ファイル・メディア・Range.md#it-file-026) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-027](../520_ケース/524_ファイル・メディア・Range.md#it-file-027) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-028](../520_ケース/524_ファイル・メディア・Range.md#it-file-028) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-029](../520_ケース/524_ファイル・メディア・Range.md#it-file-029) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-030](../520_ケース/524_ファイル・メディア・Range.md#it-file-030) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-031](../520_ケース/524_ファイル・メディア・Range.md#it-file-031) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-050](../520_ケース/524_ファイル・メディア・Range.md#it-file-050) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-OS,O-WIRE |
| [IT-FILE-051](../520_ケース/524_ファイル・メディア・Range.md#it-file-051) | R-FILE | A01,A02 | O-DB,O-FS,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-FILE-053](../520_ケース/524_ファイル・メディア・Range.md#it-file-053) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-060](../520_ケース/524_ファイル・メディア・Range.md#it-file-060) | R-FILE | A01,A02,A03 | O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-062](../520_ケース/524_ファイル・メディア・Range.md#it-file-062) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-FILE-064](../520_ケース/524_ファイル・メディア・Range.md#it-file-064) | R-OPS | A01,A02,A03,A04,A05,A06 | O-FS,O-HTTP,O-LOG,O-OS |
| [IT-PERF-032](../520_ケース/527_性能・資源・Logout混在.md#it-perf-032) | R-SYNC | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-22e97da5a4e415"></a>
## B3-22e97da5a4e415

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-001](../520_ケース/524_ファイル・メディア・Range.md#it-file-001) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-002](../520_ケース/524_ファイル・メディア・Range.md#it-file-002) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-003](../520_ケース/524_ファイル・メディア・Range.md#it-file-003) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-004](../520_ケース/524_ファイル・メディア・Range.md#it-file-004) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-005](../520_ケース/524_ファイル・メディア・Range.md#it-file-005) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-006](../520_ケース/524_ファイル・メディア・Range.md#it-file-006) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-010](../520_ケース/524_ファイル・メディア・Range.md#it-file-010) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-011](../520_ケース/524_ファイル・メディア・Range.md#it-file-011) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-012](../520_ケース/524_ファイル・メディア・Range.md#it-file-012) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-020](../520_ケース/524_ファイル・メディア・Range.md#it-file-020) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-021](../520_ケース/524_ファイル・メディア・Range.md#it-file-021) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-022](../520_ケース/524_ファイル・メディア・Range.md#it-file-022) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-023](../520_ケース/524_ファイル・メディア・Range.md#it-file-023) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-024](../520_ケース/524_ファイル・メディア・Range.md#it-file-024) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-025](../520_ケース/524_ファイル・メディア・Range.md#it-file-025) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-026](../520_ケース/524_ファイル・メディア・Range.md#it-file-026) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-027](../520_ケース/524_ファイル・メディア・Range.md#it-file-027) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-028](../520_ケース/524_ファイル・メディア・Range.md#it-file-028) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-029](../520_ケース/524_ファイル・メディア・Range.md#it-file-029) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-030](../520_ケース/524_ファイル・メディア・Range.md#it-file-030) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-031](../520_ケース/524_ファイル・メディア・Range.md#it-file-031) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-040](../520_ケース/524_ファイル・メディア・Range.md#it-file-040) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-TIME,O-WIRE |
| [IT-FILE-050](../520_ケース/524_ファイル・メディア・Range.md#it-file-050) | R-FILE | A01,A02,A03,A04 | O-DB,O-FS,O-OS,O-WIRE |
| [IT-FILE-051](../520_ケース/524_ファイル・メディア・Range.md#it-file-051) | R-FILE | A01,A02 | O-DB,O-FS,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-FILE-053](../520_ケース/524_ファイル・メディア・Range.md#it-file-053) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-054](../520_ケース/524_ファイル・メディア・Range.md#it-file-054) | R-MEDIA | A01,A02 | O-FS,O-HTTP,O-WIRE |
| [IT-FILE-060](../520_ケース/524_ファイル・メディア・Range.md#it-file-060) | R-FILE | A01,A02,A03 | O-FS,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |
| [IT-FILE-062](../520_ケース/524_ファイル・メディア・Range.md#it-file-062) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-FILE-064](../520_ケース/524_ファイル・メディア・Range.md#it-file-064) | R-OPS | A01,A02,A03,A04,A05,A06 | O-FS,O-HTTP,O-LOG,O-OS |

<a id="b3-500a48c26ab227"></a>
## B3-500a48c26ab227

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-054](../520_ケース/524_ファイル・メディア・Range.md#it-file-054) | R-MEDIA | A01,A02 | O-FS,O-HTTP,O-WIRE |
| [IT-FILE-055](../520_ケース/524_ファイル・メディア・Range.md#it-file-055) | R-MEDIA | A01,A02 | O-FS,O-HTTP |
| [IT-FILE-063](../520_ケース/524_ファイル・メディア・Range.md#it-file-063) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-009](../520_ケース/521_インターフェース.md#it-if-009) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-012](../520_ケース/521_インターフェース.md#it-if-012) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-016](../520_ケース/521_インターフェース.md#it-if-016) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-RANGE-001](../520_ケース/524_ファイル・メディア・Range.md#it-range-001) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60 | O-FS,O-HTTP,O-METRIC |
| [IT-RANGE-020](../520_ケース/524_ファイル・メディア・Range.md#it-range-020) | R-MEDIA | A01,A02,A03,A04,A05 | O-FS,O-HTTP,O-LOG,O-METRIC,O-OS,O-WIRE |
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-25970432c0f5bc"></a>
## B3-25970432c0f5bc

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-054](../520_ケース/524_ファイル・メディア・Range.md#it-file-054) | R-MEDIA | A01,A02 | O-FS,O-HTTP,O-WIRE |
| [IT-FILE-055](../520_ケース/524_ファイル・メディア・Range.md#it-file-055) | R-MEDIA | A01,A02 | O-FS,O-HTTP |
| [IT-FILE-063](../520_ケース/524_ファイル・メディア・Range.md#it-file-063) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34 | O-DB,O-FS,O-HTTP,O-LOG,O-WIRE |
| [IT-RANGE-001](../520_ケース/524_ファイル・メディア・Range.md#it-range-001) | R-MEDIA | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60 | O-FS,O-HTTP,O-METRIC |
| [IT-RANGE-020](../520_ケース/524_ファイル・メディア・Range.md#it-range-020) | R-MEDIA | A01,A02,A03,A04,A05 | O-FS,O-HTTP,O-LOG,O-METRIC,O-OS,O-WIRE |
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-3cacdd525c00ea"></a>
## B3-3cacdd525c00ea

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-006](../520_ケース/525_運用・復旧・監視.md#it-ops-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-OS,O-TIME |

<a id="b3-67232231289786"></a>
## B3-67232231289786

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-FILE-061](../520_ケース/524_ファイル・メディア・Range.md#it-file-061) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-FS,O-LOG,O-MQ,O-OS |
| [IT-LOG-010](../520_ケース/525_運用・復旧・監視.md#it-log-010) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-010](../520_ケース/527_性能・資源・Logout混在.md#it-perf-010) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-020](../520_ケース/527_性能・資源・Logout混在.md#it-perf-020) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-032](../520_ケース/527_性能・資源・Logout混在.md#it-perf-032) | R-SYNC | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-034](../520_ケース/527_性能・資源・Logout混在.md#it-perf-034) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b3-1147ebec0d66af"></a>
## B3-1147ebec0d66af

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-PERF-035](../520_ケース/527_性能・資源・Logout混在.md#it-perf-035) | R-OPS | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b3-aae5fd6f144fa1"></a>
## B3-aae5fd6f144fa1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-6fa34a1d7629d6"></a>
## B3-6fa34a1d7629d6

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-b59c4fe45debf1"></a>
## B3-b59c4fe45debf1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-7cbb35e5fb37b5"></a>
## B3-7cbb35e5fb37b5

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-003](../520_ケース/525_運用・復旧・監視.md#it-ops-003) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-f0d290df542340"></a>
## B3-f0d290df542340

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-4c1852a618a9cb"></a>
## B3-4c1852a618a9cb

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-bc661c92456d83"></a>
## B3-bc661c92456d83

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-051](../520_ケース/525_運用・復旧・監視.md#it-ops-051) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-ea3367e2b05fc6"></a>
## B3-ea3367e2b05fc6

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-051](../520_ケース/525_運用・復旧・監視.md#it-ops-051) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-1461871d02a045"></a>
## B3-1461871d02a045

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-003](../520_ケース/525_運用・復旧・監視.md#it-ops-003) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-051](../520_ケース/525_運用・復旧・監視.md#it-ops-051) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-96d8769309a8b2"></a>
## B3-96d8769309a8b2

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-002](../520_ケース/525_運用・復旧・監視.md#it-ops-002) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-003](../520_ケース/525_運用・復旧・監視.md#it-ops-003) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-022](../520_ケース/525_運用・復旧・監視.md#it-ops-022) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-023](../520_ケース/525_運用・復旧・監視.md#it-ops-023) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-024](../520_ケース/525_運用・復旧・監視.md#it-ops-024) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |

<a id="b3-cc00bad52b7cee"></a>
## B3-cc00bad52b7cee

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-002](../520_ケース/525_運用・復旧・監視.md#it-ops-002) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-003](../520_ケース/525_運用・復旧・監視.md#it-ops-003) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-022](../520_ケース/525_運用・復旧・監視.md#it-ops-022) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-023](../520_ケース/525_運用・復旧・監視.md#it-ops-023) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-024](../520_ケース/525_運用・復旧・監視.md#it-ops-024) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-026](../520_ケース/525_運用・復旧・監視.md#it-ops-026) | R-OPS | A01,A02 | O-DB,O-TIME |
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |

<a id="b3-81ee0264df1c3e"></a>
## B3-81ee0264df1c3e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-003](../520_ケース/525_運用・復旧・監視.md#it-ops-003) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |
| [IT-OPS-005](../520_ケース/525_運用・復旧・監視.md#it-ops-005) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-025](../520_ケース/525_運用・復旧・監視.md#it-ops-025) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-TIME |
| [IT-OPS-027](../520_ケース/525_運用・復旧・監視.md#it-ops-027) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-LOG |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-043](../520_ケース/525_運用・復旧・監視.md#it-ops-043) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30 | O-DB,O-FS,O-LOCK,O-LOG,O-OS |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-cea3240d3925a6"></a>
## B3-cea3240d3925a6

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-006](../520_ケース/525_運用・復旧・監視.md#it-ops-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-012](../520_ケース/525_運用・復旧・監視.md#it-ops-012) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-028](../520_ケース/525_運用・復旧・監視.md#it-ops-028) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-97391b282ac434"></a>
## B3-97391b282ac434

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-020](../520_ケース/525_運用・復旧・監視.md#it-ops-020) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-OS |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-d892170550f311"></a>
## B3-d892170550f311

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-2758a3e58f89ef"></a>
## B3-2758a3e58f89ef

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-022](../520_ケース/525_運用・復旧・監視.md#it-ops-022) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-7a5f22e604fadf"></a>
## B3-7a5f22e604fadf

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-031](../520_ケース/525_運用・復旧・監視.md#it-ops-031) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-260f781824e148"></a>
## B3-260f781824e148

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-023](../520_ケース/525_運用・復旧・監視.md#it-ops-023) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-708af92fd4bb80"></a>
## B3-708af92fd4bb80

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-PERF-035](../520_ケース/527_性能・資源・Logout混在.md#it-perf-035) | R-OPS | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b3-dcdfbde150b788"></a>
## B3-dcdfbde150b788

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-51a1ebdb55c49c"></a>
## B3-51a1ebdb55c49c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-7e61b34d094e2d"></a>
## B3-7e61b34d094e2d

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b3-bb3b57f5648722"></a>
## B3-bb3b57f5648722

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |

<a id="b3-a801f08c3a1cfc"></a>
## B3-a801f08c3a1cfc

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-OPS-010](../520_ケース/525_運用・復旧・監視.md#it-ops-010) | R-OPS | A01,A02,A03 | O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-020](../520_ケース/525_運用・復旧・監視.md#it-ops-020) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-OS |
| [IT-OPS-021](../520_ケース/525_運用・復旧・監視.md#it-ops-021) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |
| [IT-OPS-051](../520_ケース/525_運用・復旧・監視.md#it-ops-051) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-7761005a7c1734"></a>
## B3-7761005a7c1734

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-468b49562cdfe8"></a>
## B3-468b49562cdfe8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-035](../520_ケース/527_性能・資源・Logout混在.md#it-perf-035) | R-OPS | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-8fc94f87a89818"></a>
## B3-8fc94f87a89818

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-56e50837fbcea0"></a>
## B3-56e50837fbcea0

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-6cd6e51efeb503"></a>
## B3-6cd6e51efeb503

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-2135147b985081"></a>
## B3-2135147b985081

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-019](../520_ケース/522_トランザクション・データ.md#it-tx-019) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-b32079ba2752dd"></a>
## B3-b32079ba2752dd

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |

<a id="b3-2dd7b4f1524c86"></a>
## B3-2dd7b4f1524c86

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b3-d16fbc0fff805f"></a>
## B3-d16fbc0fff805f

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-6f70e571d4e7d2"></a>
## B3-6f70e571d4e7d2

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b3-cf50b6fb10bf7c"></a>
## B3-cf50b6fb10bf7c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b3-ecdab9e2d15eb9"></a>
## B3-ecdab9e2d15eb9

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |

<a id="b3-d708e386ee7d57"></a>
## B3-d708e386ee7d57

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-65a7ab6488f7df"></a>
## B3-65a7ab6488f7df

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-024](../520_ケース/525_運用・復旧・監視.md#it-ops-024) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |

<a id="b3-54897c5577633a"></a>
## B3-54897c5577633a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b3-60e77880f813f1"></a>
## B3-60e77880f813f1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-9e2ec0628b6263"></a>
## B3-9e2ec0628b6263

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-043](../520_ケース/525_運用・復旧・監視.md#it-ops-043) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30 | O-DB,O-FS,O-LOCK,O-LOG,O-OS |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-050](../520_ケース/525_運用・復旧・監視.md#it-ops-050) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-9d936fddd6ca60"></a>
## B3-9d936fddd6ca60

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-043](../520_ケース/525_運用・復旧・監視.md#it-ops-043) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30 | O-DB,O-FS,O-LOCK,O-LOG,O-OS |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-050](../520_ケース/525_運用・復旧・監視.md#it-ops-050) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |
| [IT-OPS-055](../520_ケース/525_運用・復旧・監視.md#it-ops-055) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-9dbf252a564f56"></a>
## B3-9dbf252a564f56

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-OPS-014](../520_ケース/525_運用・復旧・監視.md#it-ops-014) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-HTTP,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-015](../520_ケース/525_運用・復旧・監視.md#it-ops-015) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS |
| [IT-OPS-016](../520_ケース/525_運用・復旧・監視.md#it-ops-016) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-TIME |

<a id="b3-2091108ec78a0b"></a>
## B3-2091108ec78a0b

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-015](../520_ケース/525_運用・復旧・監視.md#it-ops-015) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b3-e0138770ff141d"></a>
## B3-e0138770ff141d

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-016](../520_ケース/525_運用・復旧・監視.md#it-ops-016) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-5d93c028edbcd2"></a>
## B3-5d93c028edbcd2

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-016](../520_ケース/525_運用・復旧・監視.md#it-ops-016) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-321b92ebbcdc06"></a>
## B3-321b92ebbcdc06

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-015](../520_ケース/525_運用・復旧・監視.md#it-ops-015) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-HTTP,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-054](../520_ケース/525_運用・復旧・監視.md#it-ops-054) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-FS,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |

<a id="b3-2449a18a89b4dd"></a>
## B3-2449a18a89b4dd

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-HTTP-014](../520_ケース/521_インターフェース.md#it-http-014) | R-SESSION | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-LOG-001](../520_ケース/525_運用・復旧・監視.md#it-log-001) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-LOG-002](../520_ケース/525_運用・復旧・監視.md#it-log-002) | R-WLOG | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-LOG-003](../520_ケース/525_運用・復旧・監視.md#it-log-003) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-LOG-020](../520_ケース/525_運用・復旧・監視.md#it-log-020) | R-WLOG | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-LOG-021](../520_ケース/525_運用・復旧・監視.md#it-log-021) | R-WLOG | A01,A02,A03,A04 | O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b3-36bfb9b87ff065"></a>
## B3-36bfb9b87ff065

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-004](../520_ケース/525_運用・復旧・監視.md#it-log-004) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-LOG-010](../520_ケース/525_運用・復旧・監視.md#it-log-010) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-010](../520_ケース/527_性能・資源・Logout混在.md#it-perf-010) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-020](../520_ケース/527_性能・資源・Logout混在.md#it-perf-020) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-54efae79d4f686"></a>
## B3-54efae79d4f686

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-005](../520_ケース/525_運用・復旧・監視.md#it-log-005) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-026](../520_ケース/525_運用・復旧・監視.md#it-ops-026) | R-OPS | A01,A02 | O-DB,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-034](../520_ケース/527_性能・資源・Logout混在.md#it-perf-034) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |

<a id="b3-5060a2cb74185f"></a>
## B3-5060a2cb74185f

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |

<a id="b3-862aafe2fe7eae"></a>
## B3-862aafe2fe7eae

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-040](../520_ケース/527_性能・資源・Logout混在.md#it-perf-040) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-001](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-SEC-002](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-002) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-008](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-008) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-030](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-030) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-be736a5ecdae98"></a>
## B3-be736a5ecdae98

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-LOG-006](../520_ケース/525_運用・復旧・監視.md#it-log-006) | R-SYNC | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-OPS-011](../520_ケース/525_運用・復旧・監視.md#it-ops-011) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-053](../520_ケース/525_運用・復旧・監視.md#it-ops-053) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-040](../520_ケース/527_性能・資源・Logout混在.md#it-perf-040) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-SEC-001](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-HTTP,O-LOG,O-TIME,O-WIRE |
| [IT-SEC-002](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-002) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-004](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-004) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-005](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-005) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-008](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-008) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11 | O-DB,O-HTTP,O-LOG,O-OS,O-WIRE |
| [IT-SEC-012](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-012) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-023](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-023) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-SEC-025](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-025) | R-SESSION | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-SEC-030](../520_ケース/523_認証・権限・セキュリティ.md#it-sec-030) | R-SESSION | A01,A02,A03 | O-DB,O-HTTP,O-LOG,O-WIRE |

<a id="b3-156f866df24bfc"></a>
## B3-156f866df24bfc

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-MQ-031](../520_ケース/526_MQ・非同期・容量.md#it-mq-031) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-ad3c495816435a"></a>
## B3-ad3c495816435a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-004](../520_ケース/526_MQ・非同期・容量.md#it-mq-004) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-030](../520_ケース/526_MQ・非同期・容量.md#it-mq-030) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-OS,O-TIME |
| [IT-MQ-031](../520_ケース/526_MQ・非同期・容量.md#it-mq-031) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-NET-001](../520_ケース/522_トランザクション・データ.md#it-net-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-MQ,O-TIME,O-WIRE |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-020](../520_ケース/525_運用・復旧・監視.md#it-ops-020) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-OS |
| [IT-OPS-028](../520_ケース/525_運用・復旧・監視.md#it-ops-028) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-e10a671fc571b1"></a>
## B3-e10a671fc571b1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-008](../520_ケース/526_MQ・非同期・容量.md#it-asy-008) | R-ASYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-OS,O-WIRE |
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-004](../520_ケース/526_MQ・非同期・容量.md#it-mq-004) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-030](../520_ケース/526_MQ・非同期・容量.md#it-mq-030) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-OS,O-TIME |
| [IT-MQ-031](../520_ケース/526_MQ・非同期・容量.md#it-mq-031) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-NET-001](../520_ケース/522_トランザクション・データ.md#it-net-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-MQ,O-TIME,O-WIRE |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-020](../520_ケース/525_運用・復旧・監視.md#it-ops-020) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-OS |
| [IT-OPS-028](../520_ケース/525_運用・復旧・監視.md#it-ops-028) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-ab2f029a12b660"></a>
## B3-ab2f029a12b660

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-ASY-006](../520_ケース/526_MQ・非同期・容量.md#it-asy-006) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-004](../520_ケース/526_MQ・非同期・容量.md#it-mq-004) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-030](../520_ケース/526_MQ・非同期・容量.md#it-mq-030) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-OS,O-TIME |
| [IT-MQ-031](../520_ケース/526_MQ・非同期・容量.md#it-mq-031) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-NET-001](../520_ケース/522_トランザクション・データ.md#it-net-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-MQ,O-TIME,O-WIRE |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-020](../520_ケース/525_運用・復旧・監視.md#it-ops-020) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-OS |
| [IT-OPS-028](../520_ケース/525_運用・復旧・監視.md#it-ops-028) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-544b1ceff0214d"></a>
## B3-544b1ceff0214d

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |

<a id="b3-4c00f43209b3fa"></a>
## B3-4c00f43209b3fa

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-TX-016](../520_ケース/522_トランザクション・データ.md#it-tx-016) | R-SYNC | A01,A02,A03,A04 | O-DB,O-LOG,O-TIME,O-WIRE |
| [IT-TX-018](../520_ケース/522_トランザクション・データ.md#it-tx-018) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-TIME,O-WIRE |
| [IT-WIRE-001](../520_ケース/521_インターフェース.md#it-wire-001) | R-SYNC | A01,A02,A03 | O-DB,O-MQ,O-OS,O-WIRE |

<a id="b3-f4dd95eb14580a"></a>
## B3-f4dd95eb14580a

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-6caa92851f75d8"></a>
## B3-6caa92851f75d8

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |

<a id="b3-e636694a34ed64"></a>
## B3-e636694a34ed64

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-043](../520_ケース/527_性能・資源・Logout混在.md#it-perf-043) | R-ASYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-e4538459e28a34"></a>
## B3-e4538459e28a34

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-030](../520_ケース/527_性能・資源・Logout混在.md#it-perf-030) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-031](../520_ケース/527_性能・資源・Logout混在.md#it-perf-031) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-032](../520_ケース/527_性能・資源・Logout混在.md#it-perf-032) | R-SYNC | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-033](../520_ケース/527_性能・資源・Logout混在.md#it-perf-033) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME |
| [IT-PERF-034](../520_ケース/527_性能・資源・Logout混在.md#it-perf-034) | R-SYNC | A01,A02 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-035](../520_ケース/527_性能・資源・Logout混在.md#it-perf-035) | R-OPS | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-0bba5af5db6b27"></a>
## B3-0bba5af5db6b27

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-042](../520_ケース/527_性能・資源・Logout混在.md#it-perf-042) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-27128310299b0c"></a>
## B3-27128310299b0c

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-032](../520_ケース/527_性能・資源・Logout混在.md#it-perf-032) | R-SYNC | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-8da6742f540eb4"></a>
## B3-8da6742f540eb4

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-IF-001](../520_ケース/521_インターフェース.md#it-if-001) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-IF-033](../520_ケース/521_インターフェース.md#it-if-033) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-010](../520_ケース/527_性能・資源・Logout混在.md#it-perf-010) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-020](../520_ケース/527_性能・資源・Logout混在.md#it-perf-020) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-TX-001](../520_ケース/522_トランザクション・データ.md#it-tx-001) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-TX-005](../520_ケース/522_トランザクション・データ.md#it-tx-005) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-LOCK,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-4cc22b54aac7f1"></a>
## B3-4cc22b54aac7f1

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-RETRY-100-集中-なし](../520_ケース/527_性能・資源・Logout混在.md#it-retry-100-集中-なし) | R-SESSION | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |

<a id="b3-ac1571403bb29b"></a>
## B3-ac1571403bb29b

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-003](../520_ケース/525_運用・復旧・監視.md#it-ops-003) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-004](../520_ケース/525_運用・復旧・監視.md#it-ops-004) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-TIME |
| [IT-OPS-005](../520_ケース/525_運用・復旧・監視.md#it-ops-005) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-025](../520_ケース/525_運用・復旧・監視.md#it-ops-025) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-TIME |
| [IT-OPS-027](../520_ケース/525_運用・復旧・監視.md#it-ops-027) | R-OPS | A01,A02,A03 | O-DB,O-LOCK,O-LOG |
| [IT-OPS-040](../520_ケース/525_運用・復旧・監視.md#it-ops-040) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-041](../520_ケース/525_運用・復旧・監視.md#it-ops-041) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-042](../520_ケース/525_運用・復旧・監視.md#it-ops-042) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-043](../520_ケース/525_運用・復旧・監視.md#it-ops-043) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30 | O-DB,O-FS,O-LOCK,O-LOG,O-OS |
| [IT-OPS-044](../520_ケース/525_運用・復旧・監視.md#it-ops-044) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-048](../520_ケース/525_運用・復旧・監視.md#it-ops-048) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-LOCK,O-LOG,O-OS,O-TIME |
| [IT-OPS-057](../520_ケース/525_運用・復旧・監視.md#it-ops-057) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-5d64e01c78ba13"></a>
## B3-5d64e01c78ba13

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-007](../520_ケース/525_運用・復旧・監視.md#it-ops-007) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-030](../520_ケース/525_運用・復旧・監視.md#it-ops-030) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-045](../520_ケース/525_運用・復旧・監視.md#it-ops-045) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15 | O-DB,O-FS,O-LOG,O-OS,O-TIME |
| [IT-OPS-046](../520_ケース/525_運用・復旧・監視.md#it-ops-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-052](../520_ケース/525_運用・復旧・監視.md#it-ops-052) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-057](../520_ケース/525_運用・復旧・監視.md#it-ops-057) | R-OPS | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-TIME |

<a id="b3-5acab7864f3e36"></a>
## B3-5acab7864f3e36

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-d9ed72e1f21f67"></a>
## B3-d9ed72e1f21f67

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-035](../520_ケース/527_性能・資源・Logout混在.md#it-perf-035) | R-OPS | A01,A02 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-b52883a6bffc6e"></a>
## B3-b52883a6bffc6e

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-009](../520_ケース/525_運用・復旧・監視.md#it-ops-009) | R-OPS | A01,A02,A03,A04,A05 | O-FS,O-LOG,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-850064e10d5040"></a>
## B3-850064e10d5040

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-OPS-047](../520_ケース/525_運用・復旧・監視.md#it-ops-047) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-e6b24885a86c18"></a>
## B3-e6b24885a86c18

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-CONFIG-001](../520_ケース/525_運用・復旧・監視.md#it-config-001) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78,A79,A80,A81,A82,A83,A84,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97,A98,A99,A100,A101,A102,A103,A104,A105,A106,A107,A108,A109,A110,A111,A112,A113,A114,A115,A116,A117,A118,A119,A120,A121,A122,A123,A124,A125,A126,A127,A128,A129,A130,A131,A132,A133,A134,A135,A136,A137,A138,A139,A140,A141,A142,A143,A144,A145,A146,A147,A148,A149,A150,A151,A152,A153,A154,A155,A156,A157,A158,A159,A160,A161,A162,A163,A164,A165,A166,A167,A168,A169,A170,A171,A172,A173,A174,A175,A176,A177,A178,A179,A180,A181,A182,A183,A184,A185,A186,A187,A188,A189,A190,A191,A192,A193,A194,A195,A196,A197,A198,A199,A200,A201,A202,A203,A204,A205,A206,A207,A208,A209,A210,A211,A212,A213,A214,A215,A216,A217,A218,A219,A220,A221,A222,A223,A224,A225,A226,A227,A228,A229,A230,A231,A232,A233,A234,A235,A236,A237,A238,A239,A240,A241,A242,A243,A244,A245,A246,A247,A248,A249,A250,A251,A252,A253,A254,A255,A256,A257,A258,A259,A260,A261,A262,A263,A264,A265 | O-CONFIG,O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS |
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-LOCK,O-METRIC,O-TIME,O-WIRE |
| [IT-DB-004](../520_ケース/522_トランザクション・データ.md#it-db-004) | R-OPS | A01,A02,A03,A04 | O-DB,O-LOG,O-OS |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-OPS-001](../520_ケース/525_運用・復旧・監視.md#it-ops-001) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-008](../520_ケース/525_運用・復旧・監視.md#it-ops-008) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16 | O-DB,O-FS,O-LOG,O-MQ,O-OS |
| [IT-PERF-001](../520_ケース/527_性能・資源・Logout混在.md#it-perf-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-002](../520_ケース/527_性能・資源・Logout混在.md#it-perf-002) | R-MEDIA | A01,A02,A03 | O-DB,O-FS,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-003](../520_ケース/527_性能・資源・Logout混在.md#it-perf-003) | R-OPS | A01,A02,A03,A04,A05 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-041](../520_ケース/527_性能・資源・Logout混在.md#it-perf-041) | R-SYNC | A01,A02,A03,A04 | O-DB,O-HTTP,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-c5c5530c4a6844"></a>
## B3-c5c5530c4a6844

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-004](../520_ケース/525_運用・復旧・監視.md#it-log-004) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-LOG-010](../520_ケース/525_運用・復旧・監視.md#it-log-010) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25,A26,A27,A28,A29,A30,A31,A32,A33,A34,A35,A36,A37,A38,A39,A40,A41,A42,A43,A44,A45,A46,A47,A48,A49,A50,A51,A52,A53,A54,A55,A56,A57,A58,A59,A60,A61,A62,A63,A64,A65,A66,A67,A68,A69,A70,A71,A72,A73,A74,A75,A76,A77,A78 | O-DB,O-FS,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-010](../520_ケース/526_MQ・非同期・容量.md#it-mq-010) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24 | O-DB,O-METRIC,O-MQ,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-PERF-010](../520_ケース/527_性能・資源・Logout混在.md#it-perf-010) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-020](../520_ケース/527_性能・資源・Logout混在.md#it-perf-020) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-FS,O-METRIC,O-MQ,O-TIME,O-WIRE |
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-9c3823d4a705f7"></a>
## B3-9c3823d4a705f7

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-DB-001](../520_ケース/522_トランザクション・データ.md#it-db-001) | R-SYNC | A01,A02,A03 | O-DB,O-LOCK,O-MQ,O-WIRE |
| [IT-DB-002](../520_ケース/522_トランザクション・データ.md#it-db-002) | R-SYNC | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-FILE-052](../520_ケース/524_ファイル・メディア・Range.md#it-file-052) | R-FILE | A01,A02,A03 | O-DB,O-FS,O-LOG,O-OS,O-WIRE |
| [IT-MQ-001](../520_ケース/526_MQ・非同期・容量.md#it-mq-001) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-MQ-004](../520_ケース/526_MQ・非同期・容量.md#it-mq-004) | R-ASYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-LOG,O-MQ,O-WIRE |
| [IT-MQ-005](../520_ケース/526_MQ・非同期・容量.md#it-mq-005) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-MQ-006](../520_ケース/526_MQ・非同期・容量.md#it-mq-006) | R-OPS | A01,A02,A03,A04 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-MQ-020](../520_ケース/526_MQ・非同期・容量.md#it-mq-020) | R-ASYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-METRIC,O-MQ,O-OS,O-TIME |
| [IT-MQ-030](../520_ケース/526_MQ・非同期・容量.md#it-mq-030) | R-ASYNC | A01,A02 | O-DB,O-MQ,O-OS,O-TIME |
| [IT-MQ-031](../520_ケース/526_MQ・非同期・容量.md#it-mq-031) | R-ASYNC | A01,A02 | O-DB,O-LOG,O-MQ,O-OS |
| [IT-NET-001](../520_ケース/522_トランザクション・データ.md#it-net-001) | R-SYNC | A01,A02,A03 | O-DB,O-HTTP,O-MQ,O-TIME,O-WIRE |
| [IT-OPS-013](../520_ケース/525_運用・復旧・監視.md#it-ops-013) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08 | O-DB,O-FS,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-OPS-020](../520_ケース/525_運用・復旧・監視.md#it-ops-020) | R-OPS | A01,A02 | O-DB,O-HTTP,O-LOG,O-OS |
| [IT-OPS-028](../520_ケース/525_運用・復旧・監視.md#it-ops-028) | R-OPS | A01,A02,A03 | O-DB,O-LOG,O-MQ,O-TIME |
| [IT-OPS-029](../520_ケース/525_運用・復旧・監視.md#it-ops-029) | R-OPS | A01,A02 | O-DB,O-FS,O-LOG,O-OS |
| [IT-OPS-049](../520_ケース/525_運用・復旧・監視.md#it-ops-049) | R-OPS | A01,A02,A03 | O-DB,O-FS,O-LOCK,O-LOG,O-OS,O-WIRE |
| [IT-OPS-056](../520_ケース/525_運用・復旧・監視.md#it-ops-056) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18 | O-DB,O-FS,O-HTTP,O-LOG,O-OS,O-TIME |
| [IT-PERF-044](../520_ケース/527_性能・資源・Logout混在.md#it-perf-044) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09 | O-DB,O-HTTP,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |
| [IT-RESTORE-001](../520_ケース/525_運用・復旧・監視.md#it-restore-001) | R-RESTORE | A01,A02,A03,A04,A05 | O-DB,O-FS,O-HTTP,O-LOG,O-MQ,O-OS,O-TIME |
| [IT-TX-030](../520_ケース/522_トランザクション・データ.md#it-tx-030) | R-SYNC | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12 | O-DB,O-HTTP,O-LOG,O-MQ,O-OS |
| [IT-PERF-046](../520_ケース/527_性能・資源・Logout混在.md#it-perf-046) | R-OPS | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-LOG,O-METRIC,O-MQ,O-OS,O-TIME,O-WIRE |

<a id="b3-qa051-20261102"></a>
## B3-QA051-20261102

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-LOG-022](../520_ケース/525_運用・復旧・監視.md#it-log-022) | R-WLOG | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10,A11,A12,A13,A14,A15,A16,A17,A18,A19,A20,A21,A22,A23,A24,A25 | O-DB,O-HTTP,O-LOG,O-MQ,O-TIME,O-WIRE |
| [IT-LOG-001](../520_ケース/525_運用・復旧・監視.md#it-log-001) | R-WLOG | A01,A02,A03,A04,A05,A06 | O-DB,O-HTTP,O-LOG,O-MQ,O-WIRE |
| [IT-LOG-020](../520_ケース/525_運用・復旧・監視.md#it-log-020) | R-WLOG | A01,A02 | O-DB,O-HTTP,O-LOG,O-WIRE |
| [IT-IF-017](../520_ケース/521_インターフェース.md#it-if-017) | R-SYNC | A01,A02,A03,A04,A05,A06 | O-DB,O-FS,O-HTTP,O-LOCK,O-LOG,O-MQ,O-TIME,O-WIRE |
