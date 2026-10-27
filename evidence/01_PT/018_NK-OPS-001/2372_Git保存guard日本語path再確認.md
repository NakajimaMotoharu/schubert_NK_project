# Git保存guard・日本語path再確認

2026-10-28 / BUG1995-YKT1743 / PG-D754の保存段階。PG12712 scan c9b56030dca23b34e515579bd3c83eed355de38bde70c81d7ec1070de95c3be8（13公開text/三pattern0）は不変。旧inline保存はindex stage後・commit前のassertionでexit1、日本語pathがGit quote表示されたことが原因。実indexを後続のNUL読取で照合すると期待14/実14・extra0/missing0。元HEAD/remote0bcd、後続pushのEverything up-to-dateは新保存成功ではない。

修正前台帳起票後、純粋なNUL parserに正例三（空・日本語/改行・複数）、負例四（末尾無し・重複・空項目二種）と余分path不一致一を与え、actual exit0。実index14の保留二工具混入0を確認。新しい保存では既stageを破棄せず最新scanの許可集合へのsubsetを確認し、全hash検査・explicit add・NUL index完全一致・cached check・commitの全段階をcheck=Trueで直列化する。一つでも失敗ならpushへ進まない。

新PG12714公開scanで後追い台帳/本書/最新checkpointを含め、元scanは上書きしない。再試験はmetadataのみ・製品PT/coverage/正式加算0、元開始0.5/2/4cap10や群終了event2732は保持し保存手戻りを別eventへ追記。保存commit/pushの真正結果は次checkpointで照合し、未確認の段階を成功にしない。
