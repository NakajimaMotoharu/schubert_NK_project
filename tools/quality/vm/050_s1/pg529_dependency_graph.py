"""BUG825/YKT594: systemd dependency attributes are sets, NOT display/argv/wire order."""
import re
GRAPH_FIELDS=frozenset(('Requires','Before','After','PartOf','BindsTo'))
def dependency_graph(value,units):
 if type(units)not in(list,tuple)or len(units)!=10 or any(type(u)is not str or re.fullmatch(r'[A-Za-z0-9_.@-]+\.service',u)is None for u in units)or len(set(units))!=10:raise ValueError('fixed ten Unit graph required')
 if type(value)is not dict or set(value)!=set(units):raise ValueError('fixed ten Unit graph required')
 result={}
 for unit,properties in value.items():
  if type(properties)is not dict or set(properties)!=GRAPH_FIELDS:raise ValueError('fixed dependency attributes required')
  normalized={}
  for key,raw in properties.items():
   if type(raw)is not str or len(raw)>8192:raise ValueError('fixed dependency values required')
   tokens=[]if raw==''else raw.split(' ')
   if len(tokens)>128 or len(set(tokens))!=len(tokens)or any(re.fullmatch(r'[A-Za-z0-9_.@-]+',t)is None or len(t)>255 for t in tokens):raise ValueError('fixed dependency values required')
   normalized[key]=sorted(tokens)
  result[unit]=normalized
 return result
