# kserver_local.conf
#
# Configuration file for KServer in local use
{
    # Run KServer as a daemon
    # Set to ON by default, OFF mainly for development
    "daemon": "ON",
    
    "verbose": "OFF",
    
    # Enable/Disable the Nagle algorithm in the TCP buffer
    "tcp_nodelay": "ON",
    
    "logs": {
      # Send KServer messages to the syslog daemon
      "system_log": "ON"
    },

    # -- Servers
    # Set "worker_connections" to 0 to desactivate a given server
    
    "TCP": {
        "listen": 36000,
        "worker_connections": 10
    },

    "websocket": {
        "listen": 8080,
        "worker_connections": 10
    },
    
    "unix": {
        "path": "/tmp/kserver_local.sock",
        "worker_connections": 10
    }
    
    # -- Memory mapping
    # Allowed memory region for DevMem
    # Addresses must be a string in hexadecimal (ex. "0xFF1100")
    # Set both to "0" to desactivate memory mapping limitations
    "addr_limits": {
        "down": "0x0",
        "up": "0x0"
    }   
}
