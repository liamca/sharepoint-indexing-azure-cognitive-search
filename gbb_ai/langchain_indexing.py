import os
from typing import Dict, List, Optional

import openai
from azure.search.documents.indexes.models import (
    SearchFieldDataType, SearchField, SimpleField, SearchableField, SemanticSettings, SemanticConfiguration, PrioritizedFields, SemanticField
)

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
from langchain.docstore.document import Document

from utils.ml_logging import get_logger

# Initialize logging
logger = get_logger()


class TextChunkingIndexing:
    """
    This class is responsible for chunking text data.
    It loads the necessary environment variables upon initialization.
    """

    def __init__(self):
        """
        Initialize the TextChunking class and load the environment variables.
        """
        self.envs = self.load_environment_variables()

    @staticmethod
    def load_environment_variables() -> Dict[str, str]:
        """
        Loads required environment variables for the application.

        This function reads environment variables from the .env file and the system,
        ensuring that all necessary variables for OpenAI and vector store configuration are set.
        If any required variable is missing, it raises an EnvironmentError.

        :return: A dictionary containing the values of the required environment variables.
        :raises EnvironmentError: If any required environment variable is missing.
        """
        load_dotenv()

        required_vars = [
            "OPENAI_API_KEY",
            "OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_AI_SEARCH_SERVICE_ENDPOINT",
            "AZURE_SEARCH_ADMIN_KEY",
        ]
        env_vars: Dict[str, Optional[str]] = {
            var: os.getenv(var) for var in required_vars
        }

        if not all(env_vars.values()):
            missing_vars = [var for var, value in env_vars.items() if not value]
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return env_vars

    @staticmethod
    def setup_aoai(
        api_key: Optional[str] = None,
        resource_endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        """
        Configures the OpenAI API client with the specified parameters.

        Sets the API key, resource endpoint, and API version for the OpenAI client to interact with Azure services.

        :param api_key: The API key for authentication with the OpenAI service.
        :param resource_endpoint: The base URL of the Azure OpenAI resource endpoint.
        :param api_version: The version of the OpenAI API to be used.
        """
        openai.api_type = "azure"
        openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_base = resource_endpoint or os.getenv("OPENAI_ENDPOINT")
        openai.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION")

    def load_embedding_model(
        self,
        deployment: str,
        model_name: Optional[str] = "text-embedding-ada-002",
        openai_api_base: Optional[str] = None,
        chunk_size: Optional[int] = 1000,
    ) -> OpenAIEmbeddings:
        """
        Loads and returns an OpenAIEmbeddings object with the specified configuration.

        :param deployment: The deployment ID for the OpenAI model.
        :param model_name: The name of the OpenAI model to use.
        :param openai_api_base: The base URL for the OpenAI API.
        :param chunk_size: (optional) The size of chunks for processing data. Defaults to 1.
        :return: Configured OpenAIEmbeddings object.
        """
        logger.info(
            f"Loading OpenAIEmbeddings object with model {model_name}, deployment {deployment}, and chunk size {chunk_size}"
        )

        try:
            self.embeddings = OpenAIEmbeddings(
                deployment=deployment,
                model=model_name,
                openai_api_base=openai_api_base or self.envs["OPENAI_ENDPOINT"],
                openai_api_type="azure",
                show_progress_bar=True,
                chunk_size=chunk_size,
            )
            logger.info("OpenAIEmbeddings object created successfully.")
            return self.embeddings
        except Exception as e:
            logger.error(f"Error in creating OpenAIEmbeddings object: {e}")
            raise

    def setup_azure_search(
        self,
        endpoint: Optional[str] = None,
        admin_key: Optional[str] = None,
        index_name: str = "langchain-vector-demo",
    ) -> AzureSearch:
        """
        Creates and configures an AzureSearch instance with the specified parameters or from environment variables.

        If the endpoint or admin_key parameters are not provided, the function attempts to retrieve them from the environment variables.
        If any required parameter is missing, an error is raised.

        :param endpoint: (optional) The base URL of the Azure Cognitive Search endpoint. Defaults to environment variable.
        :param admin_key: (optional) The admin key for authentication with the Azure Cognitive Search service. Defaults to environment variable.
        :param index_name: (optional) The name of the index to be used. Defaults to "langchain-vector-demo".
        :return: Configured AzureSearch object.
        :raises ValueError: If the endpoint or admin_key is missing.
        """
        # Default to environment variables if parameters are not provided
        resolved_endpoint = endpoint or os.getenv("AZURE_AI_SEARCH_SERVICE_ENDPOINT")
        resolved_admin_key = admin_key or os.getenv("AZURE_SEARCH_ADMIN_KEY")

        # Validate that all required configurations are set
        if not all([resolved_endpoint, resolved_admin_key]):
            missing_params = [
                param
                for param, value in {
                    "endpoint": resolved_endpoint,
                    "admin_key": resolved_admin_key,
                }.items()
                if not value
            ]
            logger.error(f"Missing required parameters: {', '.join(missing_params)}")
            raise ValueError(
                f"Missing required parameters: {', '.join(missing_params)}"
            )
        
        if not self.embeddings:
            raise ValueError("OpenAIEmbeddings object has not been configured. Please call load_embedding_model() first.")
        

        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String, searchable=True),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=len(self.embeddings.embed_query("Text")), #TODO: review 
                vector_search_configuration="default",
            ),
            SearchableField(name="metadata", type=SearchFieldDataType.String, searchable=True),
            SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="security_group", type=SearchFieldDataType.String, filterable=True),
        ]

        self.vector_store = AzureSearch(
            azure_search_endpoint=resolved_endpoint,
            azure_search_key=resolved_admin_key,
            index_name=index_name,
            embedding_function=self.embeddings.embed_query,
            fields=fields,
            semantic_settings=SemanticSettings(
                default_configuration="config",
                configurations=[
                    SemanticConfiguration(
                        name="config",
                        prioritized_fields=PrioritizedFields(
                            title_field=SemanticField(field_name="content"),
                            prioritized_content_fields=[
                                SemanticField(field_name="content")
                            ],
                            prioritized_keywords_fields=[
                                SemanticField(field_name="metadata")
                            ],
                        ),
                    )
                ],
            ),
        )

        logger.info("Azure Cognitive Search client configured successfully.")
        return self.vector_store

    @staticmethod
    def split_documents_in_chunks(
        documents: List[Document],
        chunk_size: Optional[int] = 1000,
        chunk_overlap: Optional[int] = 200,
        separators: Optional[List[str]] = None,
        keep_separator: bool = True,
        is_separator_regex: bool = False,
        **kwargs,
    ) -> List[str]:
        """
        Splits text from a list of Document objects into manageable chunks. This method primarily uses character 
        count to determine chunk sizes but can also utilize separators for splitting.
        
        :param documents: List of Document objects to split.
        :param chunk_size: (optional) The number of characters in each text chunk. Defaults to 1000.
        :param chunk_overlap: (optional) The number of characters to overlap between chunks. Defaults to 200.
        :param separators: (optional) List of strings or regex patterns to use as separators for splitting.
        :param keep_separator: (optional) Whether to keep the separators in the resulting chunks. Defaults to True.
        :param is_separator_regex: (optional) Treat the separators as regex patterns. Defaults to False.
        :param kwargs: Additional keyword arguments for customization.
        :return: A list of text chunks.
        :raises Exception: If an error occurs during the text splitting process.
        """

        try:
            # split documents into text and embeddings
            text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            separators=separators,
            keep_separator=keep_separator,
            is_separator_regex=is_separator_regex,
            **kwargs
            )
            chunks = text_splitter.split_documents(documents)
            return chunks
        except Exception as e:
            logger.error(f"Error in scraping and splitting text: {e}")
            raise


    def embed_and_index(self, texts: List[str]) -> None:
        """
        Embeds the given texts and indexes them in the configured vector store.

        This method first checks if the vector store (like Azure Cognitive Search) is configured.
        If configured, it proceeds to add the provided texts to the vector store for indexing.

        Args:
            texts (List[str]): A list of text strings to be embedded and indexed.

        Raises:
            ValueError: If the vector store client is not configured.
            Exception: If any other error occurs during the embedding and indexing process.
        """
        try:
            if not self.vector_store:
                raise ValueError(
                    "Azure Cognitive Search client has not been configured."
                )

            self.vector_store.add_documents(documents=texts)
        except Exception as e:
            logger.error(f"Error in embedding and indexing: {e}")
            raise
