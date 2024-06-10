"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        h5 = self.addHost( 'h5', ip='10.0.0.5/24', mac='00:00:00:00:00:05' )
        h6 = self.addHost( 'h6', ip='10.0.0.6/24', mac='00:00:00:00:00:06' )
        h7 = self.addHost( 'h7', ip='10.0.0.7/24', mac='00:00:00:00:00:07' )
        h8 = self.addHost( 'h8', ip='10.0.0.8/24', mac='00:00:00:00:00:08' )
        s2 = self.addSwitch( 's2' )

        # Add links
        self.addLink( h5, s2 )
        self.addLink( h6, s2 )
        self.addLink( h7, s2 )
        self.addLink( h8, s2 )


topos = { 'mytopo': ( lambda: MyTopo() ) }