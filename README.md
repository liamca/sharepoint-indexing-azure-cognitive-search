# How to Index Sharepoint Online Content to Azure Cognitive Search

This repository outlines how to use the [SharePoint / Microsoft Graph REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-graph) to index content directly from SharePoint online to Azure Cognitive Search. 

This API was chosen because it allow near real time access to content that has changed in SharePoint online and also has the ability to efficiently tell when documents have changed and can provide user access information on the content which can be useful for performing [security trimming of search results](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search).


