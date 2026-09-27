# 171 Artemis実Unit：限定実行結果

2026-09-28 JST、SSC103/SS321/341/342/343、NK-OPS-001/NK-MQ-001。Production `artemis.service` を実instanceへ束縛。171は構文/依存/配備の途中結果であり、broker実起動・clean journal・全8親受入ではない。

| Test ID | 独立期待 | 実測/判定 |
|---|---|---|
| ARTUNIT001～004 | SS342§4/7のCleanup必須依存、専用UID/実instance、private hashed LoadCredential＋Unit namespace内read-only bind、非秘密JVM/止め方・resource/hardening固定 | `PG321-artemis-unit-GREEN`：Storage8＋Bootstrap8＋Batch4＝20PT、F/E/S0、SpotBugs0、canary105全PASS。Production変更はUnit fileのみで、JaCoCo Java coverage100%を捏造しない。 |
| NATIVE033 | 隔離VMの本物のinstanceとOS accountへUnitを非起動install。Id/loaded/inactive/PID0、control-group/no/60s、権限・原本不変を確認 | `artemis.service` loaded/inactive/PID0、schubert-artemis、MemoryMax2GiB/FD65536、policy固定。`systemd-analyze verify`は実Cleanup `not-found`によりexit1、これは未解決の依存であり合格に算入しない。Credential sourceも未配置でbrokerを起動していない。 |

実行command・日時/環境/branch/基点50d1dcfa3＋dirty Unit/test hash・sanitized JUnit/JaCoCo/SpotBugs XML・VM状態と原本3SHAは `PG321-artemis-unit-GREEN` と `PG321-native033` manifest。Broker資格情報内容、raw journal/session/InvocationIDは保存しない。

未認定：Cleanupの真正Unit/処理、root hashed credential source・LoadCredential bindの実適用、broker起動/Address/Queue/security/readiness、journal clean stop、Expiry/API/Web、全8終端、業務外部起動/CHR。Mandatory `Requires`を外さず、`--ignore-dependencies`/fake Unitで実起動を作らない。
