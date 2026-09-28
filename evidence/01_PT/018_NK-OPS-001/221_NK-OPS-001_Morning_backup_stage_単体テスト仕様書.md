# 221 NK-OPS-001 Morning backup stage・単体テスト仕様書

Program ID NK-OPS-001、PG349。対象`MorningBackupStage`。RD OPS-009/BAK-001、UI251、SS331 §8.3、SS341 §5～6、SS343 §6.15、SSC-089/092/094/104/105。Productionの新run/明示resume入口から、同M/A/原本/DBを保持する`MorningControlScope`→durable current INVALID→両backup step begin commit→固定request root new-only公開→同じowner内の後続callbackまでを接続する。実backup Unit/manifest/cleanup/permitは後続未達。

| Test ID | fixture・入力 | 独立期待値 |
|---|---|---|
| PT-OPS-MBSTAGE001 | fake owned scope・固定state/DB、固定時刻/part | `scope-enter→DB両begin→publish→work→scope-close`。work中もowner保持。SS341 §5～6 |
| PT-OPS-MBSTAGE002 | 明示resume、元run/cutoff、recover=true | 元runのままDB begin、別runを選択しない。SS341 §3/6 |
| PT-OPS-MBSTAGE003 | scope/DB/publisher/workerの故障 | 後続をsuccess化せず、既存scopeのclose規則に従う。公開前失敗ならpublish0 |
| PT-OPS-MBSTAGE004 | null port/clock/part/work、割込 | IO前のnull契約拒否、割込は下位gateで非成功。 |

期待値は手書きevent列・固定UUID/InstantとSSの順序から独立作成し、production methodを期待計算に使わない。既存215～220のowner・DB・file異常/並行/再送PTと併走。native factory/実VM、外部Morning main、worker全終端と正式coverage100%は本PTの外で未達として明示する。実行command・環境・commit・結果・coverage/証跡hashは後続結果書に記録する。
