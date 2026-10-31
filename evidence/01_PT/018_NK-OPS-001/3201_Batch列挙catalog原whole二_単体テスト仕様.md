# Batch列挙catalog原whole二・単体テスト仕様

2026-10-31。Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c/normal14216。NK-BAT-001/NK-OPS-001、UI251、SS331/332/341/342/343、1185/2299/1922/1924を参照。PG-D1029。主費用WBS-F03、canonical P017-02/P018-04は参照だけで費用追加0。群開始見積1/3/6共有pp・上限10を固定し、専有費/実トークン/工数率はnull。

対象は既存batch.repository/platformのEnumValueCatalogCompatibilityTest各whole一件（PT-F03-ENUM-BAT001/OPS001）。現registry16466に両case参照なし。旧5732等は別sourceの歴史証跡として保持し、新sourceへ転用しない。Test/Production/期待値を変更せず通常六Main Jarとfresh二Test/launcherで実行する。同じsimple class名でも完全修飾名を区別する。

期待値は原Testの独立literal表：十BatchStepとbackup二件、九CleanupKindのSQL名/上限1000・logs10000/step、SUCCESS0/WARNING10、固定Application二/Maintenance八/Rootサービス五/観測八/開始対象五の名前・順序・Unit/cgroup・directory/marker、全serviceとnullに対するownedBy対応、全八enumのserialized field0/UID0。Productionをexpected生成に使わない。固定immutable値以外の並行・再送・取引は対象外で、その実処理を実行済みとはしない。

全八Sourceのphysical closureを残し、未実行の外側・native実装をcoverage分母から除外しない。既測定五Sourceのより広い合格証拠をこのenum-only測定で置換せず、新ApplicationUnit/RootStartupContext/BackupUnitStartClient三Sourceだけ現registryへ追加する。Root/Backupの外側は未実行として未達を記録する。branch0は自然0であり四counter100へ加算しない。既coverageとのexec unionは禁止。

全Main/Test/到達enum bodyと外側の初期化・Source、先行1185を読取済み。実行はenum getter/values/serialization descriptorに限定し、外側factory/create/start/retire・proc/Unit/intent・回収・権限操作を呼ばない。RootFailedStartRecovery内容/Graph9/VM/既存DB/broker/鍵/私有rawは非接触、HOLD解除0。保存execを受動検査して四held/六nativeと外側操作のprobe不在を照合する。未実行は未実行のまま、正式1964/53・歴史17/190・QA051final/451/HOLD不変。

予定commandはchecked entry経由pg16476→16478→16480、その後registry/独立post/WBS両sideを照合する。原PTは一回のみ、F/E/S/flaky/not-run0、原run/source/終了code/XML/exec/環境・全closure/hash/静的14224を記録する。失敗は修正前915/916へ起票し、元証跡を保持する。新規受入は個別criteriaが閉じるまで0。
