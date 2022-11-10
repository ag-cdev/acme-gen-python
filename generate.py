import argparse
import sys
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

#--

def generate_key():
    key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    )
    return key

def save_key(key, path, passphrase=None):
    try:
        with open(path, "wb") as f:
            if passphrase == None :
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                    ))
            else:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
                    ))
        return True
    except IOError:
        return False

def generate_csr(key, args):
    csr_data = {}
    csr_data['COUNTRY_NAME'] = args.country_name
    csr_data['STATE_NAME'] = args.state_name
    csr_data['LOCALITY_NAME'] = args.locality_name
    csr_data['ORGANIZATION_NAME'] = args.organization_name
    csr_data['EMAIL'] = args.email
    csr_data['COMMON_NAME'] =  args.common_name
    # Generate a CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.COUNTRY_NAME, csr_data['COUNTRY_NAME']),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, csr_data['STATE_NAME']),
        x509.NameAttribute(NameOID.LOCALITY_NAME, csr_data['LOCALITY_NAME']),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, csr_data['ORGANIZATION_NAME']),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, csr_data['EMAIL']),
        x509.NameAttribute(NameOID.COMMON_NAME, csr_data['COMMON_NAME']),

    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(csr_data['COMMON_NAME']),
            #x509.DNSName(input),
        ]),
        critical=False,
    # Sign the CSR with the private key.
    ).sign(key, hashes.SHA256())
    return csr

def save_csr(path, csr):
    try:
        with open(path, "wb") as f:
            f.write(csr.public_bytes(serialization.Encoding.PEM))
        return True
    except IOError:
        return False

def domain_name(cert):
    for attribute in cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME):
        return attribute.value
    return None

def main():
    parser = argparse.ArgumentParser('CSR Generator')
    parser.add_argument('--common_name', help='Common Name', required=True)
    parser.add_argument('--state_name', help='State Name', default= "STATE")
    parser.add_argument('--locality_name', help='Locality Name', default= "LOCALITY")
    parser.add_argument('--organization_name', help='Organization Name', default="ORGZ")
    parser.add_argument('--email', help='Email', required=True)
    parser.add_argument('--country_name', help='Country Name', default="US")
    parser.add_argument('--key_file', help='Key File', required=True)
    parser.add_argument('--csr_file', help='CSR File', required=True)
    args = parser.parse_args()
    #args.infile
    cert_key = generate_key()
    if save_key(cert_key, args.key_file) == True:
        csr = generate_csr(cert_key, args)
        if save_csr(args.csr_file, csr) == True :
            print("CSR written successfully!!")
if __name__=="__main__":
    main()
