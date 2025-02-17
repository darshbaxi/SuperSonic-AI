import requests
import urllib.parse

BASE_URL = 'https://defai.onrender.com'  # Change to your server's URL

# GET / - Server status
def get_server_status():
    try:
        response = requests.get(f'{BASE_URL}/')
        response.raise_for_status()  # Raise an error for bad responses
        status = response.json()
        print('Server status:', status)
    except requests.exceptions.RequestException as e:
        print('Error fetching server status:', e)

# GET /agents - List available agents
def get_agents():
    try:
        response = requests.get(f'{BASE_URL}/agents')
        response.raise_for_status()
        agents = response.json()
        print('Agents:', agents)
    except requests.exceptions.RequestException as e:
        print('Error fetching agents:', e)

# POST /agents/{name}/load - Load a specific agent
def load_agent(name):
    try:
        # URL-encode the agent name
        encoded_name = urllib.parse.quote(name)
        response = requests.post(f'{BASE_URL}/agents/{encoded_name}/load')
        response.raise_for_status()
        result = response.json()
        print(f'Agent "{name}" loaded:', result)
    except requests.exceptions.RequestException as e:
        print(f'Error loading agent "{name}":', e)

# GET /connections - List available connections
def get_connections():
    try:
        response = requests.get(f'{BASE_URL}/connections')
        response.raise_for_status()
        connections = response.json()
        print('Connections:', connections)
    except requests.exceptions.RequestException as e:
        print('Error fetching connections:', e)

# GET /connections/{name}/actions - List actions for a specific connection
def get_connection_actions(name):
    try:
        encoded_name = urllib.parse.quote(name)
        response = requests.get(f'{BASE_URL}/connections/{encoded_name}/actions')
        response.raise_for_status()
        actions = response.json()
        print(f'Actions for connection "{name}":', actions)
    except requests.exceptions.RequestException as e:
        print(f'Error fetching actions for connection "{name}":', e)

# Example usage:
def main():
    get_server_status()
    get_agents()
    load_agent('starter')        # Replace 'exampleAgent' with a valid agent name
    get_connections()
    get_connection_actions('groq')  # Replace 'exampleConn' with a valid connection name

if __name__ == '__main__':
    main()
