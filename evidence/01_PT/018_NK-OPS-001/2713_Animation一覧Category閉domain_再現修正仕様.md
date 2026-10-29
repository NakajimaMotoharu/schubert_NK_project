# 2713 BUG2103 Animation一覧Category閉domain 再現・修正仕様

現行訂正: 本書の「一覧enumにOPENINGがある」という前提は2714/BUG2104の実型・byte照合で否定された。14584はcompiler1で製品JVM前停止、BUG2103はNON_APPLICABLE、予定Main/Test修正は実施しない。以下の初期計画は履歴として保全し、再実行しない。型を回避するfixtureは作らない。

source6b53/dev-foundation/保存0ad0c536153d81289c0fe47a4911ac32e082fdaa。BUG2103/YKT1850は修正前起票済み、PG-D921。origin/main UI235 §5.3のANLRSP01 Category=MAIN/SUBTRACK/OVA、§6 IF012はOPENING可という独立許容表、SS313 SCR009/010、FUN006/UI223/SS323を根拠とする。既正常表示/順序/電文は変更しない。

PG14584は既normal14216/同Source全input・六Jarで自己DTOの五controlを検査する。MAIN-MAIN/OVA-OVA/MAIN-(MAIN+SUBTRACK)は受入、MAIN-OPENING/OVA-OPENINGは拒否を期待。MAIN-OPENINGを受け入れる構造を実測で確認するまで修正しない。javac-proc:none/Werror→own新JVM60秒で固定合成DTOのみ、実wire送信/HTTP/DB/JMS/Browser/VM/Root/graph/cohort/鍵0。公開値は五booleanと原OS/JDK prefixだけ、原session/keyなし。実exit1ならBUG再現として保全しPASS/coverage/正式へ加算しない。source/Main/Testは再現前不変更。

再現後は一覧factoryの要求categoryに対する正の閉集合を明記し、既原AnimationViewModelTest全8へ独立OPENING拒否vectorを追加する。正常三categoryの動作、IF012 watchのOPENING許可は保持。UI/SSの承認済みdomainを実装都合で広げない。正常の必要build/NullAway/全byte差分/静的解析・原8+追加境界・独立counter/期待/環境を新固定sourceで確認する。6b53の既696を新sourceへ転用せず、歴史証拠と新当sourceの限定測定を分離する。

YKTはWeb一覧/Watch/Controller・Protocol schema/record/validator・API queryのcategory束縛を読み、各対象の是正又は非該当根拠を記録する。語句検索だけで完了にしない。設計不整合ならSSC併用、上位許容値が明確な内部guard修正は追加QAなし。新再発防止は意味ある業務境界であり、単にcoverageを上げる呼出しではない。群見積1/4/8pp cap10（event3103に固定）、再現結果2714・後続source/run/checkpointへ。元計画/手戻り/資格再認証を分ける。
