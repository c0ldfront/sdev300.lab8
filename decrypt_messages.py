import base64

# like always morse code, i noticed this one based on my job in the military,
# which was field radio operator so i had to deal with cw keys, and morse code,
# only as a hobby seeing we don't use it that much anymore everything is
# digital.
# Chart : http://rumkin.com/tools/cipher/morse.php
morse_code = '- .... .. ... / ... -.. . ...- / ...-- ----- ----- / -.-. .-.. .- ... ... / .... .- ... / ... --- -- . / ... - .-. .- -. --. . / .-. . --.- ..- . ... - ... .-.-.-'

morse_table: dict = {
    # Letters
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
    # Numbers
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    # Punctuation
    "&": ".-...",
    "'": ".----.",
    "@": ".--.-.",
    ")": "-.--.-",
    "(": "-.--.",
    ":": "---...",
    ",": "--..--",
    "=": "-...-",
    "!": "-.-.--",
    ".": ".-.-.-",
    "-": "-....-",
    "+": ".-.-.",
    '"': ".-..-.",
    "?": "..--..",
    "/": "-..-.",
    # morse coding for spaces
    " ": "/",
    }


# https://morsecode.world/international/translator.html
# https://www.tutorialspoint.com/morse-code-translator-in-python
def morse_code_decrypt(message):
    message += ' '
    decipher = ''
    mycitext = ''
    for myletter in message:
        # checks for space
        if myletter != ' ':
            # cursor indexing for keeping track of where we are
            i = 0
            # just append the current letter to mycitext
            mycitext += myletter
        else:
            # increment are cursor.
            i += 1
            if i == 2:
                decipher += ' '
            else:
                # we can easily pull the conversion by getting the index and
                # looking it up in the dict, if found we append the decipher.
                decipher += list(morse_table.keys())[
                    list(morse_table.values()).index(mycitext)]
                # blank out cittext so we know we start fresh.
                mycitext = ''
    return decipher


print(morse_code_decrypt(morse_code))
# base64 is widely used in programming, i have used it for encoding image
# files down to base64 binary text of the ascii table. I used this data in
# a mmo game delivering images to clients, where the client would
# decode the base64 image and encode it back into readable image format
# that the game client can understand.
# this made it easy for us to store images we wanted updated via the server,
# rather than sending over a binary data file we just passed off the binary
# text.
# output: b'So this is base64. Now I know.'
base64_encoded = 'U28gdGhpcyBpcyBiYXNlNjQuIE5vdyBJIGtub3cu'
data = base64.b64decode(base64_encoded)
print(data)

# Caesarian Shift N12
# caesars crypto, seeing I am a history buff I thought i say this one before,
# i just figured out the shift_amount key bassed off of the algo that loops
# over the range of 14 and if we notice from the output. the shift key amount
# is 12. thus, giving us the output of.
# --- Begin Key ---- I am so clever. No one could possibly figure this out.
# --- End Key ---
# http://www.cs.trincoll.edu/~crypto/historical/caesar.html
# https://cryptii.com/pipes/caesar-cipher
# https://www.tutorialspoint.com/cryptography_with_python/cryptography_with_python_caesar_cipher.htm
# https://www.101computing.net/caesar-shift-decoder/
case_shift = ' - -- Psuwb Ysm - --- W oa gc qzsjsf.Bc cbs qcizr ' \
             'dcggwpzm twuifs hvwg cih. - -- Sbr Ysm - --'


def decrypt(text, shift_amount):
    decrypted_message = ''
    for s in text:
        if s.isalpha():
            num = ord(s)
            num += shift_amount
            if s.isupper():
                if num > ord('Z'):
                    num -= 26
                elif num < ord('A'):
                    num += 26
            elif s.islower():
                if num > ord('z'):
                    num -= 26
                elif num < ord('a'):
                    num += 26
            decrypted_message += chr(num)
        else:
            decrypted_message += s
    return decrypted_message


for num in range(14):
    print(decrypt(case_shift, num))
