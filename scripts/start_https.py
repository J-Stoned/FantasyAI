#!/usr/bin/env python3
"""
Start the FastAPI server with HTTPS support for Yahoo OAuth
"""

import os
import sys
import ssl
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from main import app
from config.settings import settings

def create_self_signed_cert():
    """Create a self-signed certificate for HTTPS"""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    import datetime
    
    # Generate private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Fantasy AI Dev"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())
    
    # Save to temporary files
    cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
    cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
    cert_file.close()
    
    key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
    key_file.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))
    key_file.close()
    
    return cert_file.name, key_file.name

def main():
    """Main startup function with HTTPS"""
    print("Starting Fantasy AI Ultimate with HTTPS")
    print(f"Version: {settings.app_version}")
    
    # Create SSL certificate
    try:
        from cryptography import x509
        cert_file, key_file = create_self_signed_cert()
        print(f"Created self-signed certificate for HTTPS")
    except ImportError:
        print("Installing cryptography package for HTTPS support...")
        os.system(f"{sys.executable} -m pip install cryptography")
        cert_file, key_file = create_self_signed_cert()
    
    # Create necessary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print(f"\nHTTPS Server will be available at: https://localhost:8000")
    print(f"API Documentation: https://localhost:8000/docs")
    print(f"OAuth Callback: https://localhost:8000/auth/callback")
    print("\nNOTE: Your browser will show a security warning about the self-signed certificate.")
    print("This is normal for local development. Click 'Advanced' and 'Proceed to localhost'")
    
    # Start the server with HTTPS
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=key_file,
        ssl_certfile=cert_file,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
    
    # Cleanup
    os.unlink(cert_file)
    os.unlink(key_file)

if __name__ == "__main__":
    main()