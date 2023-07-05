# How to Index Sharepoint Online Content to Azure Cognitive Search

This repository outlines how to use the [SharePoint / Microsoft Graph REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-graph) to index content directly from SharePoint online to Azure Cognitive Search. 

This API was chosen because it allow near real time access to content that has changed in SharePoint online and also has the ability to efficiently tell when documents have changed and can provide user access information on the content which can be useful for performing [security trimming of search results](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search).

## Requirements

- <b>SharePoint Online Site</b>: For the Microsoft Graph REST API to be able to access your content, you will need to provide access to this REST API which will included granting [admin consent](https://learn.microsoft.com/en-us/azure/active-directory/develop/console-app-quickstart?pivots=devlang-python). Optionally, if you are a Microsoft Partner or Microsoft Employee, you can also create a demo SharePoint online site from [https://cdx.transform.microsoft.com/](https://cdx.transform.microsoft.com/). To become part of the Microsoft Partner Program, please [visit here](https://partner.microsoft.com/dashboard/account/v3/enrollment/introduction/partnership). 
- <b>Azure Cognitive Search Service</b>: The content will be indexed into an Azure Cognitive Search service. You can learn more about how to get [started here](https://learn.microsoft.com/azure/search/search-what-is-azure-search).
- <b>Python v3+ Client with Jupyter Notebook</b>: This walkthrough leverages Jupyter Notebooks to perform the tasks of indexing the content.

## Configuring Access for Microsoft Graph REST API

At this point, you should have a SharePoint Online site that has one or more documents that will need to be indexed. It is highly recommended that you review this [entire document](https://learn.microsoft.com/azure/active-directory/develop/console-app-quickstart?pivots=devlang-python) so you can get a good idea on how authentication works.

### Register Application
As outlined in this document, to register your application and add the app's registration information to your solution manually, follow these steps:

- Sign in to the [Azure portal](https://portal.azure.com/).
- If you have access to multiple tenants, use the Directories + subscriptions filter  in the top menu to switch to the tenant in which you want to register the application.
- Search for and select Azure Active Directory.
- Under Manage, select App registrations > New registration.
- Enter a Name for your application, for example <code>Daemon-console</code>. Users of your app might see this name, and you can change it later.
- Select Register.
- Under Manage, select Certificates & secrets.
- Under Client secrets, select New client secret, enter a name, and then select Add. Record the secret value in a safe location for use in a later step.
- Under Manage, select API Permissions > Add a permission. Select Microsoft Graph.
- Select Application permissions.
- Under User node, select User.Read.All, then select Add permissions.


