# Format不整合・是正・必要全回帰再試行

PT-OPS-2918-001/2930-001、BUG1258/YKT1024、411/421/451/487、WBS-K01の同campaign再試行（追加leaf予算0）。Production a9/PG2802、Main/設定/期待値/既原本/配備/guest不変更。

## 失敗原本

PG2918/session32747、snapshotbd882a07788cd441d70fa69fe07795b069b6372b、actual1/Maven1、20:57:59.122538Z～21:17:52.247864Z/1193.125326秒。五module2400PT/FES0の途中XMLは保全するがbatchPTはformat gate前拒否/未実行、全体不合格。Main source inputは全不変。batch Session Test三hunkだけ正規Spotless結果と異なった。失敗log/archive/manifest/XMLの上書き・成功読み替え0。

## 原因と独立再現

CLI standaloneとPOM/Maven coreはすべてGoogle1.36.1。版差という初期仮説は実version/hashで棄却。Spotless3.10.2/lib4.10.2 installed primaryのjavapでdefaultReflowLongStrings=false/iconst0を確認。Maven正規apply後、CLI default dryrun1・skip-reflow-long-strings dryrun0という同version差を再現。CLI既定のlong-string wrapping後の結果をMavenと同じと仮定したのが原因。

Maven正規applyは347file中Session一file三hunkだけ、Main差0/Oracle値差0。Maven全六module spotless:check終了0を独立に確認。411/421へ正規設定と再現手順を追加しPOMは緩和0。完成2930 serverは、PT開始前に全六moduleのSpotless gateが非0なら拒否する純fixture/static0を先行。Source2486の想像値/除外/版変更で合格を作らない。

## 正しいTest入力と再試行

new2926/session80656 actual0、formatted Test source0e03e22b1da081fa7cc8f2f2c15367fabd275f8b、実Session全61/FES-aborted-notRun0/原SQL・close後条件、payload9b438175a638861133c22d3c9a4ed46d3c6e565a477b0f8c4f3b51a25fa5124e、LANmanifesta5f300bf3d63fbd36c3367959d8ef76eb5d3a7064ac0105602dcf6515e09b6fa。既6 failedPairのTest source byteはapplyで不変更、実2916成功を入力に使う。旧61 successは旧format sourceとして保全し現在inputへ単純加算しない。

new2930/session95452、snapshot649348029d28e05597cabaf25a2d6bcfe7b21a8e、開始21:32:17.315232Z。全六format-preflight実BUILD SUCCESS、その後新全3684/542/1643/static六実行中で未認定。終了コード/XML/coverage/静的/全inputを2932で独立検証し、2934で全Main-resource-META一致条件付き同a9 nativeを資格する。完了後追補、正式1964/53/leafdelta0/effortnull。旧2920/2922は失敗2918へ未dispatch、Root/Backup/ADMIN/VM採取の再発行0。

WorkPG379 `pg2918-server-six-v1`、`pg2926-jdbc-format-selected-v1`、`pg2930-server-six-v1`、aru `runs/PG2918-six-v1`/`PG2930-six-v1`、各原manifest/command/source/OS-JDK/version/時刻/hashを保全（raw privateは非Git）。CLI/Mavenshaは421、PYTHONPATHは838。actual違反発見→915/916先行→修正→new-only実試験の順を維持。
