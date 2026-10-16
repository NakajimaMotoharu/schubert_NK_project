"""Observe refused declaration fields without interpreting differences as valid or authorizing action."""
import inspect
import pg4210_quiescent_current_read as previous
from pg4060_original_profile_dual_stack import once

SLOT='pg4212-quiescent-configuration-observation-v1'


def payload():
    raw=previous.payload().replace(previous.SLOT,SLOT)
    raw=once(raw,"  require(CONFIG_CONTRACT['same'](old['configuration'][name],item,exec_record));value[name]=item","  value[name]=item")
    raw=once(raw,"configurations=config();require(set(configurations)==set(old['configuration'])and all(CONFIG_CONTRACT['same'](old['configuration'][u],v,exec_record)for u,v in configurations.items()))",
             "configurations=config();require(set(configurations)==set(old['configuration']))")
    raw=once(raw,"'all32DeclarationsSame':True","'declarationAccepted':False,'configurationChangedFields':{u:[k for k,v in a.items()if v!=old['configuration'][u][k]]for u,a in configurations.items()if a!=old['configuration'][u]},'declarationComparator':{u:CONFIG_CONTRACT['same'](old['configuration'][u],a,exec_record)for u,a in configurations.items()}")
    return raw


def main():
    ns={**vars(previous),'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<observation only>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
