# 1582 FilesystemHealth観測 単体テスト仕様書

NK-OPS-001/P01809/C07、RD171 MON005..013/UI252/SS351§7、PG-D529。対象FilesystemHealthObservation constructor/read、FilesystemHealthMonitor constructor/observe/snapshot、既TimedFilesystemMonitorへの接続。新依存なし、実Root/VM/DB/ネットワーク/鍵/配備/私有filesystemを操作しない。FileStoreはcallerが既に検証したfilesystemを借用、解放/新path受付/owner認証/collector周期・timeout/制御は当部品が行わない。

JDKのtotal/usableを健康観測用の使用率100×(total−usable)/totalへ変換する。標準Micrometerのdisk.freeのusable-space意味と整合する内部health inputで、独自metric名/label/exporterを追加せず、SS351の製品標準metricを置換しない。原本/実配備filesystemの同定・性能/同時変動時の実測保証は後続HOLD。二統計が不正/IOExceptionならUNKNOWN、未観測を0%/正常回復へ変換しない。unchecked Runtime/NPE/Errorはcatchして正常扱いせず同一伝播、外側の失敗処理・再開時continuityは後続owner契約。

| Test ID | 目的・入力・操作 | 期待値・独立oracle |
|---|---|---|
| FSINPUT001 | 固定FileStore total1000/usable1000・200・100・0/読取回数 | 0/80/90/100、各getter一回、path/name/toStringアクセス0。固定算数表。 |
| FSINPUT002 | 総量0/負、usable負/>total、復旧後の正常 | Optional.empty、0%成功捏造0、次正常80の不変入力。 |
| FSINPUT003 | 各getter IOException・非formatable IOException | UNKNOWN、例外原文/formatter/label0、第二getterの実呼出順。 |
| FSINPUT004 | getterのRuntime/NPE/Error | 同一例外伝播・再試行0/暗黙正常化0。 |
| FSINPUT005 | Long.MAX_VALUEとtotal1の全空/全満 | 0/100、long乗算overflow0。独立整数vector。 |
| FSINPUT006 | total10^18で80/90/95の一byte直前・丁度・直後 | 直前はIEEE754の直下literal bit値で境界を超えず、丁度/直後は当整数threshold以上。BigInteger除算の独立境界表。 |
| FSINPUT007 | constructor null/64並行独立read/入力不変 | 明示null拒否、固定全80/読取各64、FileStore所有拡張0。 |
| FSINPUT008 | 入力80継続300秒→warning、90継続60秒→critical | 固定UTC・elapsed・Severity/count、既SS351境界を接続端から確認。 |
| FSINPUT009 | critical→正常→IOException/不正統計→正常10分＋原因確認 | UNKNOWNが回復期間を切断しevent/countを保持、欠測を正常として閉鎖0。 |
| FSINPUT010 | null/context逆行/gap/64同elapsed並行poll | null時provider0、逆行はstate不変、gap切断、同一ownerは読取/observe直列・独立event count。 |

fixtureは自己所有のFileStore実装（固定byte/明示IO故障/原文非formatable）、本番FileStoreへの接続証明とは区別。expectedにproduction methodを呼ばない。正常・境界・異常・例外/null・並行・UNKNOWN回復を新10件として同監視packageの必要回帰と実行、未実行をPASSにしない。通常親lint/Werror/NullAway/Spotless/SpotBugsと当実class CRC/四counter/静的全指摘・実Jar/traceを新sourceへ結合し、実行結果にcommand/環境/commit/終了/XML/hash/BUGを記録する。全体451/native/CHR/正式受入とは別。
