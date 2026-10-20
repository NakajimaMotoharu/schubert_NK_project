"""Corrected branch applicability only; read the same original whole, preserve failed reader v1."""
import pg6250_original4034_artifacts as original
from pg6263_branchless_original import proof


def main():
    scope=original.definitions()
    # Use the already fixed4034 definition, not the obsolete original4024 source body.
    function=scope['main']
    import types
    def collect(data,path,slot,remote,public_name):
        data['branchlessOwnerProofs']=proof(data['source'])
        return original.prior.reader.collect(data,path,'pg6250-original4034-artifacts-v2',
            '/home/mini/schubert-nk-pgpt/transfer/PG6250-original4034-v2',public_name,2,
            'BUG1568/pg6250-original4034-artifacts-v1')
    namespace={**function.__globals__,'reader':types.SimpleNamespace(collect=collect,
        production_source_inputs=original.prior.reader.production_source_inputs)}
    return types.FunctionType(function.__code__,namespace)()


if __name__=='__main__':main()
