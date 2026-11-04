# 共有画面百契約の再利用判定

同じS10内のS-POST。586の「未捕捉86leaf中、7画面のbasename候補0」を「試験なし」と扱わず、6共有Test class/100原methodを本文まで照合した。591/595/599/602/605/608が独立期待値、592/596/600/603/606/609が504のexact `class#method/path/hash/span`対応である。共有ファイルを複数画面へ関連付けても試験数・費用を重複加算しない。

| 共有Test | 原method数 | 本文照合 | 既存内容として再利用できる根拠 | 追加資格の前に残る依存 |
|---|---:|---|---|---|
| UserAdminControllerTest | 19 | 591 | UI236 literal wire、明示DOM/HTTP/Unicode順/不正projection | 2arg legacy構成と普通更新構成を分離、現source実行参照の照合 |
| NotificationControllerTest | 18 | 595 | 通知検索/明細byte、状態/日時/削除/空回答/並行 | 更新token未接続構成と取消を分離、実owner/業務DB/実JMSは別 |
| ErrorMvcTest | 10 | 599 | UI222/SS313固定status/message、元例外identity、request snapshotのみ | actual DB/HTTP共通fixture、実Caddy/Browser/全nativeは別 |
| UserBusinessControllerTest | 16 | 602 | literal372/60/68/324/60byte、独立SQL version/audit/replay、100same-token | in-process実APIと普通独立process/brokerを分離、現source資格 |
| QuestionControllerTest | 23 | 605 | 検索/明細literal、QA048 locator/毎GET API/QA049保持・再操作 | APIreply stubの100並行は業務生成一回のDB証明でない、実API/JMS/CHR別 |
| TargetBusinessControllerTest | 14 | 608 | literal304byte、取消/削除の独立SQL/owner/99replay/CSRF | 実APIクラス＋専用DBと普通process/Artemis/nativeを分離 |

全100methodにはclass BeforeAllのWebLogDatabaseFixture起動がある。単体methodがmodel/valueだけに見えても、既存JUnitクラスの通常起動が純粋host処理になるとはみなさない。fixture内transaction設定失敗の資源保護BUG2245/YKT1991は共有の修理候補であり、100methodへ100回の修理費を割り振らない。追加必要実行数や個別runの許可は未確定で、100全件を未実行又は必要再実行と決めつけない。

既存083_NK-WEB-002通知取消・削除仕様（SHA9fc856dfea8c2bd56d0448ba4ed8f605decee436bde54d33b1f6d5f5fc693324）と1936の14method/family対応も再利用できる独立仕様資料である。元PG9554 manifest SHA1894885ded2b7d5bab5fc3ee741a8ea2bb0b1bc49665b5417c62158c01224f78はsource64446・構文抽出のみ/実行0。そこでのTest hash949db2…は現0c9d5b…と異なるため、旧行位置・旧実行成功・source資格へ読み替えない（c0a3fb）。差はimport明示化・複合変数宣言の分離等を含む（2f3837）が、この読取だけでruntime同値を認定しない。現位置はあくまで504/609から照合した。

候補100の静的本文照合は完了したが、各画面のruntime受入は未完。S全体は原通常PT参照不足2980中151本文照合、未レビュー2829であり、当100を151へ再加算しない。Current case参照不足2980、新Product試験0、coverage増分0、個別受入増分0、正式1964/53、工数率nullを維持する。技術3008/451も不変更。151/2980をPGPT完成率にしない。

費用比較では「stub wire/純粋projection」「実専用DB＋in-process実API」「実独立process/JMS/Browser/native」「保持/所有/UNKNOWNを含む受入全cycle」を別の適用条件とする。これらの件数から単価を作らず、旧共有8pp又は当S費を本体単価へ外挿しない。最初のVは同じ候補のHOLD/未達を保持し、この100レビューを第二VやV成功へ差し替えない。
