# 073 NK-WEB-002 operation token v2 単体テスト仕様書

PG446/PG-D356、QA049/SS314§7.2.1・末尾承認補足/SS343切戻し、RD FUN001/AUT001～004/MQ021、UI226/236。対象SessionOperationToken、SessionAttributeCodec、後続current-row lifecycleとSpring delta。現行encoder v2へ移すのは承認済み変更、旧v1 strict readとNKENC1/AES-GCM/AAD/DDLを保持する。全Web/native起動や工程認定と分離する。

| Test ID | 目的・fixture・操作 | 独立期待値／根拠 |
|---|---|---|
| TOKV201 | 3引数pending、4引数Optional完了、issue同時/以後/以前、null/未知purpose | completedAt空はpending、完了はissuedAt以上。不正は拒否。redacted toStringのみ、purpose/UUID/time不変 |
| TOKV202 | public手書きv2 UTF8 JSON、pending＋consumed混在、encoder byte/decoder属性 | formatVersion2、purpose/token/issuedAt/completedAt順。expectedはSSのliteral JSONで作る。production encodeでexpectedを作らない |
| TOKV203 | v1旧3fieldgolden、v1にcompletedAt混入、tokens→formatVersion逆順 | v1 pendingを読む、v1完成印は拒否。key順序不問、decoder結果再encodeはv2 |
| TOKV204 | completedAt null/number/object/array/duplicate/unknown/欠落必須/非canonicalUTC/issuedAt以前 | 全拒否。NPE catch正常0、unknown鍵/型/JSONversionは緩和しない |
| TOKV205 | 混合10要素/11要素/全8用途/µs境界/100並行 | 合計10まで、順序/独立日時/他session非混入。line/method/class/branch全100を新対象へ要求 |
| TOKV206 | 独立NKENC1＋DataOutputStream AAD/JCE、v1復号/v2暗号、破損/前key/16KiB | envelope/crypto/AAD不変更、legacy readの互換。秘密はpublic synthetic vectorのみ |
| TOKV207 | 後続fresh current-row issue/require/complete、全pending10、consumed oldest/tie、first-write/retired | pending不退役、必要時最古consumed1件だけ、初回完成stamp不変。不在/退役409/API0/新UUID0、JMSとDB同時保持0 |
| TOKV208 | current-row並行100/stale delta/削除・失効/commit・close不明、固定SQL後条件 | 完成をpendingに戻さず、退役再挿入0、他token不消去。失効row非再生成、不明commit/close成功化0 |

PGと独立仕様・JUnitを並行作成。TDDの未実装v2初回失敗はBUGへ算入しない。実装後の仕様違反は修正前915/必要916へ登録する。旧WEB009～023等はencoderの承認v2 oracleだけ更新し、legacy readerのv1負系/互換を消さない。新scopeの選択6reactor clean/format/compile/PT/static/4counterの後、変更群はsession/security共通と判定し451の同Source fresh全6回帰→安全採取/byte freeze→全Web/nativeへ続く。

環境421/451のJDK25.0.4/Maven3.9.12/Node24.19.0、offline M2を使う。実command/source/日時/実結果/coverage・BUG・manifest/hashは074へ追記する。failed/skipped/flaky/not-runを加算せず、token/CSRF/session/key/rawDB/credential/原本はGitへ入れない。現時点全Test IDは実装/実行未完了、正式認定run24/1964/53は据置。
