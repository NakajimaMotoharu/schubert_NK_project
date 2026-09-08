# Media query 探索記録

PG-D-071/PT-MED-008～014。2026-09-08、d986d3e基準を含むdev-media/f253e81上の新規未commit query/test、実PG18.6/本番Flyway・合成metadataのみ。

探索01: 新7method中6成功/1失敗、nullContractsAndJdbcMetadataFailuresRemainRedactedの最終fixture。Menu SQLはcount列だけを返すのに、testが未取得category文字列へNULLを注入しており、実際のDB読取は変化していなかった。期待「必須SQL NULL拒否」は維持し、集計numeric列のwasNullへ注入位置を修正する。Productionの変更なし、未実装初回fixtureの誤りでBUG起票対象ではない。失敗を合格へ算入しない。再現rawlogはwork外/tmp/PT-MED-query-explore-20260908-01.log、正式証跡にはproperties/stdout/SQL値を保存しない。

探索02（12:13:25 JST終了）: 追加7method成功。MediaRepositoryは443 instruction/36 branch/86 line/22 methodすべてmissed0、MediaQueryExceptionも全coverage100%。実PG上限と独立電文byte、異なる並び順・親/保存pair・100read/row lock非取得、全SQL/metadata/close故障のredactionを確認。探索結果を正式全reactorの代替にせず、次の正式PT-MED-20260908-02へ固定する。

Descriptor探索01（12:22:17 JST）: 10method中9成功/1error。新しい混合Music/Video fixtureで、Musicに割当てた合成PK10が既存Video fixtureのPK10と衝突した。DDLは正しく重複を拒否。Musicの合成PKを100～104へ分離し、logical ID/要求・MIME・表示・goldenの規則は変更しない。Production変更なし、初回fixture不備でBUG対象外。成功9件を正式合格へ算入せず、再度全10methodを実行する。

Descriptor探索02（12:23:18 JST終了）: 全10method成功、MediaRepository 626 instruction/40 branch/130 line/31 methodのmissed0。3 metadata入口の7format/I-A/不存在/type分離/ID照合/1024-1808byte/NULL・SQL・MIME/storage/path/255-256byte境界が成功。DB projectionだけではmanifest/物理inode検証・認可済HTTP配信とはしない。正式PT-MED-20260908-03へ固定する。
