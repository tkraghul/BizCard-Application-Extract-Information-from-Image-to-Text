## BizCardX: Extract Business Card Data with OCR

BizCardX is a Streamlit application designed to extract and manage business card information using Optical Character Recognition (OCR) technologies. This project utilizes easyOCR for text extraction and SQLite for database management.
Features

   - Upload and process business card images to extract key information.
   - Extracted data includes company name, card holder name, designation, mobile number, email address, website URL, and address details.
   - Save extracted data and image to a SQLite database.
   - View all saved business cards and delete entries if needed.

## Prerequisites

  -  Python 3.7 or later
-  Streamlit
 -   PIL (Pillow)
 -   easyOCR
 -   sqlite3
 ##   How It Works
-  Database Setup

    create_connection(db_file): Establishes a connection to the SQLite database.
    create_table(conn): Creates a table in the database to store business card details if it does not already exist.
    insert_card(conn, card_data): Inserts a new business card entry into the database.
    fetch_all_cards(conn): Fetches all business card entries from the database.
    delete_card(conn, card_id): Deletes a specific business card entry from the database.

-  OCR Processing

    extract_text_from_image(image): Uses easyOCR to extract text from the uploaded business card image. The extracted data includes company name, card holder name, designation, mobile number, email address, website URL, and address details.

-  Streamlit Application

    File Uploader: Allows users to upload business card images.
    Data Extraction: Displays extracted information after processing the image.
    Save to Database: Saves the extracted data and the image to the SQLite database.
    Display Saved Cards: Lists all saved business cards and allows deletion.
