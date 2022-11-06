import sys 
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def main(dict):
    print(dict)
    authenticator = IAMAuthenticator("API_KEY")
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url("URL")
    response = service.post_find(
                db='reviews',
                selector={'dealership': {'$eq': int(dict['dealerId'])}},
            ).get_result()
    try:  
        result= {
            'headers': {'Content-Type':'application/json'}, 
            'body': {'data':response} 
            }        
        return result
    except:  
        return { 
            'statusCode': 404, 
            'message': 'Something went wrong'
            }