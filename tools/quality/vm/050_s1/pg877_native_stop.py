"""New-only stage/ownedstop. New genuine875/A01 proof required, never start/revoke."""
import ast
from pathlib import Path
import sys
from pg847_native_stop import source as prior
R=Path(__file__).resolve().parent
def source():
 raw=prior().replace('Pg847','Pg877').replace('PG847','PG877').replace('pg847','pg877').replace('PG832','PG862').replace('pg832','pg862')
 raw=raw.replace('Immutable stage; distinct once-only failed143 verify/recover. Unknown stays attached.','Immutable new genuine1902 stage/ownedstop only; unknown stays attached.')
 raw=raw.replace('pg846-completed-readonly-v1','pg875-completed-readonly-v1').replace('pg849-chr-a01-native-v1','pg876-chr-a01-native-v1')
 marker="proof=json.loads((W/'pg875-completed-readonly-v1.safe.json').read_text());"
 assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"from pg877_stop_binding import bindings;bindings(proof);")
 ast.parse(raw);return raw
if __name__=='__main__':
 assert sys.argv[1:]in(['stage'],['stop'])
 exec(compile(source(),'<877 genuine new1902 ordered TERM only>','exec'),{'__file__':str(R/'pg877_native_stop.py'),'__name__':'__main__'})
