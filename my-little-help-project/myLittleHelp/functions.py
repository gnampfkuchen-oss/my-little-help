from rapidfuzz import fuzz

def is_similar(first: str, second:str, factor: int = 75) -> bool:
    if fuzz.ratio(first, second) >= factor:
        return True
    return False

#---------------rapidfuzz---------------#
#-------------pyspellchecker------------#

from spellchecker import SpellChecker

def is_word(word: str, lang: str) -> bool:
    spell = SpellChecker(language=lang)
    if word in spell:
        return True
    return False

#-------------pyspellchecker------------#
#---------------pysqlite3---------------#

import sqlite3

def get_from_database(databasepath:str, value: str, table_name: str) -> str:
    database = sqlite3.connect(databasepath)
    cursor = database.cursor()
    cursor.execute(f'SELECT {value} FROM {table_name};')
    result = cursor.fetchone()
    return result

def create_table(
        table_name: str, 
        databasepath: str, 
        primary_key: str, 
        primary_key_format: str, 
        other_keys: list , 
        key_formats:list, 
        autoincrement_primary_key: bool = True, 
        override_if_exists: bool = False
        ) -> None:
    
    override = " IF NOT EXISTS "
    autoincrement = " AUTOINCREMENT"
    database = sqlite3.connect(databasepath)
    cursor = database.cursor()
    if override_if_exists:
        override = " "
    if not autoincrement_primary_key:
        autoincrement = ""
    other = []
    for key in other_keys:
        other.append(",")
        other.append(key)
        other.append(key_formats[other_keys.index(key)].upper())
    other = " ".join(other)
    cursor.execute(f'CREATE TABLE{override}{table_name} ({primary_key} {primary_key_format.upper()} PRIMARY KEY{autoincrement} {other});')
    database.commit()

def insert_to_table(
        table_name: str, 
        databasepath: str,
        keys: list,
        values: list,
        ) -> None:
    database = sqlite3.connect(databasepath)
    cursor = database.cursor()
    keystr = ",".join(keys)
    value = values
    for val in value:
        val.insert(0, '"')
        val.insert(-1, '"')
    value = ",".join(value)
    cursor.execute(f'INSERT INTO {table_name} ({keystr}) VALUES ({value});')
    database.commit()

def execute_sqlite_code(databasepath: str, code: str):
    database = sqlite3.connect(databasepath)
    cursor = database.cursor()
    cursor.execute(code)
    if code.startswith("SELECT"):
        x = cursor.fetchall()
        return x
    else:
        database.commit()
    return None

#---------------pysqlite3---------------#
#------------------pgpy-----------------#

import pgpy
from pgpy.constants import KeyFlags

def new_keys_pgpy(name: str, email: str) -> tuple[str, str]:
    key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = pgpy.PGPUID.new(name, email=email)
    key.add_uid(uid)
    key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage})

    return str(key), str(key.pubkey)

def encode_pgpy(text: str, pubkey_path: str) -> str:
    public_key, _ = pgpy.PGPKey.from_file(pubkey_path)
    message = pgpy.PGPMessage.new(text)
    encrypted_message = public_key.encrypt(message)

    return str(encrypted_message)

def decode_pgpy(privkey_path: str, message_path: str) -> str:
    private_key, _ = pgpy.PGPKey.from_file(privkey_path)
    encrypted_message = pgpy.PGPMessage.from_file(message_path)
    decrypted_message = private_key.decrypt(encrypted_message)

    return str(decrypted_message)

def sign_pgpy(text: str ,privkey_path: str) -> str:
    private_key, _ = pgpy.PGPKey.from_file(privkey_path)
    message = pgpy.PGPMessage.new(text)
    message |= private_key.sign(message)

    return str(message)

