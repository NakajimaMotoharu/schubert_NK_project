"""Exact74 source-owner sites and independent actual-shape regression; no product execution."""
import pg11370_source_constructor_owner_audit as stage
stage.PRIMARY_SHA='2439413972f4aab4204fb2267631528fa72276182cc973075383226caf1c3b8a'


def guard_shape(body):
    if 'finally{standard.close();}' in body:
        return 'FINALLY'
    if 'try(varstandard=newFixedOwner())' in body:
        return 'TWR'
    return 'UNPROVEN'


if __name__=='__main__':
    # Number labels are deliberately irrelevant; the actual guard syntax decides.
    assert guard_shape('full001varstandard=newFixedOwner();try{}finally{standard.close();}')=='FINALLY'
    assert guard_shape('full002try(varstandard=newFixedOwner()){bind();}')=='TWR'
    assert guard_shape('full012try(varstandard=newFixedOwner()){bind();}')=='TWR'
    assert guard_shape('full001varstandard=newFixedOwner();bind();standard.close();')=='UNPROVEN'
    stage.post()
