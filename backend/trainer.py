import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle

def train_model():
    # Loading the Flipkart dataset
    df = pd.read_csv('products.csv')
    
    # Selecting the requested attributes
    cols = ['brand', 'product_category_tree', 'retail_price']
    df = df[cols].dropna()

    # Numeric conversion for alphanumeric strings
    le_b = LabelEncoder()
    le_c = LabelEncoder()
    
    # supervisor-suggested numeric mapping
    df['brand_n'] = le_b.fit_transform(df['brand'].astype(str))
    df['cat_n'] = le_c.fit_transform(df['product_category_tree'].astype(str))
    
    # Defining the verification logic (Verified if price > 500)
    df['target'] = df['retail_price'].apply(lambda x: 1 if float(x) > 500 else 0)
    
    # Preparing data for the AI model
    x = df[['brand_n', 'cat_n', 'retail_price']].values.tolist() # Convert to list
    y = df['target'].values.tolist()
    
    m = RandomForestClassifier()
    m.fit(x, y)
    
    # Saving numeric encoders and the model
    with open('model.pkl', 'wb') as f:
        pickle.dump(m, f)
    with open('le_b.pkl', 'wb') as f:
        pickle.dump(le_b, f)
    with open('le_c.pkl', 'wb') as f:
        pickle.dump(le_c, f)
    print("AI Model Trained with Numeric Conversion.")

if __name__ == "__main__":
    train_model()