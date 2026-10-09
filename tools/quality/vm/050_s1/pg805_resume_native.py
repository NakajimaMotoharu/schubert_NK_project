"""Fresh runtime preparation once, no service start. Old retirement isn't reissued."""
from pathlib import Path
R=Path(__file__).resolve().parent

def source():
 raw=(R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg805RuntimeResume').replace('pg778','pg805').replace('PG778','PG805').replace('pg805-failed758-tools-v1','pg805-resume-tools-v1').replace('0.1.0-PG750','0.1.0-PG796')
 raw=raw.replace("sys.argv[1]in ('stage','verify','recover')","sys.argv[1]in ('stage','prepare')").replace("        if action=='recover':assert (W/'pg805-verify-v1.exit').read_text()=='0\\n'\n",'')
 raw=raw.replace("'Pg805RuntimeResume '+action","'Pg805RuntimeResume prepare'")
 return raw

if __name__=='__main__':
 import sys
 assert sys.argv[1:]in(['stage'],['prepare'])
 exec(compile(source(),'<805 fixed runtime prepare native>', 'exec'),{'__file__':str(R/'pg805_resume_native.py'),'__name__':'__main__'})
