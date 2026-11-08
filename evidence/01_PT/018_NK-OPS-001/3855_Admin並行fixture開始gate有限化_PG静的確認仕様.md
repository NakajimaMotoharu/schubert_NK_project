# NK-OPS-001 Admin並行fixture開始gate有限化 PG・静的確認仕様

G03.05主/P010管理関連追加費0、REWORK原0.5/2/5pp cap7。BUG2519/YKT2177。現UserCommandServiceTestのadm022 firstpool.startはCountDownLatch。submit全件完了前の失敗ではstart.countDownへ達せず、ExecutorService.closeが無期限workerを待ち続け得る。start.await一siteだけをassertTrue(start.await(5, TimeUnit.SECONDS))へ変える。既同class Barrier5秒/Future30秒と同じ有限fixture方針。元100試行/成功1競合99/独立DB期待102など全oracle・fixtureと全他byteを維持する。

scopeは当一Testのsource製造+独立PGレビュー/静的確認。実DB fixtureを起動する原classのPTはNOT_RUN_HOLDであり再現/compile/JUnit/coverage/JDBC/VM/サービス等を実行しない。source token/byte逆変換、typed宣言・submit/close前後制御、現在Main不変と対象hashを確認。静的結果はPT実行PASS/coverage/新規leaf/免除へ換算しない。旧23952の当source hash/arityは変更後の実物へ流用せず、元current indexは当一sourceについて歴史として保持する。原全Test corpus/YKT2177全体はOPEN。

修正前24176保存。元bugは原因とsource是正まで、真正DB再試験がないため閉鎖しない。元計画費と手戻り区分、fresh共有残量、正式1964/53・unique517/候補114/pending12/暫定whole93/工数null・G07・全HOLD維持。結果3856へ実変更/独立根拠/hash/未実施試験と再開条件を残す。通常区切りで停止せず後続許可済みPG/PTへ継続する。
