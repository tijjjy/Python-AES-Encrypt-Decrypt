from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from hashlib import pbkdf2_hmac
import os
import getpass
import argparse
from Crypto.Random import get_random_bytes

# PROMPT FOR PASSWORD
def prompt_password(salt=None):

    # GET PASSWORD
    password = getpass.getpass("Enter your password: ")

    # GET SALT
    if not salt:
        salt = get_random_bytes(16)

    # GENERATE KEY
    key = pbkdf2_hmac("sha256", password.encode(), salt, 100000, dklen=32)
    return [key, salt]

password = ""

def encrypt_file(input_file, output_file, key, salt):

    # GENERATE SALT AND IV
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # READ FILE
    with open(input_file, 'rb') as file:
        plaintext = file.read()

    # ENCRYPT FILE
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    with open(output_file, 'wb') as file:
        file.write(salt + iv + ciphertext)
    
    # REMOVE INPUT FILE IF SET
    if args.remove and os.path.isfile(output_file):
        os.remove(input_file)

def decrypt_file(input_file, output_file):
    global password

    # GET SALT, IV, AND CIPHERTEXT FROM FILE
    with open(input_file, 'rb') as file:
        salt = file.read(16)
        iv = file.read(16)
        ciphertext = file.read()

    # PROMPT FOR PASSWORD IF NOT PROVIDED
    if not password:
        password = prompt_password(salt)

    # DECRYPT FILE
    key = password[0]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    # WRITE DECRYPTED FILE
    with open(output_file, 'wb') as file:
        file.write(plaintext)
    
    # REMOVE INPUT FILE IF SET
    if args.remove and os.path.isfile(output_file):
        os.remove(input_file)

if __name__ == '__main__':
    
    # PARSE ARGUMENTS
    parser = argparse.ArgumentParser(description='Encrypt and Decrypt files using a password and AES')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input file or directory')
    parser.add_argument('-o', '--output', type=str, help='Output file or directory')
    parser.add_argument('-e', '--encrypt', action='store_true', help='Encrypt the input file')
    parser.add_argument('-d', '--decrypt', action='store_true', help='Decrypt the input file')
    parser.add_argument('-x', '--extension', type=str, default="enc", help='Extension to add to encrypted files')
    parser.add_argument('-r', '--remove', action='store_true', help='Remove the input file after encryption or decryption')
    args = parser.parse_args()

    # CHECK IF ENCRYPT OR DECRYPT IS SET
    if not args.encrypt and not args.decrypt:
        print("Please specify whether you want to encrypt or decrypt the input file")
        exit(1)

    # CHECK IF ENCRYPT AND DECRYPT ARE SET
    if args.encrypt and args.decrypt:
        print("Please specify either to encrypt or decrypt the input file, not both")
        exit(1)

    # GET INPUT AND OUTPUT PATHS
    if args.input:
        if os.path.exists(args.input):
            inputPath = args.input
        else:
            print("Input file or directory does not exist")
            exit(1)
    # IF INPUT IS NOT SET
    elif not args.input:
        print("Please specify an input file or directory")
        exit(1)
    if args.output:
        outputPath = args.output

    args.extension = "." + args.extension

    # IF ENCRYPT IS SET
    if args.encrypt:
        # PROMPT FOR PASSWORD
        key = prompt_password()

        # IF INPUT IS A DIRECTORY
        if os.path.isdir(inputPath):
            # GET ALL FILES IN DIRECTORY
            files = [os.path.join(inputPath, f) for f in os.listdir(inputPath) if os.path.isfile(os.path.join(inputPath, f))]
            # ENCRYPT EACH FILE
            for file in files:
                # SKIP IF FILE IS ALREADY ENCRYPTED
                if file.endswith(args.extension):
                    continue
                # ENCRYPT FILE
                if args.output:
                    if not os.path.exists(outputPath):
                        os.mkdir(outputPath)
                    encrypt_file(file, outputPath + "/" + os.path.basename(file) + args.extension, key[0], key[1])
                else:
                    encrypt_file(file, file + args.extension, key[0], key[1])
        # IF INPUT IS A FILE
        if os.path.isfile(inputPath):
            # ENCRYPT FILE
            if args.output:
                encrypt_file(inputPath, outputPath + args.extension, key[0], key[1])
            else:
                encrypt_file(inputPath, inputPath + args.extension, key[0], key[1])

    # IF DECRYPT IS SET
    if args.decrypt:
        # IF INPUT IS A DIRECTORY
        if os.path.isdir(inputPath):
            # GET ALL FILES IN DIRECTORY
            files = [os.path.join(inputPath, f) for f in os.listdir(inputPath) if os.path.isfile(os.path.join(inputPath, f))]
            # DECRYPT EACH FILE
            for file in files:
                # SKIP IF FILE IS NOT ENCRYPTED
                if not file.endswith(args.extension):
                    continue
                # DECRYPT FILE
                if args.output:
                    if not os.path.exists(outputPath):
                        os.mkdir(outputPath)
                    decrypt_file(file, outputPath + "/" + os.path.basename(file[:-len(args.extension)]))
                else:
                    # REMOVE EXTENSION FROM FILE NAME and the dot
                    decrypt_file(file, file[:-len(args.extension)])
        # IF INPUT IS A FILE
        if os.path.isfile(inputPath):
            # IF OUTPUT IS SET
            if args.output:
                decrypt_file(inputPath, outputPath)
            else:
                decrypt_file(inputPath, inputPath[:-len(args.extension)])