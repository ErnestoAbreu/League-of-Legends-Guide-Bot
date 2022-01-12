space2 = '  '
space4 = space2 + space2
space6 = space4 + space2

def response(where: list, status_code: int, why: str) -> None:
    text = '* Ha ocurrido un error en:\n'
    for line in where:
        text += space4 + line + '\n'
    text += '\n'
    
    if status_code == 400:
        text += space4 + '400 (Bad Request) This error indicates that there is a syntax error in the request and the request has therefore been denied. The client should not continue to make similar requests without modifying the syntax or the requests being made.' + '\n'
        text += space4 + 'Common Reasons:' + '\n'
        text += space6 + 'A provided parameter is in the wrong format (e.g., a string instead of an integer).' + '\n'
        text += space6 + 'A provided parameter is invalid (e.g., beginTime and startTime specify a time range that is too large).' + '\n'
        text += space6 + 'A required parameter was not provided.' + '\n'

    if status_code == 401:
        text += space4 + '401 (Unauthorized) This error indicates that the request being made did not contain the necessary authentication credentials (e.g., an API key) and therefore the client was denied access. The client should not continue to make similar requests without including an API key in the request.' + '\n'
        text += space4 + 'Common Reasons:' + '\n'
        text += space6 + 'An API key has not been included in the request.' + '\n'
    
    if status_code == 403:
        text += space4 + '403 (Forbidden) This error indicates that the server understood the request but refuses to authorize it. There is no distinction made between an invalid path or invalid authorization credentials (e.g., an API key). The client should not continue to make similar requests.' + '\n'
        text += space4 + 'Common Reasons:' + '\n'
        text += space6 + 'An invalid API key was provided with the API request.' + '\n'
        text += space6 + 'A blacklisted API key was provided with the API request.' + '\n'
        text += space6 + 'The API request was for an incorrect or unsupported path.' + '\n'

    if status_code == 404:
        text += space4 + '404 (Not Found) This error indicates that the server has not found a match for the API request being made. No indication is given whether the condition is temporary or permanent.' + '\n'
        text += space4 + 'Common Reasons:' + '\n'
        text += space6 + 'The ID or name provided does not match any existing resource (e.g., there is no Summoner matching the specified ID).' + '\n'
        text += space6 + 'There are no resources that match the parameters specified.' + '\n'

    if status_code == 405:
        text += space4 + '405 (Method not allowed)' + '\n'

    if status_code == 415:
        text += space4 + '415 (Unsupported Media Type) This error indicates that the server is refusing to service the request because the body of the request is in a format that is not supported.' + '\n'
        text += space4 + 'Common Reasons:' + '\n'
        text += space6 + 'The Content-Type header was not appropriately set.' + '\n'
    
    if status_code == 429:
        text += space4 + '429 (Rate Limit Exceeded) This error indicates that the application has exhausted its maximum number of allotted API calls allowed for a given duration. If the client receives a Rate Limit Exceeded response the client should process this response and halt future API calls for the duration, in seconds, indicated by the Retry-After header. Applications that are in violation of this policy may have their access disabled to preserve the integrity of the API. Please refer to our Rate Limiting documentation below for more information on determining if you have been rate limited, and how to avoid it.' + '\n'
        text += space4 + 'Common Reasons:' + '\n'
        text += space6 + 'Unregulated API calls.' + '\n'
    
    if status_code == 500:
        text += space4 + '500 (Internal Server Error) This error indicates an unexpected condition or exception which prevented the server from fulfilling an API request.' + '\n'

    if status_code == 502:
        text += space4 + '502 (Bad gateway)' + '\n'

    if status_code == 503:
        text += space4 + '503 (Service Unavailable) This error indicates the server is currently unavailable to handle requests because of an unknown reason. The Service Unavailable response implies a temporary condition which will be alleviated after some delay.' + '\n'

    if status_code == 504:
        text += space4 + '504 (Gateway timeout)' + '\n'

    text += '\n'
    text += space4 + why + '\n'

    print(text)