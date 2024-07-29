param location string
param speechServiceName string
param tags object = {}

// Create Speech Service resource
resource speechService 'Microsoft.CognitiveServices/accounts@2022-03-01' = {
  name: speechServiceName
  location: location
  kind: 'SpeechServices'
  sku: {
    name: 'S0'
    tier: 'Standard'
  }
  properties: {
    customSubDomainName: speechServiceName // Set the custom subdomain name for the Speech Service
  }
  tags: tags
}

output id string = speechService.id
output name string = speechService.name
output endpoint string = speechService.properties.endpoint
output apiKey string = listKeys(speechService.id, '2022-03-01').key1
