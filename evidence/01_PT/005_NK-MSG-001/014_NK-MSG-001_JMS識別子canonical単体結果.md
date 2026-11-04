# NK-MSG-001 JMS識別子canonical単体結果

対象commit/Production Mainは`b09393b0e746b55fd480176d57996d65bd76a95d`、branch dev-foundation。013/692の独立UI232 oracleを維持。二箇所のparseUuidで元文字列を検査し、短縮/大文字を正規化して受理するBUG2263を是正。API/Webの第7method各1、計2新規Test、各正常1＋異常10で計22 vector。

| 実行 | 真正結果 | 扱い |
|---|---|---|
| PG18634 | compile0/unit1、2試験2failure、driver14205/d56714は0 | 実装済み旧6bの仕様違反再現。PASSに含めない。 |
| PG18636 | 四Source compile/format/CS0、PMD raw10/exit4 | thread専有Map/standalone Proxy loader/identity equalsの適用性を全10件説明、Main違反0。全F03ではない。 |
| PG18638 | source-local javacの14成功 | Maven成果物とのdebug byte差を694で検出、限定原成功として保存。normal qualificationに転用・合算しない。 |
| PG18642 | 六module build/Enforcer/Spotless/NullAway0、PT0 | Test sourceは名前段階で入力から除外し未compile/未実行。製造buildの成功で、PT PASSではない。 |
| PG18644 | 通常jar＋固定Testの14成功/FES0、4320/49c6a9実0 | 原6×2と新1×2。独立post4b2fa5・cc9609でSource/Git・全14case/22vector・実XML・singleexec/CRC/通常jar一致を確認。 |
| PG18646 | driver1、BugInstance0だがMissingClass計18 | 原失敗保全。旧cache module参照の工具不備BUG2265、静的PASSではない。 |
| PG18648 | 4775/9e73e1実0、全六module指摘0/解析エラー0 | 同invocation package→SpotBugsで現reactor参照へ是正。全aux module path/hash・元jar入力不変。 |

API JmsMessageGuard: line66/method10/class1/branch42、Web JmsReplyDecoder: line70/method10/class1/branch40、全counter未達0。CRCはそれぞれ`10d925165591aabd`/`8f2ccd699ecb1e73`、session`PG18644-JMS-CANONICAL-NORMAL`、probe66/66・70/70。通常artifactから抽出した対象classと実execを照合、手動除外・旧exec合算0。二Sourceの変更後証拠であり、他Mainや全体coverageの100%ではない。

PG18644 post初回f0dd99/1はConsole名の括弧差でpublic作成前拒否、BUG2264/YKT2009へ修正前起票し原全文695に保全。Source method/selectorとの厳密noarg名照合、誤suffix/欠落/未知名/他classの四反例＋既metadata八反例を確認、元成功PTは再演しない。BUG2263/YKT2008・BUG2264/YKT2009・BUG2265/YKT2010は現結果を検証、公開前状態はFIXED_VERIFIED_PENDING_PUBLICATION。

環境/command/input/実XML/期待値/実際値/hashは696と各public manifestに一意追跡。正常providerはown JVM Proxy、SDKは未接続destination値だけ、実broker/DB/Root/VM/native/key/session業務発行0。元DB/Backup/鍵/held/原18474OS未知と全HOLDは保持。原Null/空/欠落/未知値も元全classで成功しNPE catchによる正常化なし。IT/ST・CHR・全451・F03全域・親leafは未受入、正式1964PT/53scope・歴史17/190・工数nullは不変更。

主証拠 `evidence/provisional/PG18644-jms-uuid-normal-post-v1/manifest.json` SHA`5cafcb6a2f2d4a8b61dcc33a614de0338b5e4dc99980da102a10a1f0ea8d3ba6`、全Main build SHA`53760b6da806d104be630340aa34666194d57eceb90cbce2c10cc6f8a71b6315`、全六静的 SHA`83bbe2ec7f999ae69ba4795ef23e07534ee4b9699045e64c4e0fdb56bd484254`。
