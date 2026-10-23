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
private_key, public_key = myLittleHelp.new_keys(name="John Doe", email="john@example.com")

# Encrypt text using a public key file path
encrypted_text = myLittleHelp.encode(text="Secret Message", pubkey_path="public.key")

# Decrypt a message file using a private key file path
decrypted_text = myLittleHelp.decode(privkey_path="private.key", message_path="encrypted.msg")

# Sign text using a private key file path
signed_text = myLittleHelp.sign(text="Verified Message", privkey_path="private.key")

# Verify the signature of a message file using a public key file path
is_valid = myLittleHelp.check_sign(pubkey_path="public.key", message_path="signed.msg")
```

## Requirements

* Python 3.13 or higher
* rapidfuzz
* pyspellchecker
* pgpy
* pysqlite3

## License

This project is licensed under the MIT License. For more details, refer to the LICENSE file included in the repository.
