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

def new_keys(name: str, email: str) -> tuple[str, str]:
    key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = pgpy.PGPUID.new(name, email=email)
    key.add_uid(uid)
    key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage})

    return str(key), str(key.pubkey)

def encode(text: str, pubkey_path: str) -> str:
    public_key, _ = pgpy.PGPKey.from_file(pubkey_path)
    message = pgpy.PGPMessage.new(text)
    encrypted_message = public_key.encrypt(message)

    return str(encrypted_message)

def decode(privkey_path: str, message_path: str) -> str:
    private_key, _ = pgpy.PGPKey.from_file(privkey_path)
    encrypted_message = pgpy.PGPMessage.from_file(message_path)
    decrypted_message = private_key.decrypt(encrypted_message)

    return str(decrypted_message)

def sign(text: str ,privkey_path: str) -> str:
    private_key, _ = pgpy.PGPKey.from_file(privkey_path)
    message = pgpy.PGPMessage.new(text)
    message |= private_key.sign(message)

    return str(message)

def check_sign(pubkey_path: str, message_path: str) -> bool:
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