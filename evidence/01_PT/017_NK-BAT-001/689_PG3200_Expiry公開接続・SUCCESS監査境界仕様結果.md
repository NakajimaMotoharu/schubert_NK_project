# PG3200 Expiry公開接続・SUCCESS監査の境界PT

Program NK-BAT-001、Production CleanupDatabaseSession.forExpiry四arg・ExpiryAuditRepository.successful二overload。関連OPS009～017/DAT009/BAK、UI251252、SS331 §8/341 §9/343 child admission、SSC104/125/200、451。主担当P017-07.02とP017-11、RootReleaseAdmissionTestの補助fixture追加は既共通主担当へ重複課金しない。Main/DDL/設定/上位正本の変更なし。

## 独立期待値と試験

| Test ID・method | 入力/fixture/操作 | 期待・算出根拠 |
|---|---|---|
| PT-OPS-CDB3200001 / cdb3200001ExpiryFactoryRetainsRoleFreshSchemaAndClosesEveryOwner | 既実PG18の隔離Flyway V001～028、test-only EXPIRY actorの固定Root kernel、古い二migrationと正しい29履歴、公開四arg factory→execute | 古いreleaseはfresh schema二読目でcallback0/固定IOException/credential破棄。正しいreleaseは別child接続current_user=schubert_batch/autocommit/writable、observerがadvisory71419602を取れない間だけborrowed callback一回、終了後child.isClosed/lock取得可/credential破棄。Cleanup actorをExpiryへ渡すと構築拒否、release/context/snapshot null拒否。Production codecでexpectedを生成しない |
| PT-BAT-EXP3202001 / exp3202001EmptyAndSameRunSuccessUseLiteralAuditWithoutMutation | 実DB空→successful三arg、固定id42/run12345678/開始01Z/終了02Z・SUCCESS2/2/0/200/expiry cutoff9/5T15:00:00.000500ZをSQL insertし同runで検索 | 空Optional、成功時handleと11列snapshotを独立固定値で照合。照会の前後SQL terminal=SUCCESS\|2\|0\|NULL、borrowed transactionは未commit/未close。元run cutoffをDBから導出しない |
| PT-BAT-EXP3202002 / exp3202002SuccessRefusesForeignDayFutureEndNullAndSqlBeforeAnyRewrite | 上記固定SUCCESS、resolverが同ID別日の原本、観測がendedの1µs前、run/observed/owner/解決原本null、第一selectのSQLException/null statement | 別日/未来終了/SQL/schema不正は拒否、固定BatchRepositoryException/cause無し・SQL_SENTINEL非公開、null契約は境界拒否。成功行は元SQL状態のまま、borrowed connectionを勝手にclose/commitしない |

並行/advisory排他の実観測は新CDBと既CDB007、異常/cleanup複合は既CDB003～008を同class全十件で回帰する。監査は既五件を含む全七件。再送/日SKIPの同run/別runは既exp200001を維持する。秘密ではない専用fixture値だけを用い、配備原本DB・VM・native・鍵へ接続しない。NullPointerExceptionをcatchして正常化するProduction修正はしない。

## 実行計画・対象source

WBS group event0816で着手前低0.5/標準1.5/高4週次共有pp（P017-07.02=.2/.5/1.5、P017-11=.3/1/2.5）を固定、実費不明null。全回帰K01とN10 nativeは別既費で二重加算しない。基準Productiona9/host3691/542suite/1643Main/static六0（3054/3056）、native27（3190）、残659L133M5C483B。新Test三method/三Test file（共通helper含む）だけを追加した候補であり、旧whole成功を新Test集合合格へ流用しない。

Java25.0.4/GoogleJavaFormat1.36.1 skip-reflow-long-strings、PG18/JaCoCo0.8.15/ASM9.10.1、既server aruの隔離PG fixture。工具純一/完成server namespace0、source-format実apply済み。実行commandは既PYTHONPATHで `python3 -B tools/quality/pg3200_expiry_boundary_selected.py cleanup` と `... audit`。新-only PG3200/3202保存先、全入力Test/fixture/launcher/coverage hashと旧Main jar/fixture不変を照合、全十/七TestのXML/終了code/FES-aborted-notrun0と対象class counterを保存する。

現時点=実選択未実行、coverage増加/合格加点0。結果/source/日時/manifest hash/BUGは実行後追記する。選択後は必要な一全回帰（新Test集合3694予定/Root helper suite含む）と当native27の全Main/member同byte再資格を行う。工数null/正式1964-53/QA051final保留不変。
