
import sqlite3
from flask_restful import Resource, Api, request
from package.model import conn
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def aesencrypt( key, raw ):
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))

def aesdecrypt(enc ):
    key = "encaes"
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))

class Patients(Resource):
    """It contain all the api carryign the activity with aand specific patient"""
   
    def get(self):
        """Api to retive all the patient from the database"""
        cursor = conn.cursor()
        conn.create_function("aesdecrypt", 1, aesdecrypt)
        #patients = conn.execute("SELECT aesdecrypt( pat_ph_no ) FROM patient  ORDER BY pat_date DESC").fetchall()
       
        patients = cursor.execute("SELECT pat_first_name,pat_last_name,pat_disease_name,aesdecrypt(pat_ph_no) as pat_ph_no,pat_address FROM patient  ORDER BY pat_date DESC").fetchall()
        print(patients)
        return patients



    def post(self):
        """api to add the patient in the database"""

        patientInput = request.get_json(force=True)
        pat_first_name=patientInput['pat_first_name']
        pat_last_name = patientInput['pat_last_name']
        pat_disease_name = patientInput['pat_disease_name']
        pat_ph_no1 = aesencrypt("encaes",patientInput['pat_ph_no'])
        pat_ph_no2 = aesdecrypt("encaes",pat_ph_no1)
        print(pat_ph_no2)
        pat_ph_no = patientInput['pat_ph_no']
        pat_address = patientInput['pat_address']
        cursor = conn.cursor()
        conn.create_function("aesencrypt", 2, aesencrypt)
        patientInput['pat_id']=cursor.execute('''INSERT INTO patient(pat_first_name,pat_last_name,pat_disease_name,pat_ph_no,pat_address)
            VALUES(?,?,?,?,?)''', (pat_first_name, pat_last_name, pat_disease_name,aesencrypt("encaes", pat_ph_no),aesencrypt("encaes", pat_address))).lastrowid
        conn.commit()
        return patientInput

class Patient(Resource):
    """It contains all apis doing activity with the single patient entity"""

    def get(self,id):
        """api to retrive details of the patient by it id"""

        patient = conn.execute("SELECT * FROM patient WHERE pat_id=?",(id,)).fetchall()
        return patient

    def delete(self,id):
        """api to delete the patiend by its id"""

        conn.execute("DELETE FROM patient WHERE pat_id=?",(id,))
        conn.commit()
        return {'msg': 'sucessfully deleted'}

    def put(self,id):
        """api to update the patient by it id"""

        patientInput = request.get_json(force=True)
        pat_first_name = patientInput['pat_first_name']
        pat_last_name = patientInput['pat_last_name']
        pat_disease_name = patientInput['pat_disease_name']
        pat_ph_no = patientInput['pat_ph_no']
        pat_address = patientInput['pat_address']
        cursor = conn.cursor()
        conn.create_function("aesencrypt", 2, aesencrypt)
        cursor.execute("UPDATE patient SET pat_first_name=?,pat_last_name=?,pat_disease_name=?,pat_ph_no=?,pat_address=? WHERE pat_id=?",
                     (pat_first_name, pat_last_name, pat_disease_name,aesencrypt("encaes", pat_ph_no),aesencrypt("encaes", pat_address),id))
        conn.commit()
        return patientInput