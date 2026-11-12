# P00903 manifest原4件＋現Protocol130 通常PT仕様

対象AssetChecksumManifest/MediaIntegrityException、FIL006/007・UI237/243・SS333/343。独立Test ID PT-MED041～044とProtocol既130。SHA256(abc)の固定公知vector ba7816bf...0015ad、手書きsha256sum二space/LF/パスのliteral byte列を使用しproduction parser/encoderでexpectedを生成しない。全59627件/上限59628、path512byte/最大line578byte、69UTF8byteでもString23文字の反例、BOM/CRLF/EOF/短hash/大文字・nonhex/重複/不正UTF8/NFC/relativepath/境界と全hash64位置差、零進捗/部分read1/13/65536/IO、callerchannel不close・immutable input/Mapを確認。

元wholeTest4/全assertions不変更。並行100task/10workersは既timedinvokeAll10で全Future完了又は取消後にget、finallyshutdownNow/await10、資源後条件を保持。freshTestcompile26944終了0。26946 PMDraw5/終了4を保持し、26948でstandaloneTest/明示finitecleanupの文脈非該当5へ厳格対応、抑制追加0/適用0/未分類0/processing0/CS0/format0。Main3のsource/physical/NullAway/compiler/SB/formatは既normal結果と現在bytes同一の限定scopeを再利用。Testとhelper閉包はmemorychannelとJDKのみ、実manifest・asset・file・DB・key・Root/native/actual4アクセスを含めない。

旧whole9(PG24922)のdirectProtocol MediaDescriptorValidator/RelativePathが変わったため、当4＋現wholeProtocol130を同run134で再資格確認する。別ownerの旧Capacity5は再実行/再価格なし。旧9 aggregate100/strictsourcegate1/全sourcefourfalseを元のまま保全し、現全体へ合算しない。全179physical(API3/Protocol176)を保持し、Package/NoCode/標準syntheticfilter/実行Code/CRC/session・独立XML/counterを分ける。新Test定義0、旧execunion/手動除外0。

source固定push後command: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1412_manifest_current_qualifier.py run <fixed-source>`、1415独立post。実source/環境/command/終了code/XML/hash/coverageは元run＋postへ一意join、開始時NOT_RUN。SOURCE_REQUAL .1/.25/.5 cap1を着手前固定、専有実費null。Loader2/heldInspector3のMediaAssetFixtureはLinux native FDへ到達するためwholeHOLDで原/2・終了依存・全451/正式1964-53・元190を増加しない。


実行結果: source 96367b4511b1ebaf87f626cec8337c501a8ec789 / Main 8995f6cb6341c0298613cee3714c0d20f113c0f1。26952 genuine0/全134 FESabort0、[26954独立結果](../018_NK-OPS-001/evidence/PG26954-manifest-current-independent-v1/manifest.json) hashccab8a0eed13843032d9ca9515336d223e3aa3fc9df868213ba27c0c31b0c054。全179physical/CI171/code161/positive165CRC、L3547/M751/C161/B1056未網羅0、oldexecunion/手動除外0。環境/実command/exit/旧Capacity5/旧9 strictgate1の保全・scopeは[26958](../018_NK-OPS-001/evidence/PG26958-manifest134-whole-scope-result-v1/manifest.json)。新定義/実file操作/元190/正式更新0。
