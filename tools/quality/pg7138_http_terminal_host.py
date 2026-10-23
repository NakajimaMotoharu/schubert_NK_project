"""Corrected owner-failure contract and added Timer/fatal vectors, exact actual23 only."""
import pg7130_http_terminal_host as stage


if __name__=='__main__':
    stage.COMPILE=stage.host.W/'pg7136-http-terminal-six-compile-v3'
    stage.SLOT=stage.host.W/'pg7138-http-terminal-host-v2'
    stage.OUT=stage.host.BASE/'PG7138-http-terminal-host-v2'
    stage.SESSION_ID='PG7138-HTTP-TERMINAL'
    stage.main()
