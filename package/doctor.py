
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
    
class Doctors(Resource):
    """This contain apis to carry out activity with all doctors"""

    def get(self):
        """Retrive list of all the doctor"""

        doctors = conn.execute("SELECT * FROM doctor ORDER BY doc_date DESC").fetchall()
        return doctors



    def post(self):
        """Add the new doctor"""

        doctorInput = request.get_json(force=True)
        doc_first_name=doctorInput['doc_first_name']
        doc_last_name = doctorInput['doc_last_name']
        doc_ph_no = doctorInput['doc_ph_no']
        doc_address = doctorInput['doc_address']
        doctorInput['doc_id']=conn.execute('''INSERT INTO doctor(doc_first_name,doc_last_name,doc_ph_no,doc_address)
            VALUES(?,?,?,?)''', (doc_first_name, doc_last_name,doc_ph_no,doc_address)).lastrowid
        conn.commit()
        return doctorInput

class Doctor(Resource):
    """It include all the apis carrying out the activity with the single doctor"""


    def get(self,id):
        """get the details of the docktor by the doctor id"""

        doctor = conn.execute("SELECT * FROM doctor WHERE doc_id=?",(id,)).fetchall()
        return doctor

    def delete(self, id):
        """Delete the doctor by its id"""

        conn.execute("DELETE FROM doctor WHERE doc_id=?", (id,))
        conn.commit()
        return {'msg': 'sucessfully deleted'}

    def put(self,id):
        """Update the doctor by its id"""

        doctorInput = request.get_json(force=True)
        doc_first_name=doctorInput['doc_first_name']
        doc_last_name = doctorInput['doc_last_name']
        doc_ph_no = doctorInput['doc_ph_no']
        doc_address = doctorInput['doc_address']
        conn.execute(
            "UPDATE doctor SET doc_first_name=?,doc_last_name=?,doc_ph_no=?,doc_address=? WHERE doc_id=?",
            (doc_first_name, doc_last_name, doc_ph_no, doc_address, id))
        conn.commit()
        return doctorInput
