# 171 Artemis実Unit：限定実行結果

2026-09-28 JST、SSC103/SS321/341/342/343、NK-OPS-001/NK-MQ-001。Production `artemis.service` を実instanceへ束縛。171は構文/依存/配備の途中結果であり、broker実起動・clean journal・全8親受入ではない。

| Test ID | 独立期待 | 実測/判定 |
|---|---|---|
| ARTUNIT001～004 | SS342§4/7のCleanup必須依存、専用UID/実instance、private hashed LoadCredential＋Unit namespace内read-only bind、非秘密JVM/止め方・resource/hardening固定 | `PG321-artemis-unit-GREEN`：Storage8＋Bootstrap8＋Batch4＝20PT、F/E/S0、SpotBugs0、canary105全PASS。Production変更はUnit fileのみで、JaCoCo Java coverage100%を捏造しない。 |
| NATIVE033 | 隔離VMの本物のinstanceとOS accountへUnitを非起動install。Id/loaded/inactive/PID0、control-group/no/60s、権限・原本不変を確認 | `artemis.service` loaded/inactive/PID0、schubert-artemis、MemoryMax2GiB/FD65536、policy固定。`systemd-analyze verify`は実Cleanup `not-found`によりexit1、これは未解決の依存であり合格に算入しない。Credential sourceも未配置でbrokerを起動していない。 |
| NATIVE034 | 実instanceのhash済み4entry `ENC(...)` だけをroot600固定sourceへ原本非破壊で配置。専用UIDの一時Unitに同LoadCredential/read-only bindを設定し、host inodeとprivate inodeの差・SHA一致を確認 | UID994、private bindでroot:root0440/inode `55:2`を専用UIDが読取り、host旧file inode `64769:503359`と異なる。SHA256 `e890987596e2fc5a204ff298aba80d3814f90e6cb4b3310b5bccbe5d4945f13d` がroot sourceと一致。3つのtest-only transientはexit0、実`artemis.service`はinactive/PID0のまま。Credential内容とraw InvocationIDは非格納。 |

実行command・日時/環境/branch/基点50d1dcfa3＋dirty Unit/test hash・sanitized JUnit/JaCoCo/SpotBugs XML・VM状態と原本3SHAは `PG321-artemis-unit-GREEN` と `PG321-native033` manifest。Broker資格情報内容、raw journal/session/InvocationIDは保存しない。

未認定：Cleanupの真正Unit/処理、本物の`artemis.service`におけるLoadCredential bind適用、broker起動/Address/Queue/security/readiness、journal clean stop、Expiry/API/Web、全8終端、業務外部起動/CHR。Test-only transientでの実systemd bind成功を、本物のBroker Unit起動へ読み替えない。Mandatory `Requires`を外さず、`--ignore-dependencies`/fake Unitで実起動を作らない。
