import os
from typing import List

import openai
from langchain.embeddings import OpenAIEmbeddings


def get_embeddings(
    text: str, azure_deployment_name: str = "foundational-ada"
) -> List[float]:
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
