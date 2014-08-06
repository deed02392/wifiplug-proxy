Wifi Plug Commander
-------------------

These scripts enable you to control your wifi plug without depending on an internet connection.

By setting up IP tables to redirect the wifi plugs through this server script, you can make both the plug and the wifi plug servers think that they are connected directly, when in fact you are able to control the state of the plugs locally.

Because this solution is bi-directional, the original apps and web interfaces will continue to work flawlessly, updating themselves with the correct state.

Files
-----

* `wifiplug_sim.py` - this script allows you to simulate a Wifiplug so you can develop these scripts without switching an original plug on and off a lot (which is not something you particularly want to do regularly).
* `wifiplug.py` - a class defining the communication protocol messages and codec methods for the protocol that the wifi plug and servers use.
* `server.py` - simulates a wifi plug server
* `proxy.py` - the main script, redirecting data between the wifi plug and server and providing an administrative panel for you to configure plug states locally

Usage
-----
Implement iptables rules similar to as follows, which has the plug at 120 and the managing device at 143 (with the common gateway as 192.168.1.1):

```iptables
# wifiplug
iptables -t nat -A PREROUTING -i br0 -s \! 192.168.1.143 -p tcp --dport 221 -j DNAT --to 192.168.1.143:221
iptables -t nat -A POSTROUTING -o br0 -s 192.168.1.120 -d 192.168.1.143 -p tcp --dport 221 -j SNAT --to 192.168.1.1
iptables -A FORWARD -s 192.168.1.120 -d 192.168.1.143 -i br0 -o br0 -p tcp --dport 221 -j ACCEPT
```


Start the main proxy script
Make HTTP GET requests to the admin port depending on what state you want to change the plug to