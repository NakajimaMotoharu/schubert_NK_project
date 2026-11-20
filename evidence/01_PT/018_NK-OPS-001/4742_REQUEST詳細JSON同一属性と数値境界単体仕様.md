# REQUEST詳細JSONのフィールド同一性・数値境界

NK-MSG-002、WBS-P018-10.02/2、P018-10.03/2。UI235 §12.2、SS351 §3.3、SSC-008、PT-IDEM-012。対象 `RequestLogDetails.normalize`。Java 25と既Gson 2.14.0で、JSON文字列と独立Role値だけを供給する。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| PT-IDEM-012-JSON-001 | `truncated`と同じUnicode escape表記を単独・重複・逆順で供給。Role表記のescapeと、独立Role USER/ADMINを供給 | 単独で既定フィールド名に正規化。表示Roleは別入力のみから設定。同名重複とDetails内のRoleを拒否し、固定診断、causeなし、suppressed 0 |
| PT-IDEM-012-JSON-002 | `responseBytes`に0、-0、+0、0.0、0e0、0E+0、文字列の0を個別供給 | 0だけを数値0として保存する固定JSONとRole。SS351の符号なし整数契約から他は永久不正、固定診断、causeなし、suppressed 0 |

既5件（PG37348）と独立UTF-16境界1件（PG40218）の実行は再演しない。実ログsink、DB、稼働環境、当WBS全入口・451の成立は別に確認する。新規選択結果と対象source/fixture hash、コマンド、静的書式、測定カウンターは今回のmanifestへ記録する。
