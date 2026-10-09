"""Second93cb independent all24/all32/signature/resources seal; no stop replay."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
 raw=(R/'pg878_terminal_final.py').read_text().replace('pg877','pg887').replace('Pg877','Pg887').replace('PG877','PG887').replace('pg875','pg885').replace('pg878','pg890').replace('PG878','PG890')
 ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<890 new93cb independent final>','exec'),{'__file__':str(R/'pg890_terminal_final.py'),'__name__':'__main__'})
