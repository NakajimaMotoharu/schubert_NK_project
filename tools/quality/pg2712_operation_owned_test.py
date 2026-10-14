"""Source-construction fixtures only; no old owner/permit result is accepted."""
import ast
import json
import unittest
from unittest.mock import patch
import pg1257_fresh_independent_terminal_post as schema
from pg1446_current_cold_stage import W
import pg2708_operation_owned_sources as sources
import pg2712_operation_owned_dispatch as dispatch
import pg2716_operation_owned_post as post


class NewOwnedPreparation(unittest.TestCase):
    def fixture(self):
        actual=json.loads((W/'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        live={**actual,'binding':{**actual['binding'],'run':'00000000-0000-0000-0000-000000000001','activation':'00000000-0000-0000-0000-000000000002'}}
        seal=json.loads((W/'pg2548-strict-current-full-seal-v1/manifest.safe.json').read_bytes())
        terminal=json.loads((W/'pg2544-strict-current-terminal-v1/manifest.safe.json').read_bytes())
        projection=json.loads((W/'pg2552-strict-current-parent-projection-v1.safe.json').read_bytes())
        ctx=('b'*64,seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc'])
        return live,ctx,terminal['parentState'],projection['parentState18']

    def test_whole_graph_new_source_paths_and_terminal_classifier(self):
        live,ctx,state,fields=self.fixture();values=sources.emit(ctx,live,state,fields,'a'*64)
        whole='\n'.join(values.values())
        for value in [sources.SOURCE,sources.TOOLS,'pg2704-operation-current-full-seal-v1','PG2654',live['binding']['run']]:self.assertIn(value,whole)
        self.assertNotIn('pg2554-strict-current-owned-stop-tools-v1',whole)
        for name,raw in values.items():
            if name.endswith('.py'):ast.parse(raw)

    def test_new_only_stage_dispatch_and_all_resource_independent_post(self):
        with patch.object(dispatch,'candidate_bom',return_value='a'*64):stage=dispatch.stage()
        run=dispatch.run_source();ast.parse(run)
        for value in ['pg2710-frozen-v1.safe.json','pg2712-stage-v1.exit','Pg2708','pg2713','pg2714']:self.assertIn(value,run)
        for value in ['pg2712-'+sources.TOOLS+'.tar','PG2654']:self.assertIn(value,stage)
        live,ctx,_,_=self.fixture();raw=post.emit({n:'a'*64 for n in schema.previous.SEALS},ctx,live,'a'*64);ast.parse(raw)
        for value in [sources.SOURCE,'PG2654',sources.TOOLS,'pg2704-operation-current-full-seal-v1',post.SLOT,'allTenUnitsKernelEmpty','allClientAdvisoryFlock0']:self.assertIn(value,raw)
        with self.assertRaises(ValueError):post.emit({},ctx,live,'a'*64)


if __name__=='__main__':unittest.main()
