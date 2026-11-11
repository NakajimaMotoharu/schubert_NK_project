# A4-01 SavedRequestTarget 原四試験

Program NK-WEB-001 / owner WBS-P015-02、BUG2623 / global YKT2177。
関連 FUN001、AUT001～004、UI221/226、SS314 §7・352 §3。第65版A4-01標準1.50pp、旧候補低0.5/標準1.5/高4・cap5を保持。

対象は SavedRequestTarget.fromGet/location/toString と原 SavedRequestTargetTest の全4件 PT-WEB-005～008。Production Mainは変更しない。入力は公開合成URL文字列のみ、URI parseは外部接続を行わない。DB/JMS/VM/認証発行/鍵/held4を使用しない。

| Test ID | 操作・独立期待値 |
|---|---|
| PT-WEB-005 | 固定14相対パス・queryを文字列で照合。queryのNFD/percent表現を保存、toString固定REDACTED |
| PT-WEB-006 | nullはNPE契約、GET以外6種類・不正固定URL29種類はIAE。message固定、cause null/suppressed0 |
| PT-WEB-007 | UTF8 2047/2048byteを受入、2049byteを拒否。日本語681×3+prefix5=2048、surrogate単独拒否/正当pair保存 |
| PT-WEB-008 | pool10/合成100リクエストの独立文字列、get20秒を保持。finally shutdownNow→awaitTermination10秒をassertし正常/例外帰還のowner解放を有限化 |

期待値は元の固定literal・UTF8の独立算術から作り、Productionをexpected生成へ使わない。元Git blobを修正前に保存し、追加終了処理の逆変換で全body/literalを復元する。原4の削除・抜粋・新case加算なし。異常を誘発して無期限hangを起こさず、元source観測をbefore証拠とする。

実行はJDK25.0.4、JUnit Console1.13.4、JaCoCo0.8.15、ja-JP/Asia-Tokyo。1072 before/prepare生成→1073設定固定静的→preflight封印→source通常commit/push→pg26018原4一回→独立post。同source・Test hash・Main class byte/CRC、全四counter、F/E/S/abort0、終了code、worker資源後条件を照合する。実command・対象commit・日時・環境・結果・manifest hashは3999に保存。全Maven/実環境/正式451は別HOLDを維持する。
