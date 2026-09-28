# 215 NK-OPS-001 Morning DB能力継続・単体テスト仕様書

Program ID: NK-OPS-001。PG346。対象: `MorningDatabaseSession.Access`、`MorningNewRunAdmission.executeOwned`、`MorningResumeAdmission.executeOwned`。関連RD OPS-009/BAK-001、UI251、SS331 §8.3、SS341 §6/7/11、SS343 §6.15、SSC-055/094/104。親M・専用DB advisory・原本file所有を保ったまま、停止とA後の同run backup beginおよびCleanup handoffへ同じDB能力を渡す内部境界を試験する。公開Connection/passwordは渡さず、callback離脱後は既存`MorningDatabaseSession.Session.guard`が使用を拒否する。

| Test ID | fixture・入力・操作 | 独立期待値・根拠 |
|---|---|
| PT-OPS-MNEW011 | 固定UUID/cutoff、fake DB/File owner、既存参照0、新run | 参照不存在→原本start→同じowned callback内でDB/CONFIG二begin→handoff→後続→File/DB逆順close。step種類/順序はSS341 §6/7のliteral |
| PT-OPS-MRESUME010 | 固定既存run/cutoff、fake DB/File owner、参照整合、明示resume | DB owner取得→原本resume→参照整合→元run/cutoffによる二beginとhandoff。nowは元cutoff+1秒、recover flagはtrue。別runや新cutoffを創作しない |
| PT-OPS-MCTRL012 | 手書き親M/A/DB原本owner・固定run/cutoff、fresh8とINVALID | `stop8→fresh8→INVALID→同じDB能力によるbackup begin→原本/DB/M/A解放`。backup能力をA/INVALID前に使わず、原本と3排他が継続する。SS341 §5/6、SS343 §6.15 |
| PT-OPS-MCTRL013 | Owned境界のoriginal/stop/A/terminals/INVALID/work各null | M取得前にNPE契約拒否、file/DB/stop/worker0。nullを正常化せず捕捉しない |
| PT-OPS-MDB既存 | 実PostgreSQLとfake JDBCの専用session | callback失効/別thread/二重begin/commit不明/子handoff状態を既存MDB1～14で回帰。新Accessの外部漏洩を許さない |

期待値は手書きevent列・固定step enum/ID・実DB後条件で作り、production methodからexpectedを計算しない。正常、異常、null、境界、並行、再送は既存MNEW/MRESUME/MDBと併走して確認する。`Access`は操作能力でありraw JDBC handleを出さない。外部`MorningControlScope`への実引渡し、worker起動/backup現物/expiry/permit、実VMは本仕様の未達条件であり、選択PT成功を全親受入に使わない。coverage除外なし。実行command/環境/source commit/4指標/結果/証跡path/hash/BUG・SSCは216とmanifestへ記録する。
