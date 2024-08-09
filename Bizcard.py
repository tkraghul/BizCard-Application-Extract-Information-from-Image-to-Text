import streamlit as st
from PIL import Image
import easyocr
import sqlite3
import os

# Database setup
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    sql_create_cards_table = """
    CREATE TABLE IF NOT EXISTS business_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        card_holder_name TEXT,
        designation TEXT,
        mobile_number TEXT,
        email_address TEXT,
        website_url TEXT,
        area TEXT,
        city TEXT,
        state TEXT,
        pin_code TEXT,
        card_image BLOB
    );
    """
    try:
        c = conn.cursor()
        c.execute(sql_create_cards_table)
    except sqlite3.Error as e:
        print(e)

def insert_card(conn, card_data):
    sql = '''
    INSERT INTO business_cards(
        company_name, card_holder_name, designation,
        mobile_number, email_address, website_url,
        area, city, state, pin_code, card_image
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cur = conn.cursor()
    cur.execute(sql, card_data)
    conn.commit()
    return cur.lastrowid

def fetch_all_cards(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM business_cards")
    rows = cur.fetchall()
    return rows

def delete_card(conn, card_id):
    sql = 'DELETE FROM business_cards WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (card_id,))
    conn.commit()

# OCR setup
def extract_text_from_image(image):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    extracted_data = {
        'company_name': '',
        'card_holder_name': '',
        'designation': '',
        'mobile_number': '',
        'email_address': '',
        'website_url': '',
        'area': '',
        'city': '',
        'state': '',
        'pin_code': ''
    }

    for detection in result:
        text = detection[1]

        # Extract email address
        if "@" in text:
            extracted_data['email_address'] = text

        # Extract mobile number (Assume it's a 10-digit number)
        elif text.replace(" ", "").isdigit() and len(text.replace(" ", "")) >= 10:
            extracted_data['mobile_number'] = text

        # Extract website URL (a basic check for "www." or ".com")
        elif "www." in text or ".com" in text or ".net" in text or ".org" in text:
            extracted_data['website_url'] = text

        # Extract pin code (Assume it's a 6-digit number)
        elif text.replace(" ", "").isdigit() and len(text.replace(" ", "")) == 6:
            extracted_data['pin_code'] = text

        # Extract designation (this is harder, so assume it's a word followed by "Manager", "Engineer", etc.)
        elif any(job_title in text.lower() for job_title in ["manager", "engineer", "director", "developer", "designer"]):
            extracted_data['designation'] = text

        # For simplicity, assume the first text as company name if not identified
        if extracted_data['company_name'] == '':
            extracted_data['company_name'] = text

        # Assume the next line is the card holder name after company name is detected
        elif extracted_data['card_holder_name'] == '':
            extracted_data['card_holder_name'] = text

        # Address extraction (basic assumption based on the structure)
        elif extracted_data['area'] == '':
            extracted_data['area'] = text
        elif extracted_data['city'] == '':
            extracted_data['city'] = text
        elif extracted_data['state'] == '':
            extracted_data['state'] = text

    return extracted_data

# Main Streamlit application
def main():
    st.title("BizCardX: Extract Business Card Data with OCR")

    # Set up the database connection
    conn = create_connection("business_cards.db")
    create_table(conn)

    # Create a directory to save uploaded images
    if not os.path.exists("business_cards"):
        os.makedirs("business_cards")

    # File uploader widget
    uploaded_file = st.file_uploader("Upload a Business Card", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Save the uploaded image
        image = Image.open(uploaded_file)
        image_path = os.path.join("business_cards", uploaded_file.name)
        image.save(image_path)

        # OCR Processing
        with st.spinner('Extracting data...'):
            extracted_data = extract_text_from_image(image_path)

        # Display extracted data
        st.write("Extracted Information:")
        for key, value in extracted_data.items():
            st.write(f"{key.replace('_', ' ').title()}: {value}")

        # Insert into database
        if st.button("Save to Database"):
            with open(image_path, 'rb') as f:
                image_blob = f.read()
            card_data = (
                extracted_data.get('company_name', ''),
                extracted_data.get('card_holder_name', ''),
                extracted_data.get('designation', ''),
                extracted_data.get('mobile_number', ''),
                extracted_data.get('email_address', ''),
                extracted_data.get('website_url', ''),
                extracted_data.get('area', ''),
                extracted_data.get('city', ''),
                extracted_data.get('state', ''),
                extracted_data.get('pin_code', ''),
                image_blob
            )
            insert_card(conn, card_data)
            st.success("Card information saved successfully!")

    # Display all cards
    st.subheader("Saved Business Cards")
    cards = fetch_all_cards(conn)
    for card in cards:
        st.write(f"Card ID: {card[0]}")
        st.write(f"Company Name: {card[1]}")
        st.write(f"Card Holder Name: {card[2]}")
        st.write(f"Designation: {card[3]}")
        st.write(f"Mobile Number: {card[4]}")
        st.write(f"Email Address: {card[5]}")
        st.write(f"Website URL: {card[6]}")
        st.write(f"Area: {card[7]}")
        st.write(f"City: {card[8]}")
        st.write(f"State: {card[9]}")
        st.write(f"Pin Code: {card[10]}")
        if st.button("Delete", key=f"delete_{card[0]}"):
            delete_card(conn, card[0])
            st.experimental_rerun()

if __name__ == "__main__":
    main()
