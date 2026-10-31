# Cleanup/Expiry 公開codec原whole十六 仕様

2026-10-31 / PG-D981 / 群3397 / 主P017-07.02・関連P017-06追加費0。
開始1/3/7共有pp cap10、freshused51/reset1793774153、専有費・実tokennull。

Program NK-OPS-001、CleanupWorkerRequest（outer/Expiry/PriorExpiry全337行）、原ExpiryWorkerRequestTest七/ExpiryRequestBoundaryTest二/CleanupWorkerRequestTest七のwhole16。関連OPS009/BAK001/UI251/SS341・342・343SSC104111117200、SS343624/743/965行等。先行索引ExpiryWorkerRequest六件/CleanupWorkerRequestTest四件から855/2356等を確認。全三Test・Main・BatchRun/BatchStep/BatchStepAttempt/MaintenanceActivation/CleanupProfileを全文照合済み。

PT_DEFAULT。操作は自己byte/String/UUID/Instant/Optionalと自己二virtual taskのみ。Expiry TestのUUID.randomUUID三箇所はJDKの合成fixture生成で、entropy使用あり・秘密key/実資格読取なしとして開示する。非秘密run/boot/epoch/broker/manifest文字列は手書きdataで、実行許可・認証・DB所有・削除・Unit操作を発行しない。実Root/noargs/cohort/Backup/native/Graph9/VM/DB/JMS/鍵/私有raw/外部接続0。既HOLDのTestからの部分抽出・差替えはない。

独立oracleは原Testの手書きNKCLEAN1/NKEXPIRY1/NKEXPIRYSKIP2の全ASCIIbyteと固定UTC日時・UUID・整数・key順/LF。Production encodeをexpected生成に使わない。Expiry：全16必須field/未知・欠落・先頭zero/年9999上限/µs対ns/null/異run同JST日・元handleのid/attempt/start/end、成功失敗全byte消去・redaction。Cleanup：四field/順序・重複・範囲・nil/distinct/null/hex/framing/非canonical/再送・二task独立buffer。encode roundtripだけで正しさを証明せずliteral全byteを照合する。

原16を一fresh JVM/単一exec、固定Java25.0.4/normal14216 source6b53六jar・全Main/Test byte固定、180秒の外側budget、F/E/S/aborted/flaky/not-run0を要求。Expiry九とouter七は同一Source全三physicalの分母を一execで測定するため必要であり、旧成功確認目的の再演ではない。元別source2356/855のPASS・coverageは転用しない。helper四Sourceの既証明は保持し、今回targetとして再受入しない。

PG16012で元XML/command/exit/exec/hash/一session/CRC/全Source closure/四counterと四held六native真probe0を受動測定する。未達counterを保持し、filter/除外/合成coverageで100%にしない。PG16014で別Pythonによるliteral goldenとbyte長/field順/境界算出、全原case/TestIDとnegative metadataを照合する。静的/管理検査はProduct PTに加算0。

後段registry/WBSは元全field/歴史proof/費用/正式を保持し、現在普通宣言5786への厳密参照だけ増分を接続する。QA051final・451・正式1964/53・工数null・全HOLD不変更。実装済み機能の仕様違反は修正前BUG/YKT、上位設計不足は既分類を適用する。
