param location string
param principalId string
param sqlServerName string
param sqlDatabaseName string
param tags object = {}

@description('Set the administrator login for the SQL Server')
@secure()
param administratorLogin string
@description('Set the administrator login password for the SQL Server')
@secure()
param administratorLoginPassword string

// Create SQL Server resource
resource sqlServer 'Microsoft.Sql/servers@2022-11-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administrators: {
        login: 'admin'
        principalType: 'User'
        azureADOnlyAuthentication: true // enforces Azure AD authentication
        sid: principalId
        tenantId: subscription().tenantId
    }
    publicNetworkAccess: 'Enabled'
  }
  tags: tags
}

// Create SQL Database resource
resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-11-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  tags: tags
}

output serverName string = sqlServer.name
output databaseName string = sqlDatabase.name
