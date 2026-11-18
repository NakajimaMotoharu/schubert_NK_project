# WebMetricContextの有限終了と固定mode

F03/2-2、P018-09、BUG-3286、YKT-2387/2691、SS351/354とUI252。1815／1823の元全33を維持する。

- WEBMCTX021／023／024／033は、元latch、Future、持続したowner、未確認close・二次解放順を保持。各finallyの明示shutdownNowと30秒のawait結果を使い、外TWRの二重待ちを除く。
- WEBMCTX004のnullと元unknownに、既式とは独立に固定した同hashの二異値を加える。SS351の未知mode拒否、SDK取得に進まないこと、固定文言を確認する。
- JDK25、既Micrometer/Prometheus十一artifact、自有メモリfixture、実接続・OS操作なし。MainとWeb公開仕様を変更しない。元33・同exec・物理CRC・生counter・支援不足の実測はPG39518で記録する。
