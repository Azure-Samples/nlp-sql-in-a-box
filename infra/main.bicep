targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

param resourceGroupName string = ''

param tags object

//OpenAI Module Parameters
param openaiName string = ''

//SQL Module Parameters
param sqlServerName string = ''
param sqlDatabaseName string = ''
@description('Set the administrator login for the SQL Server')
param administratorLogin string
@secure()
@minLength(8)
@description('Set the administrator login password for the SQL Server')
param administratorLoginPassword string

//Speech Module Parameters
param speechServiceName string = ''

var abbrs = loadJsonContent('abbreviations.json')
var uniqueSuffix = substring(uniqueString(subscription().id, environmentName), 1, 5)

var names = {
    resourceGroupName: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${uniqueSuffix}'
    openaiName: !empty(openaiName) ? openaiName : '${abbrs.cognitiveServicesOpenAI}${environmentName}-${uniqueSuffix}'
    speechServiceName: !empty(speechServiceName) ? speechServiceName : '${abbrs.cognitiveServicesSpeech}${environmentName}-${uniqueSuffix}'
    sqlServerName: !empty(sqlServerName) ? sqlServerName : '${abbrs.sqlServers}${environmentName}-${uniqueSuffix}'
    sqlDatabaseName: !empty(sqlDatabaseName) ? sqlDatabaseName : '${abbrs.sqlServersDatabases}${environmentName}-${uniqueSuffix}'
}


// 1. Create resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: names.resourceGroupName
  location: location
  tags: tags
}


// 2. Deploy OpenAI
module m_openai 'modules/openai.bicep' = {
  name: 'deploy_openai'
  scope: resourceGroup
  params: {
    location: location
    openaiName: names.openaiName
    tags: tags
  }
}

// 3. Deploy Speech Service
module m_speech 'modules/speech.bicep' = {
  name: 'deploy_speech'
  scope: resourceGroup
  params: {
    location: location
    speechServiceName: names.speechServiceName
    tags: tags
  }
}

//4. Deploy SQL Server and Database
module m_sql 'modules/sql.bicep' = {
  name: 'deploy_sql'
  scope: resourceGroup
  params: {
    location: location
    sqlServerName: names.sqlServerName
    sqlDatabaseName: names.sqlDatabaseName
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    tags: tags
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name
output SQL_SERVER_NAME string = m_sql.outputs.serverName
output SQL_DATABASE_NAME string = m_sql.outputs.databaseName
output SQL_USERNAME string = administratorLogin
output SPEECH_SERVICE_API_KEY string = m_speech.outputs.apiKey
output AZURE_OPENAI_CHAT_DEPLOYMENT_NAME string = m_openai.outputs.deploymentName
output AZURE_OPENAI_API_KEY string = m_openai.outputs.apiKey
output AZURE_OPENAI_ENDPOINT string = m_openai.outputs.endpoint
