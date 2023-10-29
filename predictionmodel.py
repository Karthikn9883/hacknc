import firebase_admin
from firebase_admin import credentials, firestore, storage
from PIL import Image, ImageDraw, ImageFont
import io

# Initialize Firebase
cred = credentials.Certificate('app.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'wellspent-2123e.appspot.com'})
db = firestore.client()

# Your complete JSON data
json_data = {
    "custom_messages": [
        "Merchant: Nike, Message: You've made several purchases at Nike. Consider getting a Nike membership or look for official coupons online.",
        "Merchant: Amazon, Message: There are many transactions at Amazon. Keep an eye out for upcoming deals to save money."
    ],
    "predicted_merchant": "Amazon",
    "predicted_transaction_details": [
        {
            "Amount Spent ($)": 68.29,
            "Date": "Sun, 01 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 6,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 27.52,
            "Date": "Sun, 01 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 6,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 95.61,
            "Date": "Wed, 04 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 2,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 30.02,
            "Date": "Sun, 08 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 6,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 6.1,
            "Date": "Sun, 08 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 6,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 45.73,
            "Date": "Sun, 15 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 6,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 45.44,
            "Date": "Fri, 20 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 4,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 65.32,
            "Date": "Tue, 24 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 1,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 69.44,
            "Date": "Sun, 29 Oct 2023 00:00:00 GMT",
            "DayOfWeek": 6,
            "Merchant": "Amazon",
            "Month": 10
        },
        {
            "Amount Spent ($)": 61.1,
            "Date": "Wed, 01 Nov 2023 00:00:00 GMT",
            "DayOfWeek": 2,
            "Merchant": "Amazon",
            "Month": 11
        },
        {
            "Amount Spent ($)": 45.98,
            "Date": "Mon, 13 Nov 2023 00:00:00 GMT",
            "DayOfWeek": 0,
            "Merchant": "Amazon",
            "Month": 11
        },
        {
            "Amount Spent ($)": 38.29,
            "Date": "Thu, 16 Nov 2023 00:00:00 GMT",
            "DayOfWeek": 3,
            "Merchant": "Amazon",
            "Month": 11
        },
        {
            "Amount Spent ($)": 83.16,
            "Date": "Sat, 25 Nov 2023 00:00:00 GMT",
            "DayOfWeek": 5,
            "Merchant": "Amazon",
            "Month": 11
        }
    ]
}

# Define a function to format the transaction data
def format_transaction(transaction):
    formatted_output = []
    formatted_output.append(f"Amount Spent ($): {transaction['Amount Spent ($)']:.2f}")
    formatted_output.append(f"Date: {transaction['Date']}")
    formatted_output.append(f"Day of Week: {transaction['DayOfWeek']}")
    formatted_output.append(f"Merchant: {transaction['Merchant']}")
    formatted_output.append(f"Month: {transaction['Month']}")
    return "\n".join(formatted_output)

# Format the data
formatted_custom_messages = "\n".join(json_data["custom_messages"])
formatted_predicted_merchant = json_data["predicted_merchant"]
formatted_transaction_details = "\n\n".join([format_transaction(transaction) for transaction in json_data["predicted_transaction_details"]])

# Combine the formatted data
def create_image_with_tables(texts):
    # Define image dimensions and colors
    width, height = 800, 1000
    background_color = 'white'
    text_color = 'black'
    
    # Create a new image with white background
    img = Image.new('RGB', (width, height), background_color)
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Starting positions
    x, y = 10, 10
    
    # Draw text on image
    for text in texts:
        d.text((x, y), text, font=font, fill=text_color)
        y += 10 * len(text.split('\n'))  # Adjust y position based on number of lines

    return img

# Create image with tables and text
texts = [formatted_custom_messages, formatted_predicted_merchant, formatted_transaction_details]
img = create_image_with_tables(texts)

# Convert image to byte array
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')

# Function to upload image to Firebase Storage
def upload_to_firebase_storage(img_byte_arr, cloud_file_path):
    bucket = storage.bucket()
    blob = bucket.blob(cloud_file_path)
    blob.upload_from_string(img_byte_arr.getvalue(), content_type='image/png')
    blob.make_public()
    return blob.public_url

# Function to save URL to Firestore
def save_url_to_firestore(document_id, field_name, url):
    doc_ref = db.collection('users').document(document_id)
    doc_ref.set({field_name: url}, merge=True)

# Upload image to Firebase Storage
image_url = upload_to_firebase_storage(img_byte_arr, 'images/pie_chart.png')

# Save URL to Firestore
save_url_to_firestore('vLWAQeLvDKfkXVyWP19SBTL7cOu1', 'prediction_url', image_url)

print(f"Image uploaded to Firebase Storage and URL saved to Firestore. Image URL: {image_url}")