"""Immutable815 stage and once retire only, no normal start/stop/revoke."""
import ast
from pathlib import Path
from pg805_resume_native import source as previous
R=Path(__file__).resolve().parent
def source():
 raw=previous().replace('Pg805RuntimeResume','Pg815RuntimeRetirement').replace('pg805','pg815').replace('PG805','PG815').replace('pg815-resume-tools-v1','pg815-retirement-tools-v1').replace("('stage','prepare')","('stage','retire')").replace('Pg815RuntimeRetirement prepare','Pg815RuntimeRetirement retire')
 ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<815 exact native transport>','exec'),{'__file__':str(R/'pg815_retirement_native.py'),'__name__':'__main__'})
