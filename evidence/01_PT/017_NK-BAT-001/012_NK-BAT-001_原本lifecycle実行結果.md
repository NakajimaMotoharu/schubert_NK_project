# NK-BAT-001 原本lifecycleの実行結果

PG-D-158/011/PT-BAT-058～081。関連module探索は成功、正式全reactor待ち。正式20260913-01へ含めない。OS lock/親/DB legacy・400日GCは未完了。

| Run（2026-09-13 JST） | 結果 | sanitized原log SHA-256 |
|---|---|---|
| explore1 00:58:46 | 209 PT成功、5 branch未網羅でexit1。BUG162先行起票後に追加 | a4883dce8569bb10071f02a80b3c1da0a8147d9cb54c65404139207fe5a3db6b |
| explore2 01:02:41 | 209 PT、line/method/class/branch100%、静的解析合格、exit0 | 6b14cf599f3eccc05fcdc0de1c0c0889d6d03d90ff402d3ae88258aba2a971ff |
| explore3 01:06:42 | 209 PT、同4指標100%/静的解析、追加graph・Session並行負例・7実file trace成功、exit0 | 3f54764fab8286e3d84bc69e5e9945b90173f37b6255398c073482612dee30f8 |

対象はdev-foundation/PG158未commit変更＋dd8a54c8までの先行台帳。Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12、関連commandはJAVA_HOME=work/toolchain/jdk-25.0.4（absolute設定） ./mvnw -o -Dmaven.repo.local=work/toolchain/m2/repository（absolute設定） --no-transfer-progress -pl src/schubert-nk-batch -am verify。全正式command/時刻/source/hashは正式実行後manifestへ記録する。

BUG159の修正前2再現・BUG160/161 compile・BUG162 branch不足とYKT124～126はevidence/logsの各auditへ追跡。探索だけでは完了へ変更しない。実root・reboot・OS lockの実親は未試験。
