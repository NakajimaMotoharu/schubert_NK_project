# 1738 Prometheus公式構文parser 結果・toolchain記録

NK-OPS-001/WBS-P018-09/C07、1737/PG-D583/RD171 MON010～013/UI252253/SS351。group1964/元開始0.5/1.5/4pp/cap10。当設定は不変更、元1730/1731の未実行だった公式parser工程のみを限定閉鎖する。実Root/VM/DB/サービス/配備等HOLDを解除しない。

## 工具の初回導入

Prometheus LTS3.13.5/linux-amd64（公式公開2026-10-21）のtool-only配布。公式入手URL/参照URLは1737とPG8162、archiveSHA **0388822ace519c5a3a8ef556a541ce1b536e21d872f82deded465bd27a5a0699**（公式download掲載値と一致）。work/toolchain/promtool-3.13.5-linux-amd64へnew-only保存、promtool/LICENSE/NOTICEのregular3memberだけを抽出。サーバbinaryは抽出/起動0、既tool/設定の上書き0。TLS＋公式掲載SHAでありvendor署名検証済とは称さない。

promtool本体SHA **4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff**、owner-only mode0700、実--version終了0/3.13.5。原archive/binary/license/NOTICEはGit外のtoolchain、public manifestへpath/byte/hash/version/command/開始終端を保存。Tool準備source **0c24698fc** と構文PT対象source **941bd89d15da0d37c2023c7ce9536b9845311779** は役割を分ける。コード/既profile不変更、Java/POMへの依存追加なし。

再現は未導入の新環境で既toolchain/W親を用意し、1737の固定URL/SHA・hostLinuxx86_64/容量を確認、固定sourceのpython3 -B tools/quality/pg8162_promtool_prepare.pyを正規PYTHONPATHで一回だけ実行する。既directory/slot/OUTがある現在環境では再発行せず、元begin/process/terminal/manifestを照合する。downloadは公開HTTPS一回（redirectはcurl標準経路）、target/VM/業務networkとは別。archive/checksum不一致・取得失敗・未知状態は実行/alternate routeへ進めず保全する。

## 当sourceの真正結果

|run（当evidence/provisional配下manifest.json）|結果|SHA256|
|---|---|---|
|PG8162-promtool-prepare-v1|公式tool-only取得/実version0、ProductPT0|ca3c93186503b91ff14183b1759b7c8b1e0e33fc73d16685974a8ebd2a01ecae|
|PG8164-promtool-config-pt-v1|PROMTOOL001..006/全6成功、実syntax process5|df069f5ee7e017bfce8187af2d7c3bed2363a86f1483ded51fc55ef3b9e4b7b6|
|PG8165-promtool-config-post-v1|元source/fixtures/実command/終了byte・六改変拒否|f18a6b5f5cada9085afc15a010a38137d99214cbd3b7f6ae0aeb0439c700d122|

001は元version/公式SHA receiptの読取照合だけで再実行0。002 DEBUG/003 STANDARDの各ownedcopyに対し、固定binary check config --syntax-onlyが各exit0。004未知rootfield/005 15sに16s timeout/006同job_name二件は各独立期待exit1を実測し合格（expectednegativeを失敗件数へ混同しない）。当原6F-E-S0、新BUG0・全三工具pyflakes0、own job真正終端。元source/当コピー/tool全hashとcase別原receiptを独立postが照合、unknown結果/skipped/negative→success変更/source替え/network command/scopeinflationの六改変を拒否。単なるbeginや開始発言を成功にしない。

tag3.13.5実装/公式CLIでsyntax-only経路を点検し、当閉集合inputはrule/credential/fileSD/remote参照なし。commandは固定check/config/syntax-onlyと当ownedfileだけ、最小env/30s/close_fds/stdinDEVNULL。SD/query/health/debug/push/TSDB/serverを呼ばず、actualtargetnetwork/VM/DB/daemon/credential操作0。原4222/114/common44・Pythonsemantic8の成功確認再演0。元code/POM/profilebyteは保持し、生成ownedfixtureだけを使用した。

## 未受入・計測

今回は公式版3.13.5の構文/宣言validationのみ。参照secret/rule fileの実検証・全lint/実scrape/HTTPエンドポイント/SDK exporter互換・実mode切替/STD停止/保持総5GB・BOM配備/実owner/全451/CHR/native/QA051はUNRUN-HOLD。syntax-onlyという正規検査範囲を明示し、他範囲のPASSへ代替しない。config dataのJava四counter非適用、0/0の100認定/旧counter合成0。正式1964PT53scope/原190新受入0/工数null/全actualHOLDは不変更。

直近fresh18残82/reset1793382075・開始18、丸め共有差0は専有費や無料を意味しない。usage3e0590c6(10:11:10JST/explicit0・完全性未証明)、実N/T/PMO配賦/工数null、原/v4/v5/旧last27区間null/90再基底化0保持。工具取得1・実schema5process/6ID・独立post六反例と元製造量を分離する。PG8166公開delta scanへ最終path/hash/三format結果を記録し、push後も後続索引で具体的な独立PG/PTへ継続する。元DB/Backup/鍵/stash7/native/Currentbaseline不変更。
