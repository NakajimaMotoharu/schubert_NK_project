# Media query 探索記録

PG-D-071/PT-MED-008～014。2026-09-08、d986d3e基準を含むdev-media/f253e81上の新規未commit query/test、実PG18.6/本番Flyway・合成metadataのみ。

探索01: 新7method中6成功/1失敗、nullContractsAndJdbcMetadataFailuresRemainRedactedの最終fixture。Menu SQLはcount列だけを返すのに、testが未取得category文字列へNULLを注入しており、実際のDB読取は変化していなかった。期待「必須SQL NULL拒否」は維持し、集計numeric列のwasNullへ注入位置を修正する。Productionの変更なし、未実装初回fixtureの誤りでBUG起票対象ではない。失敗を合格へ算入しない。再現rawlogはwork外/tmp/PT-MED-query-explore-20260908-01.log、正式証跡にはproperties/stdout/SQL値を保存しない。

探索02（12:13:25 JST終了）: 追加7method成功。MediaRepositoryは443 instruction/36 branch/86 line/22 methodすべてmissed0、MediaQueryExceptionも全coverage100%。実PG上限と独立電文byte、異なる並び順・親/保存pair・100read/row lock非取得、全SQL/metadata/close故障のredactionを確認。探索結果を正式全reactorの代替にせず、次の正式PT-MED-20260908-02へ固定する。
