# 081 NK-WEB-002 User業務接続単体テスト仕様書

PG-D366/SSC177、UI225236/SS313314331、FUN009/AUT002003/MQ021/TST・QA049。Program NK-WEB-002、SessionOperationTokenLifecycle.issue/issueForForms、UserAdminController new/create/detail/change、UserDetailViewModel、同core full MVC構成・local self reset終端。既存wire/各form/APIが正本検査を分担する。PG451 source916全3146の成功を本変更へ流用しない。

## 先行token/Version接続（PGと並行）

実Linux/JDK25.0.4/Maven3.9.12/隔離PostgreSQL18.6・既存Fixtureのfresh短TX/実SQL/固定Clock/独立UUID列。Input/expectedは下記literal list/SQL及びUI236のbyte offsetから独立に作る。Production encode/ViewModelの結果をexpectedへ使わない。

| Test ID | 対象・入力/操作 | 独立oracle |
|---|---|---|
| TOKV209A | pending0～10、必要form1～4、固定用途UST/URL/UPW/ULK | pending+必要数<=10だけ全成功・必要UUID数、超過は409/UUID0/現在保持list不変（通常touch metadataは別）。返却List不変/DB資源0 |
| TOKV209B | pending5＋consumed5、完成時刻1/2/2/3/4秒、4form | 最古4件だけ退役・同時刻は保存順、literal保持UUID[1..5,10,101..104]・4new pending issuedAt+5秒、既存tuple時刻不変 |
| TOKV209C | 2個目候補が旧UUID又は今回UUID衝突、commit/close fault | 全list変更rollback/元list不変、DB資源0。commit失敗は0/close不明は実row2を次再読して区別し成功返り0 |
| TOKV209D | 同sessionへ8thread/100組の2form競合 | 全future終了、5組だけ成功/95拒否、10一意token/10UUID・上限超過/部分保存0、実SQL lock/資源0 |
| TOKV209E | null group/要素、空/11用途、未知用途/null session/削除済 | 明示境界拒否又は409、UUID0/新row再生0/NPE正常化0、現在role/purpose契約保持 |
| PT-USER-DETAIL009 | fresh literal UDT320 version0/999999999 | 正規GET/detail200・表示versionそのまま。SS331 default0/N9を独立oracleとしBUG639の誤positive/旧DETAIL005 zero=503期待を是正。byte長/target/session count/日時の他検査を緩めない |

## 後続の同User接続（現時点未実装・未実行）

GET new/POSTcreate・詳細GET実表示form/4POSTの全正常/境界/異常/null/並行/再送を対応させる。閉operation欠落/複数/未知400かつMQ0、ADMIN USER/self/最後ADMIN/version0/max、fresh UDTのusernameだけでPASSWORD bind、同token/別payload409・消費初回時刻・保持退役、password消去/HTML再表示禁止・0105最新UDT/同token、新規User0→詳細→初回変更1/ULK既解除0200同versionを実API/SQL/HTTPで確認する。API0102は既存terminal、自己UPW0000/0200だけのlocal終端は0102捏造/追加LGO0・Cookie/security/context/current rowのみ消去。これらのTest ID・独立wire/DOM/SQL値は実装前に本仕様へ追加し、未実行を合格へ算入しない。

source・branch・command・開始終了/actualexit・環境・F/E/S・四coverage・static・BUG639/YKT452/新発見BUG・safe evidence/path/hashは082/manifestへ実測後記入。選択は変更/依存suite＋全6canary、既存TOKV207208/session/security/User/API回帰を含め、User共有session/security群の機能受入はsource固定fresh全6。native/fullReady/CHR/正式run24の認定は別、安易な除外/人工assertなし。
