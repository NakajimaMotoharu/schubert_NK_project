# Scenario Entry COPY rowの12列検証：独立12仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT004005/DAT004/FUN004、UI223/242§4.4/254、SS331§2/V002・SS343§10。既COPY encoderは列別の型/nullable/byte/NFC制約を扱わないため、ScenarioEntryCopyRowを新規製造。実Current抽出/ID-map連結/全件数/game-FK/DB/transaction/driver/pg_temp/COPYは別未受入、外部hostはaru新規利用禁止・haruka構築/個別条件未確認HOLDを維持する。

Inputはnullable Stringを要素に持つnonnull Listで、既V002の非generated 12列順を固定: id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at。body_searchはgeneratedなので含めない。列数12以外拒否、mandatory9列はnull拒否、optionalはline/speaker/labelだけ。Listをprivate copy＋変更不能wrapperで保持、返却fields/columnNames変更不可、copyBytesは既encoderへ渡すだけでbyte別所有。固定redaction・安全例外/cause無し、元文字列を修正/trim/暗黙再採番しない。

Target id/file/order及びnonnull speakerはcanonical positive N12 decimal、gameは1/2。entryIndexはcanonical0..IntegerMAX、nonnull lineNumberは1..IntegerMAX。内部送信のcanonical表現なのでleadingzero/sign/空白/小数を受け付けず、外部ID仕様は変更しない。typeはdialogue/narrationだけ、dialogueはspeaker必須、narrationはspeaker null。

Bodyはnonnull NFC/validUTF8かつ1..4096byte、nullable labelはNFC/validUTF8・0..128byte、rawBlockはnonnull NFC/validUTF8で当DDLにないbyte上限を加えない。column別control検査はlabelをinline（ISO control不可）、body/rawBlockをmultiline（TAB/LF/CRだけ可、それ以外のISO control不可）として、Currentの改行を含むbody表示とCOPY escapingを保つ。NUL/孤立surrogateは拒否、非NFCを黙って変換しない。原本内容を読まず、実移行data適合性を推定しない。

created_atはcallerがtransaction内で共通採取したInstantのcanonical UTC文字列を入力（toStringと完全一致）。年0001..9999・µs精度、parse不能/非canonical offset又は余剰fractionは安全拒否。row同士の共通Instant・実DB型/FK/全件数はこの値クラスの受入ではない。

PT-MIG-ROW001..012:
001 手書き12列/完全COPY bytes、column orderからgenerated body_search除外、dialogue speaker有/NFCラベル/本文改行を固定。
002 narration speaker nullとline/label null、空label/rawBlock許容、nullと空のCOPY区別。
003 N12/ゲームの下上境界、各列0/負/N12超/leadingzero/sign/空白/小数/未知game拒否。
004 index0/IntegerMAX・line1/MAX、負/MAX+1・line0/空拒否。
005 type null/未知/Dialogue大小違い、dialogue speaker null/narration speaker有の個別拒否。
006 Body ASCII4096/4097、あ1365+ASCII1=4096/あ1366=4098、label128/129・multi byte上端、rawBlock4097以上も切捨てない。
007 nonNFC/孤立surrogate/NUL・ISOcontrolの全field別拒否、body/raw TAB/LF/CR許容・inline labelでは拒否。UTF16 fixtureはchar配列から作り既PMD defectを再現しない。
008 mandatory全9列null・optionalとcolumns数11/13/nullouter、固定安全例外でraw値非露出。
009 時刻year0001/9999・µs、年0/10000・ns/offset/非canonicalfraction/不正値拒否。
010 入力変更/返却List/columnNames/byteの所有分離。
011 文字列trim非実施・安全toString、encoder null拒否・失敗後次の独立値に影響なし。
012 所有8worker64task、Future各5秒/finallyshutdownNow-await10assert、全expectedは固定列/ASCII/UTF8 hex・独立byte算術、Production methodでexpected生成しない。

新Row1＋支援Copy1の全2physical/同source・通常static・全Row12/Copy12の24を単一execで必要変更群の全closure品質として初実行、newdefinitionsはRow12のみ（既Copy12の新定義加算0）。旧exec合算/除外/抑制0、実JVMCodeと既定counterを独立postで確認。旧Current/実DB/RootVM/native/全451/CHR/ITSTを代用しない。

追加不足1/3/6: 詳細.1/.3/.6＋製造whole12定義.5/1.5/3を一群.6/1.8/3.6cap4、normal必要24 .4/1.2/2.4cap4。元費用/群開始見積り/SV上限を保持、専有実費/token null。
