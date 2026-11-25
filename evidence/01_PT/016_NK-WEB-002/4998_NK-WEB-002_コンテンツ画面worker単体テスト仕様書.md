# NK-WEB-002 検索・Scenario・Animation worker 単体テスト仕様

UI223、SS313、FUN-003/004/006、F03/2-2-b、BUG-3847、YKT-2997。合成画面入力と正規Maven処理済み資源のみ。対象の各並行fixtureは2 worker、8独立入力、各Futureおよび終了確認10秒。既各期待値をそのまま使う。先行検証とcleanupの二重失敗、単独timeout、割込みは同じ補助クラスで独立検証済みのPG45324を参照する。

| 対象 | Test ID・期待値 |
| --- | --- |
| AnimationBrowseTemplateResourcePortTest | PT-ABROWSE-DOM001～008。元の表示・件数・navigationと、008の別タイトル・main/OVAの行混在なし。 |
| SearchTemplateResourcePortTest | PT-SEARCH-DOM001～008およびPT-WEB-FRAG-003。元の検索条件・一覧・空・エラーを保持。008は別入力と別結果の本文を独立に保持。FRAG-003は相対contextを一回だけ適用。 |
| ScenarioDetailTemplateResourcePortTest | PT-SCENE-DOM001～008。元の明細と関連操作表示を保持。008は各タイトルと本文が別の同時入力を混在させない。 |

明示25件で元期待値の行を照合。失敗・エラー・スキップは0を合格条件とし、fixtureの補助や別画面の過去試行を件数に加算しない。実API・Browser・DB・実メディア処理は別。実行argv、Java、入力hash、Jupiter XML、静的結果をPG45326へ保存する。
