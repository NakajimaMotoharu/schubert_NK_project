# PG479 固定Backup入力権限結果（限定）

仕様382/SSC197/BUG771/YKT551/工具BUG772。2026-10-06、branchdev-foundation、source318c＋明示差分（固定commit後記）、host Linux/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15。

red-v1 actual1はprotocol no testsでbatch未到達、BUG772として別保全、期待再現へ算入0。red-v2 actual1はbatch BMODE197001のInspector期待33184/actual33152（0100640/0100600）を独立literal表で再現、他2新PT正常。固定name policy修正後green-v2 actual0、明示8suite/44PT、F/E/S0、静的5module BugInstance0。旧XMLが残るnonclean選択なので全directory計2495PT等を本runへ合算しない。新inputModeはJaCoCo instruction31/branch10/line4/method1全miss0、class/global/native100は未受入。

WorkPG379 logs SHA256：red-v1 d82f0256552dcb5a4fed1b813a32424568833d961c03a2beefa7d81527ae05b1、red-v2 99a8afaf847f504f093e636192f753dbabd4d6fd32a7f49511324e628b7c9708、green-v2 a4417ed3a1e96d268411ca7281bb3f3c70abba0146d7ecc9855ff35461008921。開始/完了/実exit/source/diffは各sidecar私有に保持。

VM before-terminal capture actual0、Root pg479-archive-diagnosis/before-terminal.private.json0600、SHA581556b27224030f03ea449c53c724c2820b5d57a9d56ddc8a369dac36933ee2。全oldDB同値・旧物理原本/Backup保全、2RUNNING、actual8config契約一致/旧suffix不一致Inspectorだけ。parent3418691/INV795eec6b633244148b40b26d0251a8ed依然activating/start、元15:58:42期限不変。Root state success補助値は親終了0の証拠ではない。raw全列/heap/request/credentialはGit外私有、safeは本hash/集計だけ。

SSC197 design-only ff95acc97→PR28通常merge→origin/main b8b1199ff369ece1385585f9069da1786cceede2確認、二fileだけ。修正sourceのfresh全6/native/真正Backup完了・marker退役・再送/resume・BUG771/YKT551完了は未受入。正式run24/1964PT53scope/48.3%据置。
