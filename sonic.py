from src.server.client import ZerePyClient
from src.connections.sonic_connection import SonicConnection
client = ZerePyClient("http://localhost:8000")

agents = client.list_agents()

client.load_agent("starter")

connections = client.list_connections()

coe = SonicConnection(config={"network":"testnet"})
SonicConnection.configure(coe,"57900ba87eb8ec45870c3094bb9d32ed2f6191d094cd46bec67b147e34fabe70")

print(client.perform_action(
    connection="sonic",
    action="get-balance"
))