def check_sign_pgpy(pubkey_path: str, message_path: str) -> bool:
    public_key, _ = pgpy.PGPKey.from_file(pubkey_path)
    with open(message_path, 'r', encoding='utf-8') as f:
        file_text = f.read()

    try:
        signature = pgpy.PGPSignature.from_blob(file_text)
        lines = file_text.splitlines()
        content_lines = []
        in_content = False
        
        for line in lines:
            if "-----BEGIN PGP SIGNED MESSAGE-----" in line:
                continue
            if "Hash:" in line:
                in_content = True
                continue
            if "-----BEGIN PGP SIGNATURE-----" in line:
                break
            if in_content:
                content_lines.append(line)
        if content_lines and content_lines[0] == "":
            content_lines.pop(0)
            
        klartext = "\n".join(content_lines)

        public_key.verify(klartext, signature)
        return True
    except Exception as e:
        pass
    return False

#------------------pgpy-----------------#
#---------------nostr-sdk---------------#

from nostr_sdk import Keys, PublicKey, nip04_encrypt, nip04_decrypt, Client, EventBuilder, Filter

def generate_nostr_keys() -> dict:
    keys = Keys.generate()
    
    return {
        "private_key_hex": keys.secret_key().to_hex(),
        "public_key_hex": keys.public_key().to_hex(),
        "private_key_bech32": keys.secret_key().to_bech32(),
        "public_key_bech32": keys.public_key().to_bech32()
    }

def encrypt_with_nostr(sender_priv_key: str, recipient_pub_key: str, cleartext: str) -> str:
    sender_keys = Keys.parse(sender_priv_key)
    recipient_keys = PublicKey.parse(recipient_pub_key)
    
    return nip04_encrypt(sender_keys.secret_key(), recipient_keys, cleartext)

def decrypt_with_nostr(my_priv_key: str, sender_pub_key: str, encrypted_content: str) -> str:
    my_keys = Keys.parse(my_priv_key)
    sender_keys = PublicKey.parse(sender_pub_key)
    
    return nip04_decrypt(my_keys.secret_key(), sender_keys, encrypted_content)

async def send_via_nostr(sender_priv_key: str, text_content: str, relays: list[str] = None) -> str:
    if relays is None:
        relays = ["wss://relay.damus.io", "wss://nos.lol"]
        
    keys = Keys.parse(sender_priv_key)
    client = Client(keys)
    
    for relay in relays:
        await client.add_relay(relay)
    await client.connect()
    
    event = EventBuilder.text_note(text_content, []).to_event(keys)
    output = await client.send_event(event)
    
    await client.disconnect()
    return output.id.to_hex()

async def fetch_from_nostr(author_pub_key: str, limit: int = 10, relays: list[str] = None) -> list[str]:
    if relays is None:
        relays = ["wss://relay.damus.io", "wss://nos.lol"]
        
    tmp_client = Client(Keys.generate())
    
    for relay in relays:
        await tmp_client.add_relay(relay)
    await tmp_client.connect()
    
    author_pub = PublicKey.parse(author_pub_key)
    filter_obj = Filter().kind(1).author(author_pub).limit(limit)
    
    events = await tmp_client.fetch_events([filter_obj], None)
    await tmp_client.disconnect()
    
    return [event.content() for event in events]

async def fetch_my_nostr_messages(my_priv_key: str, limit: int = 10, relays: list[str] = None) -> list[str]:
    if relays is None:
        relays = ["wss://relay.damus.io", "wss://nos.lol"]
        
    keys = Keys.parse(my_priv_key)
    client = Client(keys)
    
    for relay in relays:
        await client.add_relay(relay)
    await client.connect()
    
    filter_obj = Filter().kind(1).pubkey(keys.public_key()).limit(limit)
    events = await client.fetch_events([filter_obj], None)
    
    await client.disconnect()
    return [event.content() for event in events]



#---------------nostr-sdk---------------#
#---------------threading---------------#

import threading

def new_thread(function: function) -> None:
    tread = threading.Thread(function)
    tread.start()
    
#---------------threading---------------#
    



