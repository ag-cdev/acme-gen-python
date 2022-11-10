
# Acme Gen Python

contain two main scripts one is generate.py and the second is call.py ;
It also includes a modified verison of simple_acme_dns pip package.

## Please note that the files have help included in them explaining parameters.


## Generate.py

used to generate CSR and privatekey

```bash
  Requires env vars or modify it inside the script (contains default values)
  python3 generate.py 
```
## Call.py

used to generate cert from CSR

```bash
  Requires the path to cert file rest will be done by script
  python3 call.py 
```

## How to use

```bash
run the generate script and get a csr
change the properties of the csr in script or use params
using - python3 generate.py 

get the aws creds and add it to call.py or to the env
then run the script and pass the cert file path.
using - python3 call.py
```

python3 generate.py --common_name "alice5.ssl.w.in" --email "admin@w.com" --key_file alice.pem --csr_file alice-csr.pem

python3 call.py --csr_file "alice-csr.pem" --email "admin@w.com" --cert_file "alice-cert.pem" --subdomain "alice5" --cname "server1" --dnszone "ssl.w.in"  --staging