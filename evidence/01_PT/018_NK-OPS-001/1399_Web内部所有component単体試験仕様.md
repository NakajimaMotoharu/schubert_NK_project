# WEBOWN327001～007 / SSC327 / PG-D482

NK-WEB-002/NK-OPS-001、SYS002004/AUT002004/MQ003008/MON003/FIL001009、UI212223224226237243253、SS313314321342343352354、main297efc157/PR189。対象WebNativeRuntimeのconstructor/start/healthy/ready/close/native固定binding。WebNativeRuntimeOwnedComponentTestに七つの独立@Testを作成する。

|TestID|独立期待・観点|
|---|---|
|WEBOWN327001|自己所有PostgreSQL/Flyway・JMS・HTTPのstart成功、Ready一回・healthy/ready、二root FDがstart後保持、borrowed鍵生存、close後FDゼロ/ready・healthy false、重複start拒否・close副作用増分0|
|WEBOWN327002|最初のdirectory検証IO/RTE/Error/null/falseでReadyゼロ、例外同identity（null/falseは固定IOException）、保持rootを通常closeで解放し借用鍵保持|
|WEBOWN327003|management Ready release IO例外、未promote・全既知componentをclose後ゼロ、元失敗identity保持|
|WEBOWN327004|start中検証gateで自己close threadを起動しprivate monitor BLOCKEDを有限期限で確認。gate解除後startとcloseが完了しFDゼロ・ready false。sleep/外部monitor同期/未確認owner解放なし|
|WEBOWN327005|四portそれぞれnullは取得前拒否、null DirectoryCallsは固定境界拒否、field不変・鍵保持。未知key/null入力も別caseで検証|
|WEBOWN327006|ownerStopping trueではreadyへ昇格しない。start失敗後も既知ownerの通常close後条件、close済start拒否・公開状態の不整合無し|
|WEBOWN327007|default固定runtime/asset/transfer path・HTTP/management portの独立literal、未知key/null/不正証明、自己directory実metadataによるnativeVerify正常/不一致。Production callerが5引数/固定bindingであることはsource/JVMで別確認|

fixtureは専用TempDir配下で新規生成し既原本DB/Backup/鍵に接続しない。JMSは新自己所有brokerの127.0.0.1 ephemeral port、HTTPは同packageport functionで0だけを供給し既Production configの固定値を変更しない。directory interface spyは公開操作を実Linux呼出へ委譲しsuccessful FD取得/closeを独立setで数える。private field reflectionやwhole startup偽callback、既成功流用は禁止。検証identityは固定Production role値をassertしつつ自己fixtureのmetadataで検証し、OS本番role認証の合格とはしない。

正常/境界/null/例外/並行・一回所有と短期component後条件を網羅し、Errorや未確認終了を正常releaseへ変えない。未知拒否範囲PTALT001/002、実Root/DONE/native/auth/全coverage100/451/ITSTは未受入を維持する。期待値は固定literal・inode/FD・公開state/独立counterで作成しProduction呼出から生成しない。

群開始event1597の.5/1.5/4ppは維持、owner WBS-P018-06/F03参照（既群の追加費計上0）。source/command/実結果/各counter/全Main hash/BUG/traceは実行後別記。七caseの作成/compile/実行前にPASSやcoverageへ加算しない。
