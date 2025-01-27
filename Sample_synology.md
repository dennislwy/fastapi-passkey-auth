# Register Options Response
GET https://account.synology.com/web/api/v1/webauthn/register/begin
```
{
    "rp": {
        "name": "Synology Account",
        "id": "account.synology.com"
    },
    "user": {
        "name": "gsftech.my@gmail.com",
        "displayName": "gsftech.my@gmail.com",
        "id": "rjp71QdXQWuOvhyj_o2eNA"
    },
    "challenge": "mGyUqN5RCODQB9PUOERtAQQuXFbasLkGjC6Tpl1l8BI",
    "pubKeyCredParams": [
        {
            "type": "public-key",
            "alg": -7
        },
        {
            "type": "public-key",
            "alg": -35
        },
        {
            "type": "public-key",
            "alg": -36
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
            "alg": -8
        }
    ],
    "timeout": 300000,
    "excludeCredentials": [
        {
            "type": "public-key",
            "id": "2JiA-ZTSzevCzGW7ioTb-1RgHrhsYXWgWlfqdSGepbc",
            "transports": [
                "hybrid",
                "internal"
            ]
        }
    ],
    "authenticatorSelection": {
        "requireResidentKey": false,
        "residentKey": "preferred",
        "userVerification": "preferred"
    }
}
```

# Registration verify
POST https://account.synology.com/web/api/v1/webauthn/register/validate
```
{
   "id":"dRtKsNl0TSyoh8G0XIUUmQ",
   "rawId":"dRtKsNl0TSyoh8G0XIUUmQ",
   "response":{
      "attestationObject":"o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YViUP_lqabXe_gyzjJZwpbY6Hwdx4e_4mF2G5tINDd0nXahdAAAAANVIgm55tNtAo9gREW9-g0kAEHUbSrDZdE0sqIfBtFyFFJmlAQIDJiABIVggnVEakFjEUDLAvZh2fHXKKhextAn610T5gyBBzjZcoGsiWCAc51HOtKFM8EG6t9Eqf81KDql87O-c5FnOmTFb6KRNvw",
      "clientDataJSON":"eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoibUd5VXFONVJDT0RRQjlQVU9FUnRBUVF1WEZiYXNMa0dqQzZUcGwxbDhCSSIsIm9yaWdpbiI6Imh0dHBzOi8vYWNjb3VudC5zeW5vbG9neS5jb20iLCJjcm9zc09yaWdpbiI6ZmFsc2V9",
      "transports":[
         "internal"
      ]
   },
   "type":"public-key",
   "clientExtensionResults":{

   },
   "authenticatorAttachment":"platform"
}
```

# Auth validate
POST https://account.synology.com/public/api/v1/webauthn/login_with_email/validate
{
   "email":"gsftech.my@gmail.com",
   "response":"{\"id\":\"dRtKsNl0TSyoh8G0XIUUmQ\",\"rawId\":\"dRtKsNl0TSyoh8G0XIUUmQ\",\"response\":{\"authenticatorData\":\"P_lqabXe_gyzjJZwpbY6Hwdx4e_4mF2G5tINDd0nXagdAAAAAA\",\"clientDataJSON\":\"eyJ0eXBlIjoid2ViYXV0aG4uZ2V0IiwiY2hhbGxlbmdlIjoiMjFQdTllcUE1NlItZ2VmM1UtakwwcUw3Qm5JQmVQeHNHMHVQUlVVSmhXNCIsIm9yaWdpbiI6Imh0dHBzOi8vYWNjb3VudC5zeW5vbG9neS5jb20iLCJjcm9zc09yaWdpbiI6ZmFsc2V9\",\"signature\":\"MEYCIQCyXTrDtWymrFm0SWXgxZNVWB_UigqaHMG3Wq9UqarawwIhAP7-xTeDWkvMB3uDIXlonNdoxRz90cl99fEyn9wy4eqA\",\"userHandle\":\"rjp71QdXQWuOvhyj_o2eNA\"},\"type\":\"public-key\",\"clientExtensionResults\":{},\"authenticatorAttachment\":\"platform\"}"
}

{
   "id":"dRtKsNl0TSyoh8G0XIUUmQ",
   "rawId":"dRtKsNl0TSyoh8G0XIUUmQ",
   "response":{
      "authenticatorData":"P_lqabXe_gyzjJZwpbY6Hwdx4e_4mF2G5tINDd0nXagdAAAAAA",
      "clientDataJSON":"eyJ0eXBlIjoid2ViYXV0aG4uZ2V0IiwiY2hhbGxlbmdlIjoiMjFQdTllcUE1NlItZ2VmM1UtakwwcUw3Qm5JQmVQeHNHMHVQUlVVSmhXNCIsIm9yaWdpbiI6Imh0dHBzOi8vYWNjb3VudC5zeW5vbG9neS5jb20iLCJjcm9zc09yaWdpbiI6ZmFsc2V9",
      "signature":"MEYCIQCyXTrDtWymrFm0SWXgxZNVWB_UigqaHMG3Wq9UqarawwIhAP7-xTeDWkvMB3uDIXlonNdoxRz90cl99fEyn9wy4eqA",
      "userHandle":"rjp71QdXQWuOvhyj_o2eNA"
   },
   "type":"public-key",
   "clientExtensionResults":{

   },
   "authenticatorAttachment":"platform"
}