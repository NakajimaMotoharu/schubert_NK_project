# PG3172 自己ADMIN条件・QSB/MQ役割・全case横断再点検

BUG1271/YKT1037、BUG1272/YKT1038。Root323bc9/60559の真正DONE/全24/全sealは実完了、同普通四owner/SOCKSを保持する。Production/Main/UI/SS/Current baselineを変更しない。

## 失敗と保全

3164/exec74762、32a4fb557固定、02:41:57.248797～42:09.662147Z、actual1/sourceQualifiedtrue。PT-NBR001～003は実PASS（JCA credential、三Login/Menu、最大二/最古REPLACED/失効GET拒否）、全体十二は未合格。ADMIN詳細HTTP200/新UDT一/新LGN三・API Login監査三/REPLACED二をfresh SQL集計し、質問未発行。自己/nonlockedなのに全四formを期待したoracleが原因。SS313 §186～187/UI225 §5によりPASSWORDだけが正しい。旧失敗と私有全24/metadataを保存し、未実行ケースを成功へ加算しない。

## 期待値の全ケース再照合

| Case | 正本・条件 | 固定期待値/技術write |
|---|---|---|
| 001 | SS314、専用保全credential | RO/JCA・ADMIN/ACTIVE/非lock、password resetなし |
| 002 | Current CHR-U01/UI264/SS313、ADMIN | 既五label/相対順＋承認追加、九card/三Login |
| 003 | DIF016/SS314 | 最大二、最初の新sessionがREPLACED、失効GET拒否 |
| 004 | UI225/SS313 §186～187、本人/nonlocked | UDT一/HTTP200、PASSWORDだけ。STATUS/ROLE/UNLOCK非表示、更新POSTなし |
| 005 | SS314 CSRF、tokenなしPOST | 403・業務API発行0 |
| 006 | UI224改行禁止、同pending token | 400・QSB Inbox/質問0、token保持 |
| 007 | UI224236/SS312324331、固定HTML本文 | 302/当owner質問一/job一/通知一・locator三列・HTML escape、QSB M0と内部W別 |
| 008 | QA049/SS324保存結果、同token/同本文 | 同receipt/302・QSB Inbox/質問不増、元M0保持 |
| 009 | QA048/SS313324、受付GET refresh | fresh QSD二件目/NONE snapshot、更新再発行0 |
| 010 | UI224236、本人通知のみ | NTS一/NONE snapshot・当receipt一行、非同期stateを完了固定にしない |
| 011 | SS314324、現二session | 正規Logout二/LOGOUT。第一のREPLACEDは不変 |
| 012 | SS331/351、全24後条件 | 保護account/既行/master/保守表不変・限定新行・Web log/outbox一対一、別複合seal |

UI232の256headerとUI236 IF-I01の64dataを独立golden sliceへ結ぶ。M0=QSB元Inbox ID=async_jobs.message_id/correlation、W=新QWK ID!=M0、Outbox correlation=M0。wireは320byte、SCHBNK01/001/QWKREQ01/001/E/I、W/M0、JST17桁、context64space/0256/data64/record0/total320/result予約space、data受付26/Question12/Job12/予約14を検査する。Production codecでexpectedを作らない。純六試験0、異UUID golden/誤M0同一化/foreign correlation/byte offset十一箇所改変を拒否。実質問はまだ未発行であり、実結果へ合わせた期待値変更ではない。

## 二失敗prefixと再試験

3162実0で認証した「一Login」から、今回3164の「三Login＋UDT一」を3170の別独立oracle/3172 RO採取で認証する。既行・保護account・当owner以外不変、new auth三（REPLACED一/有効二）/Web三、LGN三＋UDT一、query NONE、auth/Inbox/API audit identity、Web log/SENT相関を検査し、質問/他業務write0を必須にする。純二試験0/禁止差六。旧failed1は保持し、部分PASS/差分資格を全体PASSへ読み替えない。

新ready3138v5はnew-only九phase（compile/Java golden/six Python suites/credential RO）、new-only3184で実Browser十二/3136全24へ進む。既SOCKS/ordinaryのみ再利用し、Root/配備/署名/Unit reload/初期ADMIN/既Browserの再発行0。3146はRoot→認証済み一Login→認証済み三Login/UDT→新before→新after→現在を順序・owner・全値・観測窓で連結し、各oracleを別namespaceで実行する。正当化されていない現DBをbaselineへ昇格しない。後続3148/3152/3154/3156/nativeまでは未実行。
