# 質問検索・明細参照HTTP単体テスト仕様書

2026-10-03、PG-D350/NK-WEB-002・NK-QRY-001、RD FUN012～013/QST005～010/AUT、UI224/236、SS313/314/323/332。予定対象QuestionSearchForm/QuestionListViewModel/QuestionDetailViewModel/QuestionController/QuestionMvcConfiguration、questions/list・detail。PG438全6Source固定が終了するまで実装しない。

| Test ID | 事前条件・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-QRY-HTTP001 | USER/ADMIN、空/全6条件/NFC keyword/日付/page | UI236 §11 literal QSSREQ data384、Keyword0/256・Username256/64・state320/12・from332/17・to349/17・page366/6・size372/3・Reserved375/9、header256。全byteを手作成して比較、USER username送信は空でも400/API0 |
| PT-QRY-HTTP002 | UTF8 256/257・64/65、3state/未知、invalid Unicode/control、重複/未知/null/空要素 | fail-fast null契約、closed入力400、NFC/ASCII trim後上限、invalid時toRequest拒否、safe Map immutable・redacted。切捨てなし |
| PT-QRY-HTTP003 | 日付0001/9999/閏日/From≦To/366境界、page1/999999/0/負/overflow/非ASCII/plus | 同Notification formのJST日初/23:59:59.999、日付逆転/範囲外拒否、0以下→1、正数上限、独立fixed Instant/byte literal |
| PT-QRY-HTTP004 | 0/1/50row、50/51件・effective page、両role・全state | UI236 PAGED48・672row field byte、datetime/ID降順・一意/summary100・owner、ADMINのみowner表示/検索。独立JST秒/状態label/escape/pagination query/空結果、Map/List変更拒否 |
| PT-QRY-HTTP005 | count/page/order/duplicate ID/owner/summary/semantic破損 | API正常codeでも矛盾projectionは503、型不整合/欠落拒否。既存codec/API queryから独立literal不正vector、正controlも実施 |
| PT-QRY-HTTP006 | target1/N12最大/0/超過/null、ANSWERED空/本文・UNANSWERED・ERROR | QSDREQ12固定ID、QSDRSP8352はID0/12・receipt12/26・owner38/64・state102/12・question114/4096・answer4210/4096・submitted8306/17・answered8323/17・Reserved8340/12。全byte/header期待はliteral、USER owner/target mismatch拒否、空回答captionと未回答区別 |
| PT-QRY-HTTP007 | 全error code/0102、JMS timeout/correlation/context/layout/reserved/unknown | 0104/他owner/削除済404、0102 terminal Cookie/session、HTTP mapper固定分類・503、unknown identity保持、wire zero/pending0、未実行成功化なし |
| PT-QRY-HTTP008 | MVC GET/HEAD/POST、両role・HTML特殊本文/条件/空回答 | explicit template/title/escaped DOM/ADMIN限定列・field/HEAD body0・POST未接続405、削除button/POST機能完了は本参照scope外 |
| PT-QRY-HTTP009 | 実Jetty/encrypted session・匿名/両role/0102再GET | current actor認証、匿名302/no-store、GET/HEAD毎fresh wire、0102 DB/Cookie失効と後続API0、ordinary native fullReadyとは別 |
| PT-QRY-HTTP010 | 8thread100別target/context/UUID/条件 | 独立request/response対応・100別MessageID/混線0/zeroing/pending0、shared表示可変なし |
| PT-QRY-HTTP011 | factory境界/immutable snapshot・正常3stateとtimestamp/answer異常 | whole lifecycle class/method/line/branch100、null/空/欠落/未知negative、API実DB検索/delete除外/ownerは既存QuestionQueryRepositoryTestを関連実行 |
| PT-QRY-HTTP012 | keyword特殊query/ADMIN username・前/次/空・page clamp | UTF8 query encoding、USER hrefにowner無し、ADMINのみ検索条件保持、URLからcontext/token/body復元なし、独立文字列比較 |

期待値はUI offset/length・独立SQL後条件・HTTP/DOM literalから作成しProduction methodで生成しない。更新/削除token QA049の承認前変更なし、全Web業務assembly/native/Caddy/CHR・全53scope正式品質は未受入。Java4counter100/strict compile/null/static0、関連選択→共通MVC/template変更群固定全6を実行する。日時/OS/JDK/command/Source/exit/FES/実coverage/BUG/YKT/manifest/hashは064へ実測保存し、failed/flaky/skipped/not-runは合格へ算入しない。
