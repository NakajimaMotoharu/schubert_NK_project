# flock五commandの同PID方式 source是正

BUG2468/YKT2206・SS341§5.1/SS343/411451。前群は親六のargvを保持して終了済み。今回の別群で、Test内部fixtureの明示判断としてflock五argvへ--no-forkを一つずつ追加する。元見積・旧argv・元runは不変保存し、以前の「argv保持」成果を書換えない。対象はExecDescriptors competitor/after二、FileLock child/external二、StartupFileLock external一。Product Main/設定/画面/電文/Currentbaseline/本番実行commandは変更しない。

正本origin/main SS341は実util-linux flockとの相互排他を要求し、Test用コマンドargvのfork方式を固定していない。これはSSより詳細なTest実装判断であり、上位仕様/独立期待値の変更ではないためQA/SSC不要。独立oracleの競合exit20/成功0、lockcallback結果、READYとstdin、FD/PIDの既assertionは保持。単に親Process待ちを増やしてcommand終了を推測しない。

installed util-linux primary manの--no-forkはflockがcommandへexec置換してlockを保持すると定義。--closeとの併用不可をsource否定する。元/bin/true四・/bin/sh既builtinスクリプト一は変更しない。flock自身が作るcommand子を除去して同じProcess ownerがcommand PIDを保持する設計とする。command自体のdescendant/host・guest binary適合/実kernel後条件は未測定で、静的証拠から退出を認定しない。

元native/process/FS/VM/DB/Root等実操作・元Testcompile/run/代替fixture実行0。許可されたown parse-only/format/PMD-CS（既同byteOwnedTestProcess static binary/JDK25jrt補助）と、五argvだけの逆token復元/flag欠落・--close等のsource否定を実施。実PT PASS/covはnull、全HOLD維持。変更三classの必要静的のみ、元全29再実行なし。

追加発見の製造source是正、見積低0.5/標準2/高5pp、cap7。新unique/whole/leaf0、442/whole94/正式1964-53/工数null。
