# 282 通常resumeの実Backup再検証（PG387、暫定）

仕様281、NK-OPS/BAT、OPS009/BAK、UI251/253、SS341/343、SSC116/BUG350/YKT280。Source `7ba352d6f0b7c08c371e838683fb6c2ba58725af`、dev-foundation。選択91 PT/静的2module0、全6同source 2551PT/372suite F/E/S0・静的0、14:14:29 JST、13:06。全4coverageと正式53scopeは未認定。

`PT-OPS-BRESUME-VM001`：署名/pinned full hostRO BOM177/61/23のreleasePG387を新規配備し、元run/cutoffを保持した真正外部Morning --resumeを実行。親Invocation2144cbd6195e47cd8d2833576e704372、実Backup検証子01cd3703bf834fcfa27dbf1287e8f9ae、PID1のfresh start/stop doneを独立取得した。新dump/part/credential archiveは作らず、保持した元dumpのsize/hash/inode確認と実pg_restore --listのみを実行。

元4fileのbyte hash/size/dev/ino/owner/mode/nlink/mtime/ctime、元DB行9/10・attempt5の全列、および全Backup directory一覧はbefore/afterの独立byte比較で**完全不変**。元bundleは280の独立hash/固定7config/固定16credential private復号/restore-list224で検証済みの同一成果である。今回は行11/12・attempt6をSKIPPED/ALREADY_SUCCESSFUL/件数byte全0、ended=startedとして保存し、新transactionで独立再読した。request/intent退役、両PID0/全終端、permit0。systemd既定LoadCredentialは維持し、applicationのpgpass読取/コピーとarchive生成は0；secretコピー全般0と誤記しない。

Morning最終30はS2/S3未接続の部分非成功。通常SKIPの保存だけから合格を推定せず、同source実Mainの再検証完了・退役とfresh真正子を併せて確認した。UNKNOWN/実30分・Cleanup/Transfer/Expiry/issuer/APIWeb/CHRは別未完。

証跡 `evidence/provisional/PG387-native-normal-resume/manifest.json` hash `e34d282aa7c345bca237c7cb1bbf7c509c85a3fc6f52c66ed8f0533e62b59bc7`。コマンド/実日時/環境/expected/actual/BUG/SSC/hash、before/after原本成果metadata+DB、今回SKIP、PID1限定receipt・正規退役・真正execを含む。raw journal/秘密key/password/token/session/dumpはGit外。

全6manifest `evidence/provisional/PG387-known-backup-failure/manifest.json` hash `85b81fcaa79c49453a7bbdde8e7311cf84d99b31fb4d854db5ce3cdd3666f800`（継承collectorのdirectory名であり、inputは通常resume変更群）。Host未網羅B/L/M/Cは合計324/1195/263/25、PG386からgraph差分+36/+85/+9/+2。Batch host283/1125/250/25、同byte host+今回通常resume実parent/worker union261/777/148/13、不一致0、今回hostから22/348/102/12解消。PG386の生成正負とPG387の通常再検証は経路・sourceが異なり、旧execを加算して全100%を装わない。生成正負/S2/timeoutも最終同sourceで採取する。

BUG350の主経路修正・独立host/実normal resumeは確認済み、YKT280のStep/Log/Inbox/Expiry/issuer横展開は未完。未網羅も残るため障害表は「修正済・追加網羅中」、正式完了にしない。
