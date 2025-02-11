from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import os

gitlab_token = os.getenv("GITLAB_TOKEN")

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

def get_user_info(user_id):
    query = gql(f'''
        query User {{
            user(id: "gid://gitlab/User/{user_id}") {{
                username
                name
            }}
        }}'''
    )
    try:
        response = client.execute(query)
        return response
    except Exception as e:
        print(e)