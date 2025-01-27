# Register options response
```
{
    "rp": {
        "name": "MyCompanyName",
        "id": "localhost"
    },
    "user": {
        "id": "ZGVubmlz",
        "name": "dennis@gsfcorp.com",
        "displayName": "Samuel Colvin"
    },
    "challenge": "6aN1Y17sqOJZmjFPsGN4CKGkO8H9wvYZOMVOJZiNu2efTH5x9uCLQWWa9Jryb2YinDXzuYEv-VjveFNJnOPx9Q",
    "pubKeyCredParams": [
        {
            "type": "public-key",
            "alg": -7
        },
        {
            "type": "public-key",
            "alg": -8
        },
        {
            "type": "public-key",
            "alg": -36
        },
        {
            "type": "public-key",
            "alg": -37
        },
        {
            "type": "public-key",
            "alg": -38
        },
        {
            "type": "public-key",
            "alg": -39
        },
        {
            "type": "public-key",
            "alg": -257
        },
        {
            "type": "public-key",
            "alg": -258
        },
        {
            "type": "public-key",
            "alg": -259
        }
    ],
    "timeout": 60000,
    "excludeCredentials": [],
    "authenticatorSelection": {
        "authenticatorAttachment": "cross-platform",
        "residentKey": "discouraged",
        "requireResidentKey": false,
        "userVerification": "required"
    },
    "attestation": "none"
}
```

# Register verify request
```
{
   "id":"6PTQNB4ZSOasFsZ8Vv5_rA",
   "rawId":"6PTQNB4ZSOasFsZ8Vv5/rA==",
   "response":{
      "attestationObject":"o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YViUSZYN5YgOjGh0NBcPZHZgW4/krrmihjLHmVzzuoMdl2NdAAAAANVIgm55tNtAo9gREW9+g0kAEOj00DQeGUjmrBbGfFb+f6ylAQIDJiABIVggjPZiwbJm4sOF+Q0IbO+AJUL6Sa7Aj7PSt8LiCR3YcJAiWCBugfo36F5HUlSC/XWbUryxtAp6pQn+OVYWQiTxM3heNw==",
      "clientDataJSON":"eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiNmFOMVkxN3NxT0pabWpGUHNHTjRDS0drTzhIOXd2WVpPTVZPSlppTnUyZWZUSDV4OXVDTFFXV2E5SnJ5YjJZaW5EWHp1WUV2LVZqdmVGTkpuT1B4OVEiLCJvcmlnaW4iOiJodHRwOi8vbG9jYWxob3N0OjgwMDAiLCJjcm9zc09yaWdpbiI6ZmFsc2V9"
   }
}

{
   "id":"6PTQNB4ZSOasFsZ8Vv5_rA",
   "raw_id":"6PTQNB4ZSOasFsZ8Vv5/rA==",
   "response":{
      "attestation_object":"o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YViUSZYN5YgOjGh0NBcPZHZgW4/krrmihjLHmVzzuoMdl2NdAAAAANVIgm55tNtAo9gREW9+g0kAEOj00DQeGUjmrBbGfFb+f6ylAQIDJiABIVggjPZiwbJm4sOF+Q0IbO+AJUL6Sa7Aj7PSt8LiCR3YcJAiWCBugfo36F5HUlSC/XWbUryxtAp6pQn+OVYWQiTxM3heNw==",
      "client_data_json":"eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiNmFOMVkxN3NxT0pabWpGUHNHTjRDS0drTzhIOXd2WVpPTVZPSlppTnUyZWZUSDV4OXVDTFFXV2E5SnJ5YjJZaW5EWHp1WUV2LVZqdmVGTkpuT1B4OVEiLCJvcmlnaW4iOiJodHRwOi8vbG9jYWxob3N0OjgwMDAiLCJjcm9zc09yaWdpbiI6ZmFsc2V9"
   }
}
```