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

def encode_pgpy(text: str, pubkey: str) -> str:
    public_key, *_ = pubkey
    message = pgpy.PGPMessage.new(text)
    encrypted_message = public_key.encrypt(message)

    return str(encrypted_message)

def decode_pgpy(privkey_path: str, message: str) -> str:
    private_key, _ = pgpy.PGPKey.from_file(privkey_path)
    encrypted_message = message
    decrypted_message = private_key.decrypt(encrypted_message)

    return str(decrypted_message)

def sign_pgpy(text: str ,privkey_path: str) -> str:
    private_key, _ = pgpy.PGPKey.from_file(privkey_path)
    message = pgpy.PGPMessage.new(text)
    message |= private_key.sign(message)

    return str(message)

def check_sign_pgpy(pubkey: str, message: str) -> bool:
    public_key, _ = pubkey
    file_text = message

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
#---------------threading---------------#

import threading

def new_thread(function: function) -> None:
    tread = threading.Thread(function)
    tread.start()
    
#---------------threading---------------#
#-----------------emails----------------#

import smtplib
import imaplib
import email
from email.message import EmailMessage
from email.policy import default

def send_email(smtp_server, port, sender_email, password, receiver_email, subject, text):

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(text)

    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(sender_email, password)
        server.send_message(msg)

def receive_emails(imap_server, port, email_user, password, folder="INBOX", search_criteria="UNSEEN"):
    emails_list = []
    
    with imaplib.IMAP4_SSL(imap_server, port) as mail:
        mail.login(email_user, password)
        mail.select(folder)
        status, response_data = mail.search(None, search_criteria)
        mail_ids = response_data[0].split()
        
        for mail_id in mail_ids:
            status, data = mail.fetch(mail_id, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email, policy=default)
            body_content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body_content = part.get_content()
                        break
            else:
                body_content = msg.get_content()
            emails_list.append({
                "id": mail_id.decode(),
                "from": msg["From"],
                "subject": msg["Subject"],
                "body": body_content.strip()
            })
            
    return emails_list

#-----------------emails----------------#