import json
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
from sklearn.preprocessing import LabelEncoder
from loguru import logger

MODEL_FILE = 'ml_model/saved_model.pkl'
LOG_FILE = 'data/usb_device_logs.json'


def train_model() -> None:
    """ Train the model on the logged USB device data. """
    with open(LOG_FILE, 'r') as file:
        logs = json.load(file)

    if len(logs) == 0:
        logger.warning("No data to train the model.")
        return None

    # Extract features and labels, skipping entries without 'decision'
    vendor_ids = []
    product_ids = []
    serials = []
    decisions = []

    vendor_allow_count = {}  # Track how many times a vendor has been allowed

    for log in logs:
        if 'decision' not in log:
            continue
        vendor_id = log['vendor_id']
        vendor_ids.append(vendor_id)
        product_ids.append(log['product_id'])
        serials.append(log['serial'])
        decisions.append(1 if log['decision'] == 'allow' else 0)

        # Increment the count for each vendor being allowed
        if log['decision'] == 'allow':
            if vendor_id not in vendor_allow_count:
                vendor_allow_count[vendor_id] = 0
            vendor_allow_count[vendor_id] += 1

    # Check the balance of "allow" vs "block"
    allow_count = decisions.count(1)
    block_count = decisions.count(0)
    logger.info(f"Training data: {allow_count} allow, {block_count} block")

    # Encode features and train model as before
    le_vendor = LabelEncoder()
    le_product = LabelEncoder()
    le_serial = LabelEncoder()

    vendor_ids_encoded = le_vendor.fit_transform(vendor_ids)
    product_ids_encoded = le_product.fit_transform(product_ids)
    serials_encoded = le_serial.fit_transform(serials)

    X = np.column_stack((vendor_ids_encoded, product_ids_encoded, serials_encoded))
    y = np.array(decisions)

    model = DecisionTreeClassifier()
    model.fit(X, y)

    # Save the trained model and encoders
    joblib.dump(model, MODEL_FILE)
    joblib.dump(le_vendor, 'ml_model/le_vendor.pkl')
    joblib.dump(le_product, 'ml_model/le_product.pkl')
    joblib.dump(le_serial, 'ml_model/le_serial.pkl')

    logger.info("Model and encoders trained and saved.")


def predict(device_info: {}) -> '':
    """ Predict whether a device should be allowed or blocked based on past data. """
    try:
        model = joblib.load(MODEL_FILE)
        le_vendor = joblib.load('ml_model/le_vendor.pkl')
        le_product = joblib.load('ml_model/le_product.pkl')
        le_serial = joblib.load('ml_model/le_serial.pkl')
    except FileNotFoundError:
        logger.error("Model or encoders not found.")
        return None

    # Load vendor allow counts
    try:
        with open('data/vendor_allow_counts.json', 'r') as f:
            vendor_allow_count = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        vendor_allow_count = {}

    vendor_id = device_info['vendor_id']

    # Automatically allow only if the vendor has been allowed 5 or more times
    if vendor_allow_count.get(vendor_id, 0) >= 5:
        logger.info(f"Automatically allowing USB device from vendor {vendor_id}")
        return 'allow'

    # Handle unseen values for LabelEncoders
    try:
        vendor_encoded = le_vendor.transform([device_info['vendor_id']])[0]
    except ValueError:
        logger.warning(f"Vendor ID {device_info['vendor_id']} not recognized by encoder.")
        return None  # Prompt user for decision

    try:
        product_encoded = le_product.transform([device_info['product_id']])[0]
    except ValueError:
        logger.warning(f"Product ID {device_info['product_id']} not recognized by encoder.")
        return None  # Prompt user for decision

    try:
        serial_encoded = le_serial.transform([device_info['serial']])[0]
    except ValueError:
        logger.warning(f"Serial {device_info['serial']} not recognized by encoder.")
        return None  # Prompt user for decision

    # Convert device info to features for the model
    features = np.array([[vendor_encoded, product_encoded, serial_encoded]])

    # Model prediction (fallback if auto-allow threshold is not met)
    prediction = model.predict(features)
    return 'allow' if prediction == 1 else None

