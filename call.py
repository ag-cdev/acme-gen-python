import simple_acme_dns
import route53
import sys
import argparse
import os 

verbose = True if "--verbose" in sys.argv else False

def save_certificate(path, cert):
    try:
        with open(path, "wb") as f:
            f.write(cert)
            #f.write(cert.public_bytes(serialization.Encoding.PEM))
        return True
    except IOError:
        return False

def main():
    parser = argparse.ArgumentParser('Certificate Generator')
    parser.add_argument('--csr_file', help='CSR File', required=True)
    parser.add_argument('--email', help='Email', required=True)
    parser.add_argument('--cert_file', help='Email', required=True)
    parser.add_argument('--subdomain', help='Cname name to add', default= False)
    parser.add_argument('--cname', help='Cname value to add', default= False)
    parser.add_argument('--dnszone', help='Domain root for cname', default= False)
    parser.add_argument('--staging', action='store_true', help='Uses staging server')
    args = parser.parse_args()
    if args.staging:
        print("Staging in Use")
        dir_acme = "https://acme-staging-v02.api.letsencrypt.org/directory"
    else:
        dir_acme = "https://acme-v02.api.letsencrypt.org/directory" 
    client = simple_acme_dns.ACMEClient(
        email=args.email,
        directory= dir_acme,
        nameservers=["8.8.8.8", "1.1.1.1"],
            csr = open(args.csr_file, 'rb').read()
    )
    client.new_account()
    if 'ACCESS_KEY_ID' and 'SECRET_ACCESS_KEY' in os.environ:
        call_dns = route53.DNS(access_key_id=os.environ['ACCESS_KEY_ID'] ,secret_access_key=os.environ['SECRET_ACCESS_KEY'])
    else:
        call_dns = route53.DNS(access_key_id='' ,secret_access_key='')
    if args.subdomain and args.cname and args.dnszone:
            call_dns._change_cname_record("UPSERT", args.subdomain, args.cname, args.dnszone)
    else:
            print("CNAME not Inserted")
    for domain, token in client.request_verification_tokens():
        print("{domain} --> {token}".format(domain=domain, token=token))
        root_domain = '.'.join(domain.split('.')[1:])
        call_dns.create_dns_record(root_domain, token)
    if client.check_dns_propagation(timeout=12000):
        client.request_certificate()
        save_certificate(args.cert_file, client.certificate)
    else:
        client.deactivate_account()
        print("Failed to issue certificate for " + str(client.domains))
        exit(1)

if __name__=="__main__":
    main()
