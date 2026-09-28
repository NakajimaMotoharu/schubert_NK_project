# 235 NK-OPS-001 Backup起動marker所有PT仕様（PG357）

Program ID NK-OPS-001。class/method `BackupUnitStartClient.create/beginNative/start/Attempt.retireAfter/awaitClient`。関連RD OPS-009/BAK-001、UI251、SS341§5-6・343§6.15、SSC-105/106、BUG-315/YKT-248。実Unitを起動しないSynthetic Process/固定event recorderで親所有境界のみ調べる。Production markerの別inodeへの差替・自動修復・UNKNOWN正常化は許さない。

| Test ID | 事前条件、入力・操作 | 独立期待値 |
|---|---|---|
| PT-OPS-BSTART010 | marker publication後、固定systemctl argvを模したclient exit0。親証明callback失敗→成功→再実行。別に送達不明とclient非zero | SS341/343の順序に従い、exit0だけではretire0。証明失敗後retire0、成功後retire1、二重retire拒否。UNKNOWN/非zeroは証明callback実行前に拒否 |
| PT-OPS-BSTART011 | publication中にthread interrupt。start port呼出回数・retire回数を独立count | markerの存在を維持、start0、UNKNOWN、retire0。中断flag維持 |
| PT-OPS-BSTART012 | null証明、証明callbackの再入、保持root再確認、marker退役IO不明を合成 | null拒否、再入拒否・marker不変。正常証明はroot前後確認後一度のみretire。IO不明後のretryは拒否して同inode二度目unlinkを行わない |
| PT-OPS-BSTART001～009 | 既存固定argv、policy/root、未知送達、timeout/close、公開順等を再実行 | 承認済み固定仕様を不変更 |

期待event順はSS341/343の固定順から手で作り、Productionの同methodをexpected生成に使わない。Null/未知/例外はBSTART001～012で確認。並行/再送は同一start markerのnew-only file PT231と、M/A排他・実Unit未知配送の後続PTへ追跡。`RetirementGate` callbackの真正M/A・原本・fresh receipt0・明示stop/全process終端は本仕様のSynthetic eventで証明されず、後続のProduction親結線と隔離VM実測までSSC-106/BUG-315/YKT-248を閉じない。

実行環境Linux/JDK25.0.4/Maven3.9.12、branch `dev-foundation`。限定commandは`./mvnw -o -f src/schubert-nk-batch/pom.xml -Dtest=BackupUnitStartClientTest test spotbugs:check jacoco:report`。security境界変更のためsource固定後、Production6 clean `test spotbugs:check jacoco:report`を実行。対象commit、件数、終了code、全4coverage/未網羅、関連BUG/SSC、証跡path/hashは236へ記録する。限定coverageは既存execと混在し得るため正式100%とみなさない。
