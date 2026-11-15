# PgJDBC COPY API・独立期待値・24件対応仕様

Program NK-MIG-001、PostgresMigrationCopyPort.copy/snapshot/cancelOwned/requirePg/requireManager/requireCopy/toString。RD MIG003/005/006・MIG-DAT005・TST、UI223/242/254、SS311/331/343・SSC417。仕様148と併用する。

全件の事前条件は将来のSDK実行許可、Java25、既定42.7.13 ABIの正式確認、秘密を含まない合成fixture、借用write transaction。現在はSDK jar読取・compile・実行を許可しないため実行commandなし、全24件NOT_RUN_HOLD。型確認・動的結果・coverage・NPE排除の受入は未完。@Disabledや除外で合格にしない。

|Test ID / method|入力・操作|独立期待値・観点|結果|
|---|---|---|---|
|PT-MIG-PGCOPY001 / pgcopy001|six fixed tables|six independent SQL commands and six hand-authored wire rows; actual count1/end1/inactive/no cancel|NOT_RUN_HOLD|
|PT-MIG-PGCOPY002 / pgcopy002|empty dataset|writes0/end1/count0/inactive|NOT_RUN_HOLD|
|PT-MIG-PGCOPY003 / pgcopy003|null target/table/rows|fixed IAE; SDK calls0|NOT_RUN_HOLD|
|PT-MIG-PGCOPY004 / pgcopy004|unknown/case/namespace/whitespace table|fixed IAE before SDK; no dynamic identifier|NOT_RUN_HOLD|
|PT-MIG-PGCOPY005 / pgcopy005|six widths+-1/empty/null row/capture changes|fixed IAE based on owned snapshot, SDK calls0|NOT_RUN_HOLD|
|PT-MIG-PGCOPY006 / pgcopy006|autoCommit true|fixed SQL exception before unwrap|NOT_RUN_HOLD|
|PT-MIG-PGCOPY007 / pgcopy007|readOnly true|fixed SQL exception before unwrap|NOT_RUN_HOLD|
|PT-MIG-PGCOPY008 / pgcopy008|attribute SQL/runtime/Error|original primary identity; unwrap/start/cancel0|NOT_RUN_HOLD|
|PT-MIG-PGCOPY009 / pgcopy009|unwrap null/SQL/runtime/Error|null fixed SQL; thrown identity preserved; start0|NOT_RUN_HOLD|
|PT-MIG-PGCOPY010 / pgcopy010|manager null/SQL/runtime/Error|null fixed SQL; no start/cancel|NOT_RUN_HOLD|
|PT-MIG-PGCOPY011 / pgcopy011|copy start null/SQL/runtime/Error|null fixed SQL; unowned handle cancel0|NOT_RUN_HOLD|
|PT-MIG-PGCOPY012 / pgcopy012|initial inactive|fixed SQL; writes/end/cancel0|NOT_RUN_HOLD|
|PT-MIG-PGCOPY013 / pgcopy013|every write position x three primary types|exact primary; subsequent writes/end0; active handle cancel once|NOT_RUN_HOLD|
|PT-MIG-PGCOPY014 / pgcopy014|invalid surrogate/NUL|IAE; active handle cancel once; no accepted row count|NOT_RUN_HOLD|
|PT-MIG-PGCOPY015 / pgcopy015|end SQL/runtime/Error|original primary; failure-only cancel when active|NOT_RUN_HOLD|
|PT-MIG-PGCOPY016 / pgcopy016|end count -1/0/2/MAX for one row|fixed SQL; no success|NOT_RUN_HOLD|
|PT-MIG-PGCOPY017 / pgcopy017|active after end|fixed SQL; cancel once and check inactive|NOT_RUN_HOLD|
|PT-MIG-PGCOPY018 / pgcopy018|primary three x cleanup three|first primary same identity; one ordered suppressed cleanup|NOT_RUN_HOLD|
|PT-MIG-PGCOPY019 / pgcopy019|cleanup same primary identity|no self-suppression; rethrow original|NOT_RUN_HOLD|
|PT-MIG-PGCOPY020 / pgcopy020|active query faults/cancel remains active|original primary with cleanup fault; no cleanup success inferred|NOT_RUN_HOLD|
|PT-MIG-PGCOPY021 / pgcopy021|callback input mutation/null field|owned snapshot unchanged; SQL NULL marker retained in literal wire|NOT_RUN_HOLD|
|PT-MIG-PGCOPY022 / pgcopy022|borrowed connection/repeated normal call|commit/rollback/close/set attributes0; independent second handle|NOT_RUN_HOLD|
|PT-MIG-PGCOPY023 / pgcopy023|redaction/public vectors|fixed redacted toString; explicit six SQL/column widths; no data in logs|NOT_RUN_HOLD|
|PT-MIG-PGCOPY024 / pgcopy024|8 workers/64 tasks|each literal wire/count; future5 seconds; finally shutdownNow/await10; NOT_RUN_HOLD|NOT_RUN_HOLD|

期待値はSSの明示六列リストと手書きSQL、合成rowから独立Pythonで作ったUTF8 wire hex、明示call履歴を使用し、production methodからexpectedを生成しない。証跡PG33710のcorrected-independent-six-copy-command-vectors.jsonとindependent-future-pt-row-wire-vectors.jsonへ対応する。SQL delimiterのPG復号後は09、NULL markerは5c4e。原・現SQLは全byte同一で、BUG3001は誤検知取り下げ。意図的に二重化した別合成negativeだけ5c74/5c5c4eとして拒否した。これはDB実行や実PTではない。

公式API source照合は[PGConnection REL42.7.13](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/PGConnection.java)、[CopyManager](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/copy/CopyManager.java)、[CopyIn](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/copy/CopyIn.java)、[CopyOperation](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/copy/CopyOperation.java)、[PostgreSQL17 COPY](https://www.postgresql.org/docs/17/sql-copy.html)。ソース上の契約確認のみでSDK ABI実測ではない。コピー済vendor sourceは格納しない。

接続認証・same-peer・排他・TX期限・rollback・資源後条件・未知結果の隔離はcaller側残条件。COPY cancel呼出しのソースがあっても実DB回収成功は未確認であり、再送を発行しない。性能・large dataset・実同時入力変更・DB永続化・migration/cutback・IT/STも未受入。
