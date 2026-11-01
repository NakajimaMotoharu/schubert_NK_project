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
| [IT-DB-003](../520_ケース/522_トランザクション・データ.md#it-db-003) | R-SYNC | A01,A02 | O-DB,O-LOCK,O-METRIC,O-TIME |

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
| [IT-PERF-010](../520_ケース/527_性能・資源・Logout混在.md#it-perf-010) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-METRIC,O-WIRE |

<a id="b2-itc-perf-020"></a>
## B2-ITC-PERF-020

| Test ID | 経路 | Assertion | 証跡 |
|---|---|---|---|
| [IT-PERF-020](../520_ケース/527_性能・資源・Logout混在.md#it-perf-020) | R-FILE | A01,A02,A03,A04,A05,A06,A07,A08,A09,A10 | O-DB,O-FS,O-METRIC,O-WIRE |

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
