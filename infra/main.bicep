targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@description('Resource group name')
param resourceGroupName string = ''

@description('User\'s principal id')
param principalId string

@description('Tags to be used for all resources')
param tags object = {}

//OpenAI Module Parameters
@description('OpenAI resource name')
param openaiName string = ''

//SQL Module Parameters
@description('SQL Server resource name')
param sqlServerName string = ''
@description('Database name')
param sqlDatabaseName string = ''
@description('Set the administrator login for the SQL Server')
param administratorLogin string
@description('IP address to allow for SQL Server connection')
param ipAddress string = ''

//Speech Module Parameters
@description('Speech service resource name')
param speechServiceName string = ''

var location = deployment().location
var abbrs = loadJsonContent('abbreviations.json')
var uniqueSuffix = substring(uniqueString(subscription().id, environmentName), 1, 5)

var names = {
    resourceGroupName: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
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
    principalId: principalId
    ipAddress: ipAddress
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
    principalId: principalId
    ipAddress: ipAddress
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
    principalId: principalId
    ipAddress: ipAddress
    sqlServerName: names.sqlServerName
    sqlDatabaseName: names.sqlDatabaseName
    administratorLogin: administratorLogin
    tags: tags
  }
}

output SQL_SERVER_NAME string = m_sql.outputs.serverName
output SQL_DATABASE_NAME string = m_sql.outputs.databaseName
output SPEECH_SERVICE_ID string = m_speech.outputs.id
output AZURE_OPENAI_CHAT_DEPLOYMENT_NAME string = m_openai.outputs.deploymentName
output AZURE_OPENAI_ENDPOINT string = m_openai.outputs.endpoint
