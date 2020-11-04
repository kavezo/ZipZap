import datetime
import pathlib

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# From https://stackoverflow.com/a/56292132
root_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"NA"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"NA"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"NA"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"MagiReCA"),
])
root_cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    root_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=3650)
).add_extension(
    x509.BasicConstraints(ca=True, path_length=None), critical=True
).sign(root_key, hashes.SHA256(), default_backend())

# Now we want to generate a cert from that root
cert_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
new_subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"NA"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"NA"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"NA"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"*.magica-us.com")
])
cert = x509.CertificateBuilder().subject_name(
    new_subject
).issuer_name(
    root_cert.issuer
).public_key(
    cert_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=2 * 365)
).add_extension(
    x509.SubjectAlternativeName([
        x509.DNSName(u"*.magica-us.com"),
        x509.DNSName(u"magica-us.com"),
        x509.DNSName(u"*.snaa.services"),
        x509.DNSName(u"snaa.services")
    ]),
    critical=False,
).add_extension(
    x509.ExtendedKeyUsage([
        ExtendedKeyUsageOID.SERVER_AUTH
    ]),
    critical=True,
).sign(root_key, hashes.SHA256(), default_backend())

path = 'windows/nginx_windows/nginx/conf/cert'

pathlib.Path(path).mkdir(parents=False, exist_ok=True)
with open(path + '/ca.crt', 'bw+') as f:
    f.write(root_cert.public_bytes(encoding=serialization.Encoding.PEM))
with open(path + '/ca.key', 'bw+') as f:
    f.write(root_key.private_bytes(encoding=serialization.Encoding.PEM,
                                   format=serialization.PrivateFormat.TraditionalOpenSSL,
                                   encryption_algorithm=serialization.NoEncryption()))
with open(path + '/site.key', 'bw+') as f:
    f.write(cert_key.private_bytes(encoding=serialization.Encoding.PEM,
                                   format=serialization.PrivateFormat.TraditionalOpenSSL,
                                   encryption_algorithm=serialization.NoEncryption()))
with open(path + '/site.crt', 'bw+') as f:
    f.write(cert.public_bytes(encoding=serialization.Encoding.PEM))