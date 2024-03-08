from rehelper import search_word

# Dictionary to hold the prompts for each RFC, including a general prompt
prompts = {
    "MMJ930128UR6": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "country_of_origin": "str",
            "supplier": "str" // not take IMPORT EXPORT LETTER, 
            "total": "float",
            "items": [
                {
                    "part_number": "str",
                    "description": "str",
                    "quantity": "int",
                    "unit_of_measure": "str",
                    "cost": "float",
                    "weight": "float"
                }
            ]
        }"""
    },
    "EAT930158UR8": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "country_of_origin": "str",
            "supplier": "str",
            "total": "float",
            "items": [
                {
                    "part_number": "str",
                    "description": "str",
                    "quantity": "int",
                    "unit_of_measure": "str",
                    "cost": "float",
                    "weight": "float"
                }
            ]
        }"""
    },
    "GENERAL": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "country_of_origin": "str",
            "supplier": "str",
            "total": "float",
            "items": [
                {
                    "part_number": "str",
                    "description": "str",
                    "quantity": "int",
                    "unit_of_measure": "str",
                    "cost": "float",
                    "weight": "float"
                }
            ]
        }"""
    }
}

def get_prompt(rfc):
    """
    Retrieves the prompt for a given RFC.
    """
    rfc = rfc.upper()  # Ensure RFC is in uppercase for uniformity
    # Return the prompt for the given RFC if it exists, otherwise return the general prompt
    return prompts.get(rfc, prompts["GENERAL"])["Prompt"]

def search_RFC_in_text(text):
    """
    Searches for an RFC in the given text and returns the corresponding prompt if found.
    """
    rfc_list = ["MMJ930128UR6", "EAT930128UR6"]
    for rfc in rfc_list:
        # Check if the RFC is found in the text
        if search_word(text, rfc):
            print(f"RFC {rfc} encontrado")
            return get_prompt(rfc)
    # Return the general prompt if no RFC is found
    print("RFC no encontrado")
    return get_prompt("GENERAL")