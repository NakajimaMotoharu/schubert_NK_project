"""BUG999: verify exact local XML first, distinct six-exec host baseline/native union."""
import ast,inspect
from pathlib import Path
import pg969_current_native_counter as previous
R=Path(__file__).resolve().parent
def code(hashes,before,after,end):
    raw=previous.code(hashes,before,after,end)
    changes=(
        ('pg969-current-eight-native-v1','pg972-current-eight-native-v2'),('PG969-current-eight-native-v1','PG972-current-eight-native-v2'),
    )
    for a,b in changes:assert raw.count(a)==1,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
if __name__=='__main__':
    raw=inspect.getsource(previous.main).replace("str(R/'pg969_current_native_counter.py')","str(R/'pg972_current_native_v2.py')")
    env=dict(previous.__dict__);env.update(code=code,R=R);exec(compile(raw,'<972 local XML and aggregate separated>','exec'),env);env['main']()
