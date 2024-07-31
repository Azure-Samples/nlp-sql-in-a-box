param location string
param principalId string
param sqlServerName string
param sqlDatabaseName string
param ipAddress string
param tags object = {}

@description('Set the administrator login for the SQL Server')
@secure()
param administratorLogin string

// Create SQL Server resource
resource sqlServer 'Microsoft.Sql/servers@2022-11-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administrators: {
        login: administratorLogin
        principalType: 'User'
        azureADOnlyAuthentication: true // enforces Azure AD authentication
        sid: principalId
        tenantId: subscription().tenantId
    }
    publicNetworkAccess: (ipAddress != '') ? 'Enabled' : 'Disabled'
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


resource sqlAllowLocalConnection 'Microsoft.Sql/servers/firewallRules@2020-11-01-preview' = if (ipAddress != '') {
  name: 'AllowLocalConnection'
  parent: sqlServer
  properties: {
    startIpAddress: ipAddress
    endIpAddress: ipAddress
  }
}

output serverName string = sqlServer.name
output databaseName string = sqlDatabase.name
