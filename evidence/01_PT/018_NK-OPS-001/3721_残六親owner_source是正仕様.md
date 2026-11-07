# 残六親owner source是正仕様

BUG2467/YKT2205・SS341343/411451。LinuxExecDescriptors008 competitor/after二、LinuxFileLock.externalFlockInteroperability childとexternal helper二、LinuxStartupFileLock.external helper一、LinuxInodeSecurity.setAcl一。現八owner中残六。source確認済みOwnedTestProcess(a9ab/PG23100)を不変利用し、全start直後TWR/同じ親ProcessのTERM5+force5待機/unknown例外/interrupt保持へ揃える。旧正常argv/環境/期待値/assertion/戻り値を保持し、FileLock main childはinner finallyでreader/writer/executor close前にowner.close、外側TWRの二回目はno-op。元親終端でfork command終端・lock解放を証明しない。

元flock五commandはdefault forkを維持し--no-fork等へ変更しない、setfaclのdescendant不明も未解明。BUG2468/YKT2206は別OPEN、全六をsource是正しても元runtimeの全面解決とはしない。新しいcleanup routeの実PT/時刻/資源後条件は未測定HOLD。

実start/stop/wait/VM/DB/鍵/Root/native/FS等操作0、元Test compile/run0、代替fixture/harness実行0。自作parse-only/format/PMD/CSと独立逆token/所有scope/metadata否定だけ。変更四classを固定、helperの同byte静的13を再利用。元29は不変25+変更4をcomposeし位置/hash/reasonを現在へ再束縛、all29成功engine再演なし。

追加発見の製造source是正群、着手見積低0.5/標準2/高5pp、cap7。新unique/whole/leaf0、442/whole94/正式1964-53/工数null/全HOLD維持。
