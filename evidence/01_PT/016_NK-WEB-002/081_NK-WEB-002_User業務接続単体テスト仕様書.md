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

## 同User接続（限定試験済み・全体受入待ち）

以下のBIZ001～012を製造と並行して追加した。実行結果・対象sourceは082、追加後に未実行の観点はnot-runとして区別する。独立USRMUT24/UDT320はUI236 offset、HTTP/DOM/SQLは固定期待でありProductionからexpectedを算出しない。

| Test ID | 入力/観点 | 固定期待/根拠 |
|---|---|---|
| PT-USER-BIZ001 | ADMIN new GET/HEAD、UCR0000/0200新User | default USER/true/password空、保持1UCR UUID、372byte独立request・24byte返信version0、consume初回/固定302 detail・新User version0表示 |
| PT-USER-BIZ002 | full詳細0/max・self/他・LOCKED/ACTIVE/DISABLED、実表示1～4formと容量 | fresh UDT320、実表示用途だけ全確保/上限とretire順、STATUS/ROLE自己禁止・Lock解除lock中だけ、0版hidden/CSRF/固定action |
| PT-USER-BIZ003 | STATUS/ROLE/PASSWORD/UNLOCKの0000/0200 | 独立60/68/324/60 byte（UI236 §6の実表を実行前に照合）、target/version一致→consume→固定302、ULK0200同versionは許容、各POSTは既存各formをborrow |
| PT-USER-BIZ004 | unknown/missing/multiple operation/field、bad ID/version/token/confirm、USER/foreign actor | MQ更新0、operation400/USER403/null明示拒否、retired409/新UUID0、CSRFは実security chain拒否 |
| PT-USER-BIZ005 | genuine0105/9000/応答喪失・入力error | fresh UDT最新版409、保持同token・明示GETなし新発行0、password空/原文ログなし・同内容manual retry・API失敗を成功消費しない |
| PT-USER-BIZ006 | 全非成功code・wrong target/version/layout/context/unknown | UI232 mapper400401403404409429503、0102専用終端、未知503/consume0、mandatory/result束縛維持 |
| PT-USER-BIZ007 | API0102とself UPW成功を区別 | genuine0102は既存event/401又はGET302、self UPW0000/0200はCookie/current local/security/display消去/固定Login302・0102event/LGO0・他row保全 |
| PT-USER-BIZ008 | local completion/保存commit-close不明・missing session/foreign marker/handler response failure/fatal | 未確認を成功化0、同token次row再読、元Error維持/外側所有継続・秘密原文なし |
| PT-USER-BIZ009 | 実HTTP CSRF/role/login/各DOM/form/action/escaped入力 | GETHEAD/承認POST/405/403を実chainで照合、password/認証context/rawsession/descriptor非公開、全操作単値bound |
| PT-USER-BIZ010 | 実API create0→fresh detail→初回update1・unlock既解除同版・LOCKED解除0→1→保存再送1 | SQL/監査/owner/HMAC・response成功profileの独立後条件、UI新User一往復を閉じBUG639/YKT452再発防止。LOCKED前提はfixture SQLのみ、初回0000と同token再送0200のversion1/failed_count0/locked_untilNULL・解除監査1/Inbox再送1を固定SQLで確認（最後の追加methodはv5後追加、全回帰までnot-run） |
| PT-USER-BIZ011 | 100同時POST・保持/消費/旧input再操作・別input409 | 全future終了/独立message・API idempotency/同token同input保存結果・新UUID0、DB/JMS同時所有0/短TX資源0 |
| PT-USER-BIZ012 | 全新constructor/factory/null/immutable projection/closed form | 同core依存invariant/静的null・negative、password閉鎖と4フォームsealed境界、line/method/class/branch100/静的0 |

GET new/POSTcreate・詳細GET実表示form/4POSTの全正常/境界/異常/null/並行/再送を対応させる。閉operation欠落/複数/未知400かつMQ0、ADMIN USER/self/最後ADMIN/version0/max、fresh UDTのusernameだけでPASSWORD bind、同token/別payload409・消費初回時刻・保持退役、password消去/HTML再表示禁止・0105最新UDT/同token、新規User0→詳細→初回変更1/ULK既解除0200同versionを実API/SQL/HTTPで確認する。API0102は既存terminal、自己UPW0000/0200だけのlocal終端は0102捏造/追加LGO0・Cookie/security/context/current rowのみ消去。これらのTest ID・独立wire/DOM/SQL値は実装前に本仕様へ追加し、未実行を合格へ算入しない。

source・branch・command・開始終了/actualexit・環境・F/E/S・四coverage・static・BUG639/YKT452/新発見BUG・safe evidence/path/hashは082/manifestへ実測後記入。選択は変更/依存suite＋全6canary、既存TOKV207208/session/security/User/API回帰を含め、User共有session/security群の機能受入はsource固定fresh全6。native/fullReady/CHR/正式run24の認定は別、安易な除外/人工assertなし。

実行前の正本照合補足：ROLEはUI236 §6.2で68 byte（先行draftの64ではない）。self/ACTIVEはPASSWORDだけの1formであり、全画面一律2以上ではない。旧2引数read-only MVCのdetail002 POSTは新full業務依存が未注入なので503/API0へ更新する。full構成の同POSTは実際のclosed operation/CSRF/保持tokenを検証し、未指定操作を400とする。旧read-only資料/結果は保全し、本変更の合格へ流用しない。

PG-D367/BUG641643再発防止：PT-ADM-TIME001を010のProgram仕様へ先行追加、UserQueryRepositoryの5DB日時（.123456/.999999/.000001）のms-only wire投影とμs SQL原値保持をliteral vectorで確認する。PT-USER-BIZ011-TX=EncryptedWebSessionRepositoryTest#bizOwnership001FixtureDistinguishesSendingThreadFromOtherBorrowersは実2Connection/latchで他thread1中の送信thread0、送信threadborrow時1/global2、両close後0/観測Map空を独立に照合する。BIZ011の100実API同token成功はAPI開始時この同thread0を確認し、全終了後global0/version1/99REPLAY/同token初回完成印・一意Message100を確認する。他thread短TXを禁止する期待へ変更しない。BUG642のBIZ009開始は実/loginからCSRF/cookieを取得し、同core実HTTP/self UPW/Cookie消去まで到達する。failed-v2/未到達を再試験合格に算入しない。
