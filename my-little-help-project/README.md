# my-little-help

my-little-help is a Python utility library that provides simplified wrapper functions for rapidfuzz, pyspellchecker, sqlite3, and pgpy.

## Installation

Install the package via pip from PyPI:

```bash
pip install my-little-help
```

## Usage

### String Similarity (rapidfuzz)

```python
import myLittleHelp

# Check if two strings are similar based on a ratio threshold
similar = myLittleHelp.is_similar("apple", "aple", factor=75)
print(similar)  # Returns True or False
```

### Spell Checking (pyspellchecker)

```python
import myLittleHelp

# Verify if a word exists in the dictionary of a specific language
valid_word = myLittleHelp.is_word("hello", lang="en")
print(valid_word)  # Returns True or False
```

### Database Management (sqlite3)

```python
import myLittleHelp

db_path = "storage.db"

# Create a database table
myLittleHelp.create_table(
    table_name="users",
    databasepath=db_path,
    primary_key="id",
    primary_key_format="INTEGER",
    other_keys=["name", "email"],
    key_formats=["TEXT", "TEXT"],
    autoincrement_primary_key=True,
    override_if_exists=False
)

# Insert data into a table
myLittleHelp.insert_to_table(
    table_name="users",
    databasepath=db_path,
    keys=["name", "email"],
    values=[["John Doe"], ["john@example.com"]]
)

# Fetch data from a table
data = myLittleHelp.get_from_database(
    databasepath=db_path,
    value="name",
    table_name="users"
)

# Execute custom SQLite code
results = myLittleHelp.execute_sqlite_code(
    databasepath=db_path,
    code="SELECT * FROM users;"
)
```

### PGP Encryption and Signing (pgpy)

```python
import myLittleHelp

# Generate a new PGP private and public key pair string
private_key, public_key = myLittleHelp.new_keys_pgpy(name="John Doe", email="john@example.com")

# Encrypt text using a public key file path
encrypted_text = myLittleHelp.encode_pgpy(text="Secret Message", pubkey_path="public.asc")

# Decrypt a message file using a private key file path
decrypted_text = myLittleHelp.decode_pgpy(privkey_path="private.asc", message_path="encrypted.asc")

# Sign text using a private key file path
signed_text = myLittleHelp.sign_pgpy(text="Verified Message", privkey_path="private.asc")

# Verify the signature of a message file using a public key file path
is_valid = myLittleHelp.check_sign_pgpy(pubkey_path="public.asc", message_path="signed.asc")
```

### Nostr Integration (nostr-sdk)

```python
import myLittleHelp
import asyncio

# Generate a new Nostr private and public key pair in both Hex and Bech32 formats
keys = myLittleHelp.generate_nostr_keys()
print(keys["private_key_bech32"])  # nsec...
print(keys["public_key_bech32"])   # npub...

# Encrypt a text offline using Nostr NIP-04 encryption
encrypted_content = myLittleHelp.encrypt_with_nostr(
    sender_priv_key="nsec...",
    recipient_pub_key="npub...",
    cleartext="Hello Nostr"
)

# Decrypt a Nostr NIP-04 message offline
cleartext = myLittleHelp.decrypt_with_nostr(
    my_priv_key="nsec...",
    sender_pub_key="npub...",
    encrypted_content=encrypted_content
)

# Send any text (Nostr-encrypted, PGP armor string, or plain text) via Nostr Relays
async def send():
    event_id = await myLittleHelp.send_via_nostr(
        sender_priv_key="nsec...",
        text_content=encrypted_content,
        relays=["wss://relay.damus.io", "wss://nos.lol"]
    )
    print(f"Sent successfully! Event ID: {event_id}")

asyncio.run(send())

# Fetch raw text contents from a specific author via Nostr Relays
async def fetch():
    payloads = await myLittleHelp.fetch_from_nostr(
        author_pub_key="npub...",
        limit=5,
        relays=["wss://relay.damus.io", "wss://nos.lol"]
    )
    print(payloads)  # Returns a list of raw strings

asyncio.run(fetch())

async def fetch_my_mentions():
    messages = await myLittleHelp.fetch_my_nostr_messages(
        my_priv_key="nsec...",
        limit=10,
        relays=["wss://relay.damus.io", "wss://nos.lol"]
    )
    print(messages)

asyncio.run(fetch_my_mentions())
```

## Requirements

* Python 3.13 or higher
* rapidfuzz
* pyspellchecker
* pgpy
* pysqlite3

## License

This project is licensed under the MIT License. For more details, refer to the LICENSE file included in the repository.
