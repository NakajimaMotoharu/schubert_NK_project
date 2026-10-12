# 694 WARNING保全pair・livepeer限定回収 単体テスト仕様

NK-OPS-001、SS343/353/SSC279・既SSC265275・QA047、BUG1165～1168/YKT933～936。対象1777/1780/1782 readonlyproof、1784 oncehandOff。停止処理・Root業務再演は本試験対象外、旧UNKNOWN正常化禁止。

| Test ID | fixture/input・操作 | 独立期待値 |
|---|---|---|
| REC-1777-ARGV | 実emitted Java/子argv・typed101/4FD/allchildren・全global static | Java476087/t8492401、子476116/t8492565、親class/子sourceは1773全frozenhash、旧99FD/coldbinding無し |
| REC-1780-PEERS | literal app2/web1/batch1、null/bool/unknownrole/不足余剰/port0・65536/foreignDB/address/管理app・state/重複PID | 正規4peerだけ、唯一batch476114/PG998-native-stop/advisory1。全client/serverTCP inodeはAPI451130/Web452144/retained476087へ対応 |
| REC-1782-ENTRY | isolatedtemp/mock SSHでactualmain/旧1766slot存在/成功・失敗・既slot | 新固定slot一回SSHだけ、旧dir不変更、失敗stdoutを成功JSONにしない。fixture結果をactualVM成功へ加算0 |
| REC-1784-GATE | actualmain中のrealtemp FLOCK/別actor競合/既slot再発行/忙しいgate | SSH前にhostgate取得、接続中別actor拒否、最後正常release。旧1774hostgate無しは別実観測として保持 |
| REC-1784-PHASE | 実emitted AST/source、子→reap→親、全FD差の限定、各pidfd/耐久一回予約/普通TERM | 同fresh proof/元全値、子先TERM後の親FD変化は当子stdin/stdout pipeの通常closeだけ。未知close/newFD/別PID/ticks/errnoは拒否。SIGKILL/DBterminate/reset-failed禁止 |
| REC-1784-ACTUAL | 新metadata十Ref/wholeproof/現samepeer/OFD/一回guard→子→親→全後条件 | 管理peer/advisory/M-A0、普通daemon4及びDBpeer3保持、全24/32/187/原本Backup/native不変、新Ref/bus正常帰還。oldcloseはUNKNOWNのまま |

独立whole原値は1770/b8ce seal、fresh pair proofは1782/4c226a4e958291f100b1b20e05ff854dda3e511e1cdc58d16cb11bfb85834a6d。before期待をactual afterから生成せず、before全row・Source・file/FD/OFD/socket・元診断capture_data58と1回予約無しから計算する。raw値はguest root0600だけ、公開はcounts/hash/非秘密PID/generation・phase。

実行=固定PYTHONPATH＋pyflakes3.4.0でunittest1777/1780/1782/1784、1782一回readonlyprobe→sourceをcommit固定→1784新slot一回、最後別fullpost。環境=Ubuntu26.04.1/x86-64/Java25.0.4/PG18.6/Python3.14、Main2741/PG1638/BOM195e/boot3d69。formal/coverage100/旧UNKNOWNは更新しない、未実行/片側/失敗を合格へ加算しない。command/終了code/対象operatorcommit/hash・利用枠は695とmanifestへ記録する。
