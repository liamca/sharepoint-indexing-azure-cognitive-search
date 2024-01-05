# How to Index Sharepoint Online Content to Azure AI Search

**Note** This repo is in beta stage and still being tested. Please report any issues you find so we can provide a complete approach for indexing content from SharePoint Online to Azure AI Search.

This notebook demonstrates the integration of the SharePoint / Microsoft Graph REST API for indexing content directly from SharePoint Online into Azure AI Search.

We have created the SharePointDataExtractor class based on the principle of dependency injection to simplify and abstract the complexity involved in the process of indexing content from SharePoint to Azure AI Search. This approach streamlines the handling of [security trimming](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search) and efficient content updates. It is particularly beneficial for applications that require real-time data synchronization and secure data access.

For more detailed information on using the SharePoint / Microsoft Graph REST API, refer to the official documentation [here](https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-graph).

## 💡 Solution

> 📌 **Note**
>
> For a comprehensive example, please refer to the [Indexing Content Notebook](01-indexing-content-beta.ipynb).

### SharePointDataExtractor Class

The `SharePointDataExtractor` class, located in the `src/gbb_ai/sharepoint_data_extractor.py` module, is designed to simplify and optimize the process of extracting data from SharePoint using the Microsoft Graph API. It provides efficient mechanisms for authentication and data retrieval from SharePoint sites.

> ❗The class is extensible, allowing for custom logic to be added as needed. Feel free to add methods or modify existing logic to suit your specific use case.

```python
from gbb_ai.sharepoint_data_extractor import SharePointDataExtractor

# Instantiate the SharePointDataExtractor client
client_extractor = SharePointDataExtractor()
```

### Key Functionality

1. **Client Initialization**: Ensures authentication and authorization in a few lines of code. The extractor is easily set up with necessary parameters such as tenant ID, client ID, and client secret for authentication and API access. It utilizes MSAL for Python to manage secure access tokens. Environment variables can be conveniently loaded from a `.env` file for further configuration.

```python
client_extractor.load_environment_variables_from_env_file()
client_extractor.msgraph_auth()
```

2. **Data Retrieval**: 
   - Retrieves Site and Drive IDs from SharePoint.
   - Fetches files from SharePoint drives, with optional filters for modification time and file formats.
   - Gets permissions for each file for security trimming purposes.

3. **Content Processing**: 
   - Extracts text content from `.docx` and `.pdf` files.
   - Retrieves and processes file content from SharePoint drives.

4. **Metadata Extraction**: Extracts and formats metadata from SharePoint files, including web URLs, size, creation, and modification details.

```python

# Use the `retrieve_sharepoint_files_content` method to fetch file content and metadata from SharePoint
files = client_extractor.retrieve_sharepoint_files_content(site_domain=SITE_DOMAIN, site_name=SITE_NAME, folder_path="/test/test2/test3/", minutes_ago=60)

# The method returns a list of dictionaries, where each dictionary represents a file.
# Here's an example of the output `files`:
[
    {
        'content': 'LLM creators should exclude from their training data papers on creating or enhancing pathogens....',  # content
        'id': '01W3WT6PG5HFCYLSOAMNGIGWEBISZCI5X4',  # The unique identifier of the file
        'source': 'https://XXX.sharepoint.com/sites/XXX/_layouts/15/Doc.aspx?sourcedoc=%7B854539DD-C0C9-4C63-8358-8144B22476FC%7D&file=test3.docx&action=default&mobileredirect=true',  # The source URL of the file
        'name': 'test3.docx',  # The name of the file
        'size': 73576,  # The size of the file in bytes
        'created_by': 'System Administrator',  # The user who created the file
        'created_datetime': '2023-12-15T00:44:01Z',  # The date and time when the file was created
        'last_modified_datetime': '2023-12-15T00:44:15Z',  # The date and time when the file was last modified
        'last_modified_by': 'System Administrator',  # The user who last modified the file
        'read_access_entity': 'Contoso Visitors'  # The entity that has read access to the file
    },
    # ... more file data ...
]
```

