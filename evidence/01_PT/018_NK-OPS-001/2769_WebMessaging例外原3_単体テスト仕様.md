# Web Messaging固定例外・原whole3仕様

2026-10-30、source6b53/normal14216、WBS-F03、着手見積.5/2/4pp固定。関連NK-WEB-001/NK-MSG-001/NK-SCN-001、UI232/234/235、SS311/321/352、BUG1482/1483・元1191/PT-F03-EXC008～010。

対象は元web.messaging.ExceptionValueContractTestの全3method、JmsRequestReplyException/ProtectedReadWireException/ScenarioWireExceptionの全bodyとenum/initializerを読了。固定enum/安全literal message/合成cause同一性/constructor null invariantだけで、実JMS/DB/鍵/graph探索/HTTP/VM/サービス/ファイル0。nullは明示constructor guardのfail-fastをassertし、NPEをcatchして正常業務扱いする実装ではない。

EXC008は三例外の全enum、入力Reasonと安全literal文言とcause有無・同一性、Protected/Scenario null拒否。EXC009/010はJmsのcause無/有constructorでnull Reasonを即拒否。期待値は入力enum/literal/合成causeidentityを独立使用しproduction methodでexpected生成しない。mutable state/資源/再送・競合はこの値対象に非該当、実交換の合格へ転用しない。

PG14786は原whole3を一回だけ、JDK25/元6module Jar/新launcher/reporter、source/Jar/Test固定で新onlySLOTに実行する。全XML3/1、F/E/S/flaky/not-run0、原環境/command/exit/hashを収録。14788は一exec/CRC/Source三件・全六physicalの四counterを資格済みshared postv2で解析。既JmsRequestReplyException資格は保持し今回の新Sourceへ二重計上せず、旧execと合成しない。後続2770に結果/証跡hash、全不足を残す。

command `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14786_web_messaging_exception_three_pt.py`、続いて14788のpost。業務Main/Test変更0、外部状態UNOBSERVED_HOLD、正式1964/53・歴史17/190・工数null・QA051final・全HOLDは不変。
