
import re 
import regex
def validRFC(rfc):
        valid = re.compile(r'^[A-Z&Ñ]{3,4}[0-9]{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])[A-Z0-9]{2}[0-9A]$')
        return valid.match(rfc)
def searchRFC(rfc):
        pattern = regex.compile(r'^[A-Z&Ñ]{3,4}[0-9]{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])[A-Z0-9]{2}[0-9A]$', re.IGNORECASE|re.M)
        return regex.search(pattern,rfc)

def validate_rfc(word):
    if validRFC(word):
        return word
    
    
def extract_rfc(text):
    rfclist=map(validate_rfc ,text.split())
    rfclist=list(filter(None,rfclist))
    rfclist=list(set(rfclist))
    return rfclist

def search_word(text, word):
    # Using \b to define whole word boundaries
    # and re.IGNORECASE to ignore case sensitivity
    # The expression (?:(?<=\S)\S*|\b) before and after the word
    # allows handling cases where the text is joined together without spaces
    pattern = r"(?:(?<=\S)\S*|\b){}(?=\S*\S(?=\S)|\b)".format(re.escape(word))
    return re.findall(pattern, text, re.IGNORECASE)
