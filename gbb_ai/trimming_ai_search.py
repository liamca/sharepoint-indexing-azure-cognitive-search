import os
from typing import Dict, List, Union

import msal
import requests
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import Vector

from gbb_ai.utils import get_embeddings
# load logging
from utils.ml_logging import get_logger

logger = get_logger()


class AzureSearchManager:
    def __init__(self, index_name: str):
        self.search_client = SearchClient(
            endpoint=os.getenv("AZURE_AI_SEARCH_SERVICE_ENDPOINT"),
            index_name=index_name,
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY")),
        )

        # Microsoft Graph API setup
        self.tenant_id = os.getenv("TENANT_ID")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.graph_uri = "https://graph.microsoft.com"
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]

        # Authenticate with Microsoft Graph
        self.token = self.msgraph_auth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            authority=self.authority,
            scope=self.scope,
        )

    @staticmethod
    def msgraph_auth(client_id: str, client_secret: str, authority: str, scope: list):
        """
        Authenticate with Microsoft Graph using MSAL for Python.
        """
        app = msal.ConfidentialClientApplication(
            client_id=client_id, authority=authority, client_credential=client_secret
        )
        try:
            # Attempt to acquire token silently
            access_token = app.acquire_token_silent(scope, account=None)
            if not access_token:
                # Acquire new token
                access_token = app.acquire_token_for_client(scopes=scope)
                if "access_token" not in access_token:
                    logger.error("Error acquiring authorization token.")
                    return None
            return access_token.get("access_token")
        except Exception as err:
            logger.error(f"Error in msgraph_auth: {err}")
            raise

    def get_current_user_groups(
        self, user_id: str = "4e6b32a4-9233-4256-8e97-94e5584c5886"
    ) -> List[str]:
        """
        Retrieve the groups of the current user from Azure AD.
        """
        if not self.token:
            logger.error("Access token is not available.")
            return []

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf"

        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code != 200:
                logger.error(
                    f"Error retrieving user groups: {response.status_code} {response.reason}"
                )
                logger.error(f"Response content: {response.text}")
                return []
            groups_data = response.json()
            group_names = [
                group["displayName"]
                for group in groups_data.get("value", [])
                if group["@odata.type"] == "#microsoft.graph.group"
            ]
            return group_names
        except Exception as e:
            logger.error(f"Exception in retrieving user groups: {e}")
            return []

    def secure_hybrid_search_rerank(
        self,
        search_query: str,
        security_group: Union[str, List[str]],
        azure_deployment_name: str = "foundational-ada",
        top_k: int = 5,
        semantic_configuration_name: str = "config",
    ) -> List[Dict]:
        """
        Executes a secure, hybrid search with reranking based on semantic analysis and security group filters.

        Parameters:
        - search_query (str): The search query text to execute.
        - security_group (Union[str, List[str]]): Security group name(s) to filter the search results, ensuring data access control and relevance to the specified group(s).
        - azure_deployment_name (str, optional): The OpenAI deployment name used for semantic analysis. Defaults to "foundational-ada".
        - top_k (int, optional): The number of top results to retrieve and rerank. Defaults to 5.
        - semantic_configuration_name (str, optional): The semantic search configuration name to use. Defaults to "config".

        Returns:
        - List[Dict]: A list of search results, each as a dictionary containing the score, reranker score, and content.

        This function performs a semantic search using the specified query and Azure deployment. It filters results based on the given security group(s) for enhanced data security and relevance. The top results are then reranked to present the most pertinent information.
        """
        try:
            # Construct the filter using search.in function
            if isinstance(security_group, list):
                security_filter = (
                    f"search.in(security_group, '{','.join(security_group)}')"
                )
            else:
                security_filter = f"search.in(security_group, '{security_group}')"

            # Fetch and filter search results based on security group
            results = self.search_client.search(
                search_text=search_query,
                top=top_k,
                vectors=[
                    Vector(
                        value=get_embeddings(search_query, azure_deployment_name),
                        k=50,
                        fields="content_vector",
                    )
                ],
                query_type="semantic",
                semantic_configuration_name=semantic_configuration_name,
                query_language="en-us",
                filter=security_filter,
            )

            # Process and log the formatted results
            formatted_results = [
                {
                    "score": doc["@search.score"],
                    "reranker_score": doc["@search.reranker_score"],
                    "content": doc["content"].replace("\n", " ")[:1000],
                }
                for doc in results
            ]
            logger.info(
                "Search Results:\n"
                + "\n".join(
                    [
                        f"Result {i}:\nScore: {result['score']}\nReranker Score: {result['reranker_score']}\nContent: {result['content']}\n{'-'*50}"
                        for i, result in enumerate(formatted_results, 1)
                    ]
                )
            )

            return [result["content"] for result in formatted_results]
        except Exception as e:
            logger.error(f"Error retrieving search results: {e}")
