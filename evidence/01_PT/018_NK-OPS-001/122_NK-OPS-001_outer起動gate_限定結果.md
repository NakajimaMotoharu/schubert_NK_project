# 子outergate限定結果（PG301）

Bootstrap全111PT/新STARTADMIT8PT・RELEASE8PTを含めclean成功、failure/error/skipped0・静的0。API/Web selected各13PT（LOAD5/MAIN4/INPUT4）成功、両SpotBugs0（21:18:14 JST）。105負canary成功。coverageは120のsame-source multi-environment限定結果を参照、全Production source gateではない。

BUG266: credential/DB factoryをnative2FD・自己/独立release/config照合の後へ移した。BUG268: exact内部2FD env名だけ認めalias/任意秘密namespace拒否を維持。BUG269: 独立reviewで先行config file読取を指摘、修正前起票後にFD入場callback内へ移し同immutable Config値を業務へ渡す。全3件/YKT200/202/203は直接限定再試験済・正式全gate待ち、完了日なし。現在permit/fullroot/Ops/schema/実morning/fullrelease BOM/実業務main成功はまだ未達。

native018/019は実API/Web UID・zero5caps/NNP・samePID/proc/Invocation・root2FD/actualrelease/outergate/readycloseを順次限定確認。公開config/permit/roots vector、BOM=false、工具payloadであるためR2/R3/CHR合格0。初回同時A競合、reset-failed inactiveUnitエラー、initial test/compile/coverage check失敗は別非成功履歴としてmanifestへ記録。秘密/raw journal/session/token/DB dumpはGitへ保存しない。
