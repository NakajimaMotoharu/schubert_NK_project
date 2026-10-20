# 1236 API三owner十二表現の製造・単体試験仕様

PG-D447/BUG1509/YKT1269、WBS-F03主費（User/Media/Idempotency関連Program参照費0）、開始.5/1.5/4pp、原v3v4不変更。着手時source7a664ce0a・分類5910-v2/283a0330を基点とし、当十二全て未点検を照合済み。実PG後の新source/hashを結果へ固定する。

- UserCommandService：条件version999999999のprivate定数化と七p++の別statement化。PT-ADM014～023/UserCommandServiceTest10：独立SQL後条件/JCA/六operation/監査/再送/最後ADMIN/楽観競合・null・失敗rollback。SQL/bind値/順は既literalsから検証し期待値にProduction methodを使わない。
- AssetChecksumManifest：read代入/line index増分を独立statementへ、byte LFを命名。PT-MED041～044/AssetChecksumManifestTest4：固定abc SHA/UTF8パス/partial/zero-read/EOF/最大/未知/並行/例外/borrow未close。実masterやdeploymentファイルを使わない。既UseConcurrentHashMap根拠はsource変化のため要再点検であり自動転用しない。
- WipingByteArrayOutputStream：reserve後buf[count] store→count++分離。PT-IDEM-WIPE001～003/SecretBufferTest3とResponseSnapshotCodecTest7：全容量消去/旧配列/最大/境界/例外/返却copy所有、固定nonce独立圧縮/AAD/JCE。四synchronized overrideは親BAOSとの同monitor整合・Production呼出しscopeの非公開局所所有を強化点検し、raw指摘は削除/抑制せず個別根拠を残す。実secret/heap/nativeアクセスは行わない。

選択35/10：API24とprotocolGolden3/storageEnum1/bootstrapEnum1/WebRange4/batchEnum2。全六format先行→offline package/通常PT/JaCoCo/SpotBugs。PT_DEFAULT、自己所有hostの新only私有snapshot、UserCommandServiceのDBは既ApiLogDatabaseFixtureによる新temp PostgreSQL18/loopbackランダムport・本sourceのFlyway/grantだけ。実VM/Unit/current/原本DBBackup/鍵/permit/failed-cohort/実ADMIN操作は不使用。fixture stopは当fixtureのtemp DBのみ、環境変更/権限取得/拒否探索を含まない。

予定command=canonical PYTHONPATHで`python3 -B tools/quality/pg5912_api_expression_selected.py`、後続`pg5914_api_expression_static.py`。fresh枠>10/clean source/未使用namespace確認後一回、全851source/1666Mainの宣言三outer＋必要nested/debugだけ差、公開ABI不変、無除外PMDのcompound十/条件二消失・他rule保持を照合。実line/method/class/branch/XML/command/OS/JDK/source/run/hash/BUGは1237へ、未測定を100へ補完しない。必要global全体は残変更群とまとめる。旧source3973/199/native/正式の成功を新sourceへ輸入せず、PT代替完成0、PG/PT全体完了ではない。
