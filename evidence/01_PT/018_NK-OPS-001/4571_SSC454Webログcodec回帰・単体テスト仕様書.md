# SSC-454 Webログcodecの回帰仕様書

NK-MSG-002、MON-003、UI242、SS331 §9.3／351 §12／352 §11.2、BUG-3224／YKT-2674、451。担当の正規WebLogPayloadCodecTest全体を実行する。開始記録の九件に、元PG33790にも含まれる既存weblogOwn001を加え、正しい実行分母は10件。新規Test定義は0。

対象Test IDは元WebLogPayloadCodecTestの10メソッドと公開prepare.jsonの対応。既存の独立AAD・envelope vector、malformed/null/境界、並行workerの期限と終了、使用不能providerの固定例外、ciphertext・相関値の保持を維持する。canonicalAadAndFullEnvelopeMatchIndependentVectorAndCopiesAreDefensiveの診断期待一箇所だけを正本SS351の固定文字列へ変更する。前後差と同一Protocol176物理を公開manifestへ固定する。

専用のJDKテストプロセスと原合成fixtureを使用する。実サービス、実鍵、OS key store、VM、DB、Broker、外部プロセスと接続しない。実行コマンド、exit、環境、Test IDの結果、coverage未到達とhashは実行結果に記録。
