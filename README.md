# How to Index Sharepoint Online Content to Azure Cognitive Search

This repository outlines how to use the [SharePoint / Microsoft Graph REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-graph) to index content directly from SharePoint online to Azure Cognitive Search. 

This API was chosen because it allow near real time access to content that has changed in SharePoint online and also has the ability to efficiently tell when documents have changed and can provide user access information on the content which can be useful for performing [security trimming of search results](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search).

## Requirements

- <b>SharePoint Online Site</b>: For the Microsoft Graph REST API to be able to access your content, you will need to provide access to this REST API which will included granting [admin consent](https://learn.microsoft.com/en-us/azure/active-directory/develop/console-app-quickstart?pivots=devlang-python). Optionally, if you are a Microsoft Partner or Microsoft Employee, you can also create a demo SharePoint online site from [https://cdx.transform.microsoft.com/](https://cdx.transform.microsoft.com/). To become part of the Microsoft Partner Program, please [visit here](https://partner.microsoft.com/dashboard/account/v3/enrollment/introduction/partnership). 
- <b>Azure Cognitive Search Service</b>: The content will be indexed into an Azure Cognitive Search service. You can learn more about how to get [started here](https://learn.microsoft.com/azure/search/search-what-is-azure-search).
- <b>Python Client with Jupyter Notebook</b>: This walkthrough leverages Jupyter Notebooks to perform the tasks of indexing the content.


