from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json

with open('./mysite/secret_var.json', 'r') as file:
    secret_var = json.load(file)

gitlab_token = secret_var["gitlab_token"]

transport = RequestsHTTPTransport(
    url="https://gitlab.com/api/graphql",
    verify=True,
    retries=3,
    headers={
        "Private-Token": gitlab_token,
        "Content-Type": "application/json"
    }
)

client = Client(transport=transport, fetch_schema_from_transport=True)

username = secret_var["gitlab_username"]

query = gql(f'''
    query Users {{
        users(usernames: ["{username}"]) {{
            nodes {{
                id
                username
            }}
        }}
    }}'''
)

def fetch_users():
    try:
        response = client.execute(query)
        return response
    except Exception as e:
        print(e)