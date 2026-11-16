# 現Protocol raw残作業

33未hit method = 十値classの27method + 六utility constructor。59未hit branchは17method、別に四compiler mapの16instruction。元rawの同source単一execから照合し再実行0。

- WIRE_METADATA_VALUES: Independent fixed constructor inputs; explicit getters/rendering; real typed Map lookup with separately constructed equal keys, null/other type and unequal component keys. Retain original whole constructor/negative fixtures and source pins. No JMS/backend operation.
- PAYLOAD_MODEL_VALUES: Independent SS offsets/lengths/fields and immutable list inputs. Preserve redacted toString. WireMessage pairs share one immutable FixedPayload identity while wrappers are independent. FieldDefinition has separate switch branch gap; value API tests alone cannot qualify entire class.
- UTILITY_AND_BRANCH_RESPONSIBILITIES: Six private utility constructors require SS responsibility review before PG, preserve public API/actual cached-state ownership. Seventeen branch methods retain independent error/boundary expectations. Four javac switch-map code gaps remain explicit; no filter/exclusion or impossible enum injection.

全体BUG3111/YKT2583はOPEN。正式認定/工数率を変更しない。
