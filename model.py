import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Constants for detection thresholds
PING_ATTACK_THRESHOLD = 35
PORT_ATTACK_THRESHOLD = 150

# Function to detect intrusion using Random Forest
def detect_intrusion(df):
    # Encode categorical columns
    label_encoders = {}
    for col in df.select_dtypes(include='object').columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    # Split dataset into features and labels
    X = df.drop(columns=["Protocol"])
    y = df["Protocol"]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Train Random Forest Classifier
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    # Make predictions
    y_pred = rf_model.predict(X_test)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    # Detect Ping and Port Attacks
    ping_attack_detected = (
        df["Protocol"]
        .rolling(window=PING_ATTACK_THRESHOLD)
        .apply(lambda x: (x == label_encoders["Protocol"].transform(["eth:ethertype:ip:data"])[0]).all(), raw=True)
        .any()
    )

    if ping_attack_detected:
        print("It's a ping attack!")
        return True

    port_attack_detected = (
        df["Protocol"]
        .rolling(window=PORT_ATTACK_THRESHOLD)
        .apply(lambda x: (x == label_encoders["Protocol"].transform(["eth:ethertype:ip:tcp"])[0]).all(), raw=True)
        .any()
    )

    if port_attack_detected:
        print("It's a port attack!")
        return True

    print("No attack detected.")
    return False


# Main function
def run_intrusion_detection():
    file_path = input("Enter the file path for the dataset: ").strip()
    # Remove any quotes from the input
    file_path = file_path.strip('"').strip("'")
    try:
        # Load the dataset
        df = pd.read_csv(file_path)

        # Display available columns
        print("Available columns:", df.columns)

        # Run intrusion detection
        detect_intrusion(df)

    except Exception as e:
        print(f"Error: {e}")


# Run the main function
if __name__ == "__main__":
    run_intrusion_detection()