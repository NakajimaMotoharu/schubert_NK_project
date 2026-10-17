# 保持Expiry監査比較・SSC302単体仕様

## 2026-10-17 09:01JST 新4848 actual59PT/10suite合格・三method全条件0

4848元68863、sourceSnapshot **04bbdb73b532537e3546191d72dee913b17629a0**、23:57:51.646427～23:58:59.998382Z、actualMaven0/資格0・**59PT/10suite・全case完全一致/FES0**。元実PostgreSQL試験も完走、新14PT XML SHA **16ebd0868382d0a52be37405dfc2c7d519823e0f148e67cdacc72a450f2d42e6**、原SQL XML **d2cc639ff7623fe282fe862d52d42c9a06d38d0533edd422b394b620e5f05674**。Maven log **cb025f0f1fd18e097174aa390608fa1fcaa797b6888657b273d0ba530d0cc1ad**。環境三binary全hash/versionはbegin receipt、全10XML/command/時刻/exitはmanifestに保存。

実method各miss0：API admittedConfiguration=9line/1method/2branch、batch verifyPriorAudit=15line/1method/**22branch**、batch verifyPriorExpiry=10line/1method/**4branch**。実fixture全DB不変/rollback/normal停止を含む。BUG1389/YKT1155当host工具限定閉鎖、原1Errorを成功化しない。新helperは宣言data boundaryであり認可/本番DB成功を示さず、旧825e nativeへ追加しない。

全compiled Mainの前置測定は旧1646→候補1647、変更 **ApiProcessMain.class / CleanupExpiryExecution.classの2**、追加 **ApiProcessMain$ConfigurationLoad.classの宣言interface1**、その他1644 byte同一/削除0。宣言interfaceは実class byte inventoryに含め、実行命令なしの0/0を除外設定へ転用せず、構成/呼出し契約を新8PTで検証する。所定wholeで再度物理全SHA・Jar/22新caseを独立照合するまで全体へ繰上げない。

## 2026-10-17 08:59JST 4842はhost initdb不存在・新14PT自体0/combined未合格

4842元64850/source0e93e7b76184275b4fe010582d99d504bce7f637、23:54:33.636074～23:55:41.419246Z、actualMaven1/資格1・59PT/10suite・既DB試験に1Error（新14件はFES0）。log **d5fc0e39d5ce6c3af0c65bd45ed099ccdc163e44e694a32f0ad50448fdfec196**。旧selectorのhost環境path `toolchain/postgresql18/usr`にinitdbが存在せず、Productionや判定本体の失敗ではない。batch coverage未生成のまま非0判定、合格加算0。

BUG1389/YKT1155先行、現host既存実物 `work/characterization-tools/root/usr`へnew-only4848をbind。実initdb/postgres/pg_ctlは18.6（Ubuntu18.6-0ubuntu0.26.04.1）、initdb SHA b2b8d645e0947409f04744ac075d92511f9400c3b200a67f351bb4970129f9aa・pg_ctl SHA d515ae2903b94700993fed2979319ec9c5ad5f9083b10cae5e274a6071ca4104、Fixture既LDは同root lib/x86_64-linux-gnu＋lib/postgresql/18/libを使う。新install/業務DB/VM/DDL変更0。起動前3program存在/実version/実hashをbeginへ保存、missing root拒否・strict suite/全case gate独立2工具0/static0。次clean固定→4848の未実行分だけ一回。全回帰4844は準備中/未発行、先行資格guardは旧failed4842のままのため発行不可、actual新selected0を確認してから改版する。

Program NK-BAT-001/NK-OPS-001、CleanupExpiryExecution.verifyPriorAudit/verifyPriorExpiry。RD DAT-009/OPS-009、UI251、SS331/341/343 SSC117/125/200/302・451。設計main ef0c73b4b/PR148（design-only093234a97）済み。元11比較は同じ順序/固定IOExceptionのまま抽出し、Repository guard/strong snapshot validation/borrowedConnection/transaction/SQL/Unit/permit/期限を不変更。新data-only helperの成功はDB/原本/OS認可の証拠ではない。

## PT-OPS-EXPIRY-AUDIT-SSC302001..014

共通独立fixture=run38100000…/cutoff2026-09-30T00:00:00Z、prior42/attempt1/start00:00:01/end00:00:02、明示expiry2026-09-23T00:00:00Z、SUCCESS/before3/after1/target2/success2/failure0/bytes200/errorなし。期待値をProductionの算出で作らない。新RetainedExpiryAuditTestは次14JUnit。

| ID末尾 | 目的/入力・操作 | 独立期待値 |
|---|---|---|
| 001 | 正常fixture、0/Long.MAX_VALUEの差分 | 正常帰還・0-0=0及びMAX-0=MAX、算術overflowなし |
| 002 | status WARNING | 固定StorageIoException UNAVAILABLE |
| 003 | endedを明示+1秒 | 元prior終了時刻不一致を同固定拒否 |
| 004 | expiryを明示+1秒 | 7日前の固定cutoff不一致を拒否 |
| 005/006 | before/afterそれぞれnull | 0補完/NPE正常化せず固定拒否 |
| 007 | before0/after1 | before>=after違反を固定拒否 |
| 008 | before3/after0/success2 | 3-0≠2を固定拒否 |
| 009 | target3/success2 | 完了件数不一致を固定拒否 |
| 010 | failure1 | SUCCESS監査の失敗件数を固定拒否 |
| 011/012 | errorCode/errorSummary各UNTRUSTED | 診断混入を固定拒否・固定message/causeなし/suppressed0 |
| 013 | null reference/snapshot | 内部契約の即拒否、NPE catch正常化0 |
| 014 | nonSkipped/selected1/nullを外側へ渡す | JDBC呼出0で先行拒否、borrowed Connection操作0 |

この負Snapshotは内部predicateの境界用であり、DDL/DAOがその行を受け入れる証拠ではない。新反例を通すためDB constraintやDAOを緩和しない。本物PostgreSQL18/Flyway schema028の既CleanupExpiryExecutionTestも同runで実行し、正常SKIP/既成功監査・全fixture行不変、所定不正行拒否/rollbackを併用する。再送/並行owner/Unitは本pure比較の外側の既scope契約で別受入、免除/自動合格としない。

## 実行条件・証跡

新4842はAPI SSC301関連7suite＋WebStartupInputsTest＋既DB試験＋新14PTの**全6module/10suite**を物理path/@Testから着手前検査し、source/archive全SHAを固定、全case集合/actualMavenExit0/FES0を独立資格。実API helperとbatch verifyPriorAudit/verifyPriorExpiryの各LINE/METHOD/BRANCH miss0を追加gateにする。選択理由=新SS301/302とその設定/元SQL・関連entry、全体回帰とは分離。NoTests/POM true不変更・非対象0件成功化0。selector1工具0/host静的0、Api/batch整形規約適用、実PT未実行。

環境Linux/JDK25.0.4/Maven3.9.12/PostgreSQL18/JaCoCo0.8.15/NullAway0.14.1/ErrorProne2.50.0/GJF1.36.1。command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes3.4.0/runtime> python3 -B tools/quality/pg4842_expiry_audit_selected.py`。clean commit後一回、W/pg4842-expiry-audit-selected-v1へbegin/owner/manifest/元log・snapshot内XML/coverageを保存。実source/終了code/時刻/hash/coverageを結果後記、未実行を合格にしない。新BUG未発見、TDD未実装初回失敗は障害扱いしない。

現配備825e/PG4702/native10・全1646は原source測定、candidateのAPI/Expiry Main変更へ流用0。必要変更群をまとめたfresh全回帰/all-six format前置・新Source全physical Main/CRC/native/CHR/四100/F03/451/trace/引継ぎは別未完。正式1964/53/旧17歴史/工数null/QA051finalは維持。
