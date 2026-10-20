"""Recheck five changed-source Throwable guards; no new PT/native or historical PASS import."""
import inspect
import types
import pg5872_terminal_identity8_review as previous
from pg5886_terminal_serial_whole import SOURCE

OLD_SOURCE='0f572da66c9e3f0818cddb5bf679e7b8bc0f47da'


def prior_index_function():
    return types.FunctionType(previous.prior_index.__code__,{**vars(previous),'OLD':OLD_SOURCE},'serial_prior_source_index')


def reader_source():
    raw=inspect.getsource(previous.main)
    changes={'PG5868-terminal-dispositions-v1':'PG5894-serial-dispositions-v1','58408654af3af57edc4d8e961ecf7b14dde788dccc63e37419a9b6df300a1d90':'d631c0612dc0da64e381820e5f9b2080bf4ea8544c85b917e8a129a33a82c419','PG5846-current-static3967-v3':'PG5876-current-static3971-v1','f42681dbfd498db8a13b9374d0d2c94c9cddc149fea8f83597ce0d90b0491a9d':'3c90000fad14ffdc5ab032596bfcf6f85ecef199c987b10967228ea133bff06f','pg5870-terminal-reference-facts-v1':'pg5896-serial-reference-facts-v1','666f75579d550f7b5ec9cd69600dffe5d7cdf1e8d29ac68a9c70ae6b8445b45e':'aade9992f685e6c0ec0fa25b753e3a8d5bcfab57ea019070fd86ccee4e61b2fb','pg5858-terminal-static-v1':'pg5882-terminal-serial-static-v1','len(held)!=8 or used!=held or len(decisions)!=8':'len(held)!=5 or used!=held or len(decisions)!=5','all and only eight changed prior guards':'all and only five changed prior guards','PG5872-terminal-identity8-v1':'PG5898-serial-identity5-v1',"-=8":"-=5","+=8":"+=5","'recheckedChangedPrior':8":"'recheckedChangedPrior':5",'PG-D444;':'PG-D445;'}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one current five-guard source/fact binding: '+old)
        raw=raw.replace(old,new,1)
    compile(raw,'<five current Throwable guards>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'OLD':OLD_SOURCE,'prior_index':prior_index_function()}
    exec(compile(reader_source(),'<five current Throwable guards>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
