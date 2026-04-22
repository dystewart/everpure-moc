import os
from pypureclient.flashblade import Client

client = Client(
    target=os.environ["PURE_BASE_URL"],
    api_token=os.environ["PURE_API_TOKEN"],
)

print(client.get_arrays())