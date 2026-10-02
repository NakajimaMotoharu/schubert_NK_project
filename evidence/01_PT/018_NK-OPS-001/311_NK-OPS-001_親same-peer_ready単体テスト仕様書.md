# 311 親same-peer ready（SSC164）

Program NK-OPS-001/MorningStartupLaunchOwner/RootStartupContext/MorningServiceReadiness。
RD SYS002/004・OPS009、UI212/251、SS342§4.2/5.2・343、D05同S3接続。

| Test ID | 入力/操作 | 独立期待値 |
|---|---|---|
| READY428001 | 固定proc status/main、同inode、HTTP literal5値 | 前後同親/子guard3回・ordinary2回・socket2回。差inode/消失/identity driftはfalse |
| READY428002 | UID/GID/groups/NNP/各5cap欠落・誤値、main0/重複/末尾NUL欠落、長大/非ASCII | mandatory field一つでも違えば拒否、未知statusは非成功、root UID0をordinary成功にしない |
| READY428003 | 503/301、DOWN/余分property、config001/schema023などwrong info | exact200UP/保持署名manifest5値のみ許可。期待値は独立literal、production serialization不使用 |
| READY428004 | IO8地点/guard3地点失敗、portのnull応答 | IOException又は境界null違反を伝播、NPEをcatchして正常扱いしない |
| READY428005 | Linux tcp/tcp6 literal、本人/他inode、wildcard/::1/他loopback/port/state/truncated | exact1278091のIPv4又はmapped v6かつLISTEN/本人inodeのみ。Webはfixed8081で同条件 |
| READY428006 | expected map欠落・非法version/hash | 構築拒否、INFO応答からexpectedを作らない |
| READY428007～009 | API→Web成功、各段のIO/runtime/Error、null returned owner | 真の成功ではlive owner保持、失敗では返却済slotだけWeb→APIでstop。native未捕捉slotの保全は別VM条件、stub成功をnativeへ算入しない |
| READY428010～012 | host本人proc・本人owned1278091の実HTTP、503/302/4097bytes/NUL、NOFOLLOW/length/errno/固定PID・port | 実kernel/HTTP部品を照合、redirect無し/境界拒否/close。単体IO検査であり人工的外部Main呼出し又は実NK起動合格ではない |

Host package-local IOは部品PTだけ。native入口/Root generation/owner・permit readback/各syscall及び停止・timeout/intent後条件はVM同Source採取で別閉鎖し、人工的main呼出し/除外による100%は行わない。変更methodはhost seamで正負を採取、native private IOは実Morning/同peer Unitへ接続し、現普通JVM coverage未採取問題を別追跡する。全coverage要求は変更しない。

実行command/環境/source/coverage/BUG/SSC/hashは選択run後manifestへ記録。現実装・選択PT実行中、未実行は合格算入しない。全6は同起動契約接続群を固定後に行い、工具だけのPG427保存では再生成しない。

17:41 v6選択：Protocol5/Storage8/Bootstrap10/API5/Web4/Batch28=60PT、9class、FES0/static6zero/strict compile/format成功。private `Work PG379/pg428-ready-selected-v6.log` SHA d225d96b13d20e0f3036cf0506667d19234790641af57baa10d21c8ca8488319。v1 no-tests/初回不要suppress/v4 production型推論/v5新PT型推論失敗は合格へ算入せず、BUG524～526に記録、selector・不要annotation削除・型明示後のv6だけが成功。native外部Main/親全ready/100%は別未合格。v6には実本人proc/socket/HTTPを直接観測した部品3PTを含むが、同Source VM全起動を代用しない。変更群固定全6を次に実行し、新規/既存/解消未網羅はfullで照合する。