## Known limitations
Currently this approach does not allow the following:
- <b>Folder or File Filters</b>: This approach does not currently implement the ability to limit indexing to specific documents or folders within a SharePoint site. In the future, we will look into adding support for SharePoint embedded which does offer this level of access granularity.

## Requirements

- <b>SharePoint Online Site</b>: For the Microsoft Graph REST API to be able to access your content, you will need to provide access to this REST API which will included granting [admin consent](https://learn.microsoft.com/en-us/azure/active-directory/develop/console-app-quickstart?pivots=devlang-python). Optionally, if you are a Microsoft Partner or Microsoft Employee, you can also create a demo SharePoint online site from [https://cdx.transform.microsoft.com/](https://cdx.transform.microsoft.com/). To become part of the Microsoft Partner Program, please [visit here](https://partner.microsoft.com/dashboard/account/v3/enrollment/introduction/partnership). 
- <b>Azure AI Search Service</b>: The content will be indexed into an Azure AI Search service. You can learn more about how to get [started here](https://learn.microsoft.com/azure/search/search-what-is-azure-search).

## Configuring Access for Microsoft Graph REST API

At this point, you should have a SharePoint Online site that has one or more documents that will need to be indexed. It is highly recommended that you review this [entire document](https://learn.microsoft.com/azure/active-directory/develop/console-app-quickstart?pivots=devlang-python) so you can get a good idea on how authentication works.

## Register Application
As outlined in this document, to register your application and add the app's registration information to your solution manually, follow these steps:

- Sign in to the [Azure portal](https://portal.azure.com/) as the Admin you copied from above/
- If you have access to multiple tenants, use the Directories + subscriptions filter  in the top menu to switch to the tenant in which you want to register the application.
- Search for and select Microsoft Entra ID.
- Under Manage, select App registrations > New registration.
- Enter a Name for your application, for example <code>sharepoint-ai-search-indexing</code>. Users of your app might see this name, and you can change it later.
- Select Register.
- Under Manage, select Certificates & secrets.
- Under Client secrets, select New client secret, enter a name, and then select Add. Record the value which will be the "Client Secret" in a safe location for use in a later step. NOTE: Do not copy the "Secret ID" as this is not needed.
- Under Manage, select API Permissions > Add a permission. Select Microsoft Graph.
- Select Application permissions.
- Under User node, select User.Read.All as well as Site.Read.All, then select Add permissions.
- If you notice that "Grant Admin Consent" is required, enable this now. Make sure all permissions have been granted admin consent. If you require an Admin, please see this [document](https://learn.microsoft.com/en-us/entra/identity-platform/index-service?pivots=devlang-python) for additional help.
- Click "Overview" and copy the "Application (client) ID" as well as the "Directory (tenant) ID"

## Configuration Env variables

We will now use environment variables to store our configuration. This is a more secure practice as it prevents sensitive data from being accidentally committed and pushed to version control systems.

Create a `.env` file in your project root and add the following variables:

```env
# Microsoft Entra ID Configuration
TENANT_ID='[Your Azure Tenant ID]'
CLIENT_ID='[Your Azure Client ID]'
CLIENT_SECRET='[Your Azure Client Secret]'

# SharePoint Site Configuration
SITE_DOMAIN='[Your SharePoint Site Domain]'
SITE_NAME='[Your SharePoint Site Name]'

# Azure AI Search Service Configuration
SEARCH_SERVICE_ENDPOINT='[Your Azure Search Service Endpoint]'
SEARCH_INDEX_NAME='[Your Azure Search Index Name]'
SEARCH_ADMIN_API_KEY='[Your Azure Search Admin API Key]'
```

Replace the placeholders (e.g., [Your Azure Tenant ID]) with your actual values.

+ `TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET` are used for authentication with Azure Active Directory.
- `SITE_DOMAIN` and `SITE_NAME` specify the SharePoint site from which data will be extracted.
+ `SEARCH_SERVICE_ENDPOINT`, `SEARCH_INDEX_NAME`, and `SEARCH_ADMIN_API_KEY` are used to configure the Azure AI Search service.

> 📌 **Note**
> Remember not to commit the .env file to your version control system. Add it to your .gitignore file to prevent it from being tracked.

