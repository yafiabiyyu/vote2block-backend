# Vote2Block Ethereum Blockchain

## Ethereum Network
| Chain ID | Name                     | Chain   | Network |
| ---------|:------------------------:|:-------:| ------- |
| 3        | Ethereum Testnet Ropsten | ETH     | Ropsten |
| 5777     | Private Blockchain       | ETH     | Private |

## Root URL
http://127.0.0.1:5000/vote2block/api/v1

## Database
### User Document
```json
{
    "_id":"<ObjectID>",
    "username":"yafiabiyyu",
    "password":"CodingJos",
    "nama_lengkap":"Abiyyu Yafi",
    "contact":{
        "phone":"+62xxxxxxxxxxx",
        "email":"emailuser@mail.co"
    },
    "alamat":{
        "provinsi":"Jawa Timur",
        "kota":"Malang",
        "alamat_lengkap":"Jl Senggani 500 jos gandos"
    },
    "access":{
        "level":1,
        "group":"dev"
    },
    "ethereum":{
        "ethereum_address":"0xFabf8979D3A16170ce8a13C1281268fb37e8f55b",
        "ethereum_access":"d2df65c7033667d7e9138957b64f3682cf94de39953827e37"
    }
}
```