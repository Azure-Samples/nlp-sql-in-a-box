//Declare Parameters--------------------------------------------------------------------------------------------------------------------------
param location string
param openaiName string
param gptModel string
param gptVersion string
param tags object = {}

resource openai 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openaiName
  location: location
  tags: tags
  sku: {
    name: 'S0'
  }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: openaiName
    apiProperties: {
      statisticsEnabled: false
    }
    networkAcls: {
      defaultAction: 'Allow'
    }
    publicNetworkAccess: 'Enabled'
  }
}

resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openai
  name: gptModel
  properties: {
    model: {
      format: 'OpenAI'
      name: gptModel
      version: gptVersion
    }
  }
  sku: {
    capacity: 10
    name: 'Standard'
  }
}

output id string = openai.id
output endpoint string = openai.properties.endpoint
output deploymentName string = gptDeployment.name
output apiKey string = openai.listKeys().key1
