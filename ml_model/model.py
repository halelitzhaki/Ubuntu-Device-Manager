import json
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
from sklearn.preprocessing import LabelEncoder

MODEL_FILE = 'ml_model/saved_model.pkl'
LOG_FILE = 'data/usb_device_logs.json'


def train_model():
    """ Train the model on the logged USB device data. """
    with open(LOG_FILE, 'r') as file:
        logs = json.load(file)

    if len(logs) == 0:
        print("No data to train the model.")
        return None

    # Extract features and labels, skipping entries without 'decision'
    vendor_ids = []
    product_ids = []
    serials = []
    decisions = []

    for log in logs:
        if 'decision' not in log:
            continue
        vendor_ids.append(log['vendor_id'])
        product_ids.append(log['product_id'])
        serials.append(log['serial'])
        decisions.append(1 if log['decision'] == 'allow' else 0)

    # Encode features and train model as before
    le_vendor = LabelEncoder()
    le_product = LabelEncoder()
    le_serial = LabelEncoder()

    vendor_ids_encoded = le_vendor.fit_transform(vendor_ids)
    product_ids_encoded = le_product.fit_transform(product_ids)
    serials_encoded = le_serial.fit_transform(serials)

    X = np.column_stack((vendor_ids_encoded, product_ids_encoded, serials_encoded))
    y = np.array(decisions)

    # Train the model on the entire dataset if there are not enough samples for a split
    if len(X) < 2:
        print("Not enough data to split, using all data for training.")
        model = DecisionTreeClassifier()
        model.fit(X, y)
    else:
        # Train/test split (only if there is enough data)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model
        model = DecisionTreeClassifier()
        model.fit(X_train, y_train)

    # Save the trained model
    joblib.dump(model, MODEL_FILE)
    print("Model trained and saved.")


def predict(device_info):
    """ Predict whether a device should be allowed or blocked based on past data. """
    try:
        model = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        return None

    # Convert device info to features
    features = np.array([[
        le_vendor.transform([device_info['vendor_id']])[0],
        le_product.transform([device_info['product_id']])[0],
        le_serial.transform([device_info['serial']])[0]
    ]])

    prediction = model.predict(features)
    return 'allow' if prediction == 1 else 'block'
