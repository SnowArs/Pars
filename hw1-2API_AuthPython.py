import cloudmersive_validate_api_client
from cloudmersive_validate_api_client.rest import ApiException
from pprint import pprint

#create an instance of the API class
api_instance = cloudmersive_validate_api_client.DomainApi()
domain = 'cloudmersive.com' 


# Configure API key authorization: Apikey

api_instance.api_client.configuration.api_key = {}
api_instance.api_client.configuration.api_key['Apikey'] = '750c495b-3211-4331-a816-00b75c5311cc'

try:
    # Validate a domain name
    api_response = api_instance.domain_check(domain)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DomainApi->domain_check: %s\n" % e)
