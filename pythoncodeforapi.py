import firebase_admin
from firebase_admin import credentials, firestore, storage
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# Initialize Firebase
cred = credentials.Certificate('app.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'wellspent-2123e.appspot.com'})
db = firestore.client()

# Function to upload file to Firebase Storage
def upload_blob(source_file_name, destination_blob_name):
    bucket = storage.bucket()
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    blob.make_public()  # Make the file public
    public_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
    print("File {} uploaded to {}. Public URL: {}".format(source_file_name, destination_blob_name, public_url))
    return public_url  # Returns the public URL of the uploaded file

def save_image_url_to_firestore(user_id, image_url):
    user_ref = db.collection('users').document(user_id)
    user_ref.update({'image_url': image_url})
    print(f"Image URL saved to Firestore for user: {user_id}")

# Rest of your code for data processing and plot generation
# ...
font_size = 25  # Adjust as needed

# Reading the CSV files
spending_trends = pd.read_csv("spending_trends.csv", encoding="ISO-8859-1")
m_category = pd.read_csv("M_category.csv", encoding="ISO-8859-1")

# Merging the data
merged_data = pd.merge(spending_trends, m_category, on="Merchant")

# Grouping by Category and summarizing
category_spending = merged_data.groupby("Category")["AmountSpent"].sum().reset_index()

debt_df = pd.DataFrame({"Category": ["Debt"], "AmountSpent": [250]})
category_spending = pd.concat([category_spending, debt_df], ignore_index=True)

travel_df = pd.DataFrame({"Category": ["Travel"], "AmountSpent": [350]})
category_spending = pd.concat([category_spending, travel_df], ignore_index=True)

# Computing savings
monthly_income = 10000  # Replace this with your actual monthly income value
total_spent = category_spending["AmountSpent"].sum()
savings = monthly_income - total_spent

# Adding savings to the category_spending dataframe
savings_df = pd.DataFrame({"Category": ["Savings"], "AmountSpent": [savings]})
category_spending = pd.concat([category_spending, savings_df], ignore_index=True)

category_spending.loc[category_spending['Category'] == 'Savings', 'AmountSpent'] = savings

# Setting the color palette
custom_colors = {
    "Café": "#FF9999",
    "Food": "#66B2FF",
    "Gas": "#99FF99",
    "Grocery": "#FFCC66",
    "Online": "#C285FF",
    "Savings": "#FF66B2",
     "Debt": "#D9534F",
    "Shopping": "#99E6E6",
    "Travel": "#FFD700"
}

# Handling missing colors
def get_color(category):
    return custom_colors.get(category, "#FFFFFF")  # Default color is white

colors = category_spending["Category"].apply(get_color)

# Plotting the pie chart
plt.figure(figsize=(10, 10))
plt.pie(category_spending["AmountSpent"], labels=category_spending["Category"], colors=colors, autopct='%1.1f%%', textprops={'fontsize': font_size})
plt.title("Spending and Savings by Category", fontsize=font_size)



# Save image locally
plt.savefig("pie_chart.jpg", dpi=303)

# Upload image to Firebase Storage and get the public URL
image_url = upload_blob("pie_chart.jpg", "images/pie_chart.jpg")

# Save the image URL to Firestore under the specific user's document
user_id = 'cNXetVB40fWgOjIAMNuQNxreueq2'  # Replace with the actual user ID
save_image_url_to_firestore(user_id, image_url)

# Show plot
plt.show()
