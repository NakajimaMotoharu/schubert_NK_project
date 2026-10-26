# ResultCode15期待独立化・静的分類結果

G03.01、群2384・開始1/4/8pp/上限10、BUG1826/YKT1577・追加BUG1827/YKT1578。source b8234ad5a1403e944acaf8e13f1e5f07a22309bd、Main21d不変。UserMutationReplay4/UserQueryReplay4/LogReplay1/QuestionQueryReplay3/LoginReplay2/QuestionMutationReplayの共通wire一、計15呼出し/六既存Test sourceを、Test-local `oracleResultCode`へ変更した。新Java source/依存/moduleなし。原担当/費用/既Test IDは現registryのまま、元byte配置・全assertionを保持する。

## 独立期待・判断

UI232§7のorigin/main正本と作業treeのbyte一致を確認して固定表を作成した。Test helperはenum identityのexhaustive switchのみで、Production wireValue/fromWire/成功classifier/encoderを呼ばない。六Test各local helperとし、元TestのDB/key/graph等のfixtureを別ルートからロードしない。nullは正常値へ補完しない。Test-local独立表の重複自体を製品module共通化やProduction定数依存へ置換しない。

SUCCESS=0000、VALIDATION_ERROR=0100、AUTHENTICATION_FAILED=0101、SESSION_INVALID=0102、FORBIDDEN=0103、NOT_FOUND=0104、CONFLICT=0105、LOCKED=0106、NOT_CANCELLABLE=0107、IDEMPOTENT_SUCCESS=0200、TEMPORARY_FAILURE=9000、RESOURCE_LIMIT=9001。

## 検証仕様と実結果

|記録|対象・期待・実結果|manifest SHA-256|
|---|---|---|
|PG10406-result-code-literal-plan-v1|UI232正本hash/元六source SHA/15限定変換・六local helperを固定。actual0|f247320941366dd0700ab3cbf8eb6601e00b6732cb2234c72b8526bc9ce4991f|
|PG10408-result-code-literal-static-v1|declared worktreeの所定static。own62760 actual1、raw26/CS0/processing0。九duplicateを先行起票、他17の個別文脈へ|6d2be81271bde4578c98e3f59be2a3c3ddc47881095a1d9a7c77889972c5d06a|
|PG10410-result-code-literal-plan-v1|Log五/Login四の九同値String定数。source=null/baseSource=b98の未commit候補SHAを固定、actual0。元literalをProduction定数から取得しない|55d6a1a5f6bc7c127c5838c4b130b4e6bcc5ec94aa9dd99833ff83ef07439301|
|PG10412-result-code-final-static-v1|own77520 actual1、raw17/CS0/processing0、元九duplicate解消。raw26/17の1を保持|73c9f0237b0e32e2c8a006c700b4d95af35c4892519003ea77b192a22bd841c0|
|PG10414-result-code-six-compile-v1|own22659 actual0、固定sourceb823の正常六module/NullAway/PT0。所定static先行後の一回compile|83e2904ee2a0ee50ef0efab4916f73f53aaa0660cd8b3a2555b2eec21477da35|
|PG10416-result-code-literal-post-v1|actual0、六×12=72固定mapping entry、誤code72/Production依存再導入六/定数別値九の87metadata拒否。元全文token/全assertion/byte配置保持、全Main1843・他Test1949同byte、当六source由来13class差（Test1956→1962）|4a50827d1a97a6f6fda1df03d484edd7eeee0e3f135bd9b76fcb8ff7861e67ae|

72/87は静的source metadataの項目/変異数であって製品PT件数ではない。実assertion呼出し総数は未計測null、元全文token保持の根拠とは区別する。元業務Test/新local helperを動的にロード・実行していない。製品PT0/NOT_EXECUTED_HOLD、coverage未測定。

raw17は各実line/source SHA/所有へ個別結合。Test worker八、null負例三、固定JDBC Proxy loader三、try-withで所有するoriginal/retryのborrowed alias一、意図的に明示closeしたcodecを使う閉鎖後負例一、入力identityによる固定context選択一。抑制追加0。明示closeのsource確認を実key lifetime/消去/DB後条件やHOLD解除へ変換しない。全F03/G03/451未受入。

## 実行・保存・次作業

commandは各同番号tools/quality Python工具、PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime。Linux7.0.0-38 amd64/JDK25.0.4/Maven3.9.12/PMD7.28.0/CS14.3.0/GJF1.36.1、branch dev-foundation。工具command/input/expected/actual/開始終了/対象hash・UI根拠と全counter未測定は各manifestに結合。実環境/原本/Backup/鍵/native/held witness二file操作0。

旧b98のrole13source/全Main byteは不変だが、10402の四PTはsourceb98のまま歴史参照し、sourceb823全体のPASSへ移さない。正式1964PT/53scope、個別17/190、工数null、QA051 final/全安全HOLD不変更。次は現10384/source3d9fのregistryへrole13＋code六の計19最終SHAを原担当/費用/旧runtime保持でbatch追跡する。新sourceへの旧成功の合算・新WBS受入加算0。
