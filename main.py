import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import multiprocessing
from symspellpy import SymSpell, Verbosity
import os

st.set_page_config(page_title='VisualHealth', page_icon='👁️‍🗨️', layout="centered", menu_items=None)

@st.dialog('INTEGRITY WARNING')
def warning():
    st.write('''
            THE TOOL IS STILL UNDER DEVELOPMENT! \n
            IT MAY PRODUCE INACCURATE DATA! \n  
            PLEASE DO NOT FULLY DEPEND ON THE TOOL AND ONLY USE IT AS A SUPPLEMENT!
            ''')
warning() 

def initialize_symspell():
    max_edit_distance_dictionary = 2
    prefix_length = 7
    sym_spell = SymSpell(max_edit_distance_dictionary, prefix_length)

    # Load a frequency dictionary for text correction
    dictionary_path = os.path.join("frequency_dictionary_en_82_765.txt")  # Ensure you have this file
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

    # Load a bigram dictionary for context-aware correction
    bigram_path = os.path.join("frequency_bigramdictionary_en_243_342.txt")  # Ensure you have this file
    sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

    return sym_spell

def correct_text_with_symspell(sym_spell, text):
    suggestions = sym_spell.lookup_compound(text, max_edit_distance=2)
    return suggestions[0].term if suggestions else text

# Check for haram ingredients
def check_haram(ingredients, haram_list):
    found_haram = [item for item in haram_list if item.lower() in ingredients.lower()]
    return found_haram

# Check for unhealthy ingredients
def check_unhealthy(ingredients, unhealthy_list):
    found_unhealthy = [item for item in unhealthy_list if item.lower() in ingredients.lower()]
    return found_unhealthy

def main():
    st.title("Ingredients Analyzer")

    # Upload image
    uploaded_file = st.file_uploader("Upload an image of an ingredient label")

    if uploaded_file:
        try:
            # Load and display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

            # Convert the PIL image to a numpy array
            image_np = np.array(image)

            # Create EasyOCR reader object
            reader = easyocr.Reader(['en'])

            # Perform OCR on the image
            result = reader.readtext(image_np)

            if result:
                # Extract text from the OCR result
                extracted_text = " ".join([text[1] for text in result])

                # Display the raw extracted text
                st.subheader("Extracted Text:")
                st.text(extracted_text)

                # Correct the extracted text using SymSpell
                sym_spell = initialize_symspell()
                corrected_text = correct_text_with_symspell(sym_spell, extracted_text)

                # Display the corrected text
                st.subheader("Corrected Text:")
                st.text(corrected_text)

                # Lists of haram and unhealthy ingredients
                haram_list = [
                    # Animal-based ingredients
                    "pork", "pig", "boar", "hog", "gelatin", "lard", "bacon", "ham", "sow", "swine",
                    "enzymes from non-halal sources", "rennet from non-halal sources",
                    "lipase", "pepsin", "carmine", "cochineal",
                    "meat broth from non-halal sources", "animal fat from non-halal sources",
                    
                    # Alcohol and derivatives
                    "alcohol", "ethanol", "beer", "wine", "rum", "brandy",
                    "vodka", "gin", "whiskey", "bourbon", "liqueur", "ethanol-based flavoring",
                    
                    # Miscellaneous
                    "vanilla extract with alcohol", "natural flavors containing alcohol",
                    "wine vinegar", "balsamic vinegar with alcohol", "fermented fruit juice",
                    "glycerin from non-halal sources", "lecithin from non-halal sources",
                    "mono and diglycerides from non-halal sources",
                    
                    # Pig derivatives
                    "pig fat", "pig skin", "pig byproducts",
                    "oleic acid from non-halal sources",
                    
                    # Blood and related products
                    "blood", "blood plasma",
                    
                    # Miscellaneous derivatives
                    "casein from non-halal sources", "hydrolyzed animal protein"
                ]

                unhealthy_list = [
                    # Sweeteners and sugars
                    "high fructose corn syrup", "corn syrup", "maltodextrin", "refined sugar",
                    "artificial sweeteners", "aspartame", "sucralose", "saccharin",
                    "acesulfame k", "cyclamate",
                    
                    # Fats and oils
                    "trans fats", "partially hydrogenated oils", "fully hydrogenated oils",
                    "palm oil", "interesterified fats", "vegetable shortening",
                    
                    # Preservatives
                    "sodium benzoate", "potassium sorbate", "calcium propionate",
                    "butylated hydroxyanisole", "bha", "butylated hydroxytoluene", "bht",
                    "tert-butylhydroquinone", "tbhq", "propyl gallate",
                    
                    # Additives
                    "monosodium glutamate", "msg", "yeast extract", "autolyzed yeast extract",
                    "artificial flavoring", "artificial food coloring",
                    "caramel coloring", "red 40", "yellow 5", "yellow 6", "blue 1",
                    "sodium phosphate", "calcium disodium edta",
                    
                    # Nitrates and nitrites
                    "sodium nitrate", "sodium nitrite", "potassium nitrate", "nitrate", "nitrite",
                    
                    # Brominated compounds
                    "potassium bromate", "brominated vegetable oil", "bvo",
                    
                    # Emulsifiers and stabilizers
                    "polysorbate 80", "carrageenan", "propylene glycol",
                    "xanthan gum", "guar gum",
                    
                    # Other unhealthy compounds
                    "sulfites", "sulfur dioxide", "benzoates",
                    "phosphoric acid", "aluminum compounds", "hydrolyzed vegetable protein",
                    "dextrose", "propylene glycol alginate", "silicon dioxide",
                    "nitrates", "modified starch"
                ]


                # Analyze ingredients
                haram_found = check_haram(corrected_text, haram_list)
                unhealthy_found = check_unhealthy(corrected_text, unhealthy_list)

                # Display results
                st.subheader("Analysis Results:")
                if haram_found:
                    st.error(f"Haram Ingredients Detected: {', '.join(haram_found)}")
                else:
                    st.success("No haram ingredients detected. The product appears to be halal.")

                if unhealthy_found:
                    st.warning(f"Unhealthy Ingredients Detected: {', '.join(unhealthy_found)}")
                else:
                    st.info("No unhealthy ingredients detected. The product appears to be healthy.")
            else:
                st.warning("No text detected from the image. Please try again with a clearer image.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Ensure multiprocessing safety
    multiprocessing.freeze_support()  # This is needed for Windows
    main()
