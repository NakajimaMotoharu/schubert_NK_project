"""Reevaluate complete Root oracle plus actual Browser chain without rewriting any snapshot."""
import inspect
import pg3592_current_browser_composite_seal as previous
import pg3808_hygiene_acceptance as root
import pg3814_hygiene_browser_actual as actual
from pg3798_hygiene_current_observer import SOURCE,BOM

SLOT='pg3816-hygiene-browser-composite-full-seal-v1'


def namespace():
    values={**previous.__dict__,'SOURCE':SOURCE,'BOM':BOM,'root':root,'actual':actual,'SLOT':SLOT}
    for function in [previous.compose,previous.payload]:exec(compile(inspect.getsource(function),'<newsource immutable-chain composite>','exec'),values)
    return values


def compose(raw,chain,sha):return namespace()['compose'](raw,chain,sha)


def payload(binding):return namespace()['payload'](binding)


def main():
    module=root.old_seal;raw=inspect.getsource(module.entry)
    for a,b in [('pg2686-operation-current-live-binding-v1',root.LIVE),('pg2682-parent-watch-v1','pg3798-parent-watch-v1'),('pg2702-operation-current-rows-v1',root.ROWS),('pg2700-operation-current-terminal-v1',root.TERM)]:raw=raw.replace(a,b)
    values={**module.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'TERM':root.TERM,'payload':payload}
    exec(compile(raw,'<current independent Root plus Browser composite capture>','exec'),values);return values['entry']()()


if __name__=='__main__':raise SystemExit(main())
