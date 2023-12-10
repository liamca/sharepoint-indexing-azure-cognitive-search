from typing import List, Dict
from azure.search.documents.models import Vector
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain.embeddings import OpenAIEmbeddings
import os
import openai

# load logging
from utils.ml_logging import get_logger

logger = get_logger()

class AzureSearchManager:
    def __init__(self):
        self.search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
            index_name=os.getenv("AZURE_COGNITIVE_SEARCH_INDEX_NAME"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY"))
        )

    def get_embeddings(self, text: str, azure_deployment_name: str = "foundational-ada") -> List[float]:
        """
        Retrieve embeddings for the given text using OpenAI's embedding model.

        :param text: Text to get embeddings for.
        :param azure_deployment_name: The name of the OpenAI deployment to use.
        :return: List of embeddings.
        """
        openai.api_type = "azure"
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_ENDPOINT")
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        deployment = azure_deployment_name
        model_name = "text-embedding-ada-002"
        embeddings = OpenAIEmbeddings(
            deployment=deployment,
            model=model_name,
            openai_api_base=os.getenv("OPENAI_ENDPOINT"),
            openai_api_type="azure",
            show_progress_bar=True,
            chunk_size=1000,
        )
        return embeddings.embed_query(text)


    def hybrid_retrieval_rerank(self, search_query: str, security_group: str, azure_deployment_name: str = "foundational-ada", top_k: int = 5, semantic_configuration_name: str = "config") -> List[Dict]:
        """
        Perform hybrid retrieval and reranking on the search results.

        :param search_query: The search query text.
        :param security_group: The security group to filter results by.
        :param azure_deployment_name: The name of the OpenAI deployment to use.
        :param top_k: Number of top results to fetch.
        :param semantic_configuration_name: The name of the semantic search configuration to use.
        :return: List of search results with reranking scores.
        """
        try:
            results = self.search_client.search(
                search_text=search_query,
                top=top_k,
                vectors=[Vector(value=self.get_embeddings(search_query, azure_deployment_name), k=50, fields="content_vector")],
                query_type="semantic",
                semantic_configuration_name=semantic_configuration_name,
                query_language="en-us",
                filter=f"security_group eq '{security_group}'"
            )

            formatted_results = []
            for doc in results:
                content = doc["content"].replace("\n", " ")[:1000]
                formatted_results.append({
                    "score": doc['@search.score'],
                    "reranker_score": doc['@search.reranker_score'],
                    "content": content
                })

            logger.info(f"Search query: {search_query}, results: {formatted_results}")

            # Extract only the "content" field from each result
            content_list = [result["content"] for result in formatted_results]

            return content_list
        except Exception as e:
            logger.error(f"Error retrieving search results: {e}")