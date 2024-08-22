import cv2
import mediapipe as mp
from djitellopy import Tello
import time
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Encryption Setup (AES)
def generate_aes_key():
    return secrets.token_bytes(32)  # 256-bit key

def encrypt_message(key, message):
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()
    return iv, encrypted_message

def decrypt_message(key, iv, encrypted_message):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return decrypted_message.decode()

# Authentication Setup
AUTH_TOKEN = "secure_token"

def authenticate(token):
    return token == AUTH_TOKEN

# Initialize Mediapipe hands module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)

# Initialize Tello drone
tello = Tello()
tello.connect()
tello.streamon()
tello.takeoff()
tello.send_rc_control(0, 0, 0, 0)

time.sleep(4)

# Encryption Key
aes_key = generate_aes_key()

# Initialize OpenCV video capture for Tello stream
cap = cv2.VideoCapture('udp://0.0.0.0:11111')

# Direction mapping with corresponding drone commands
direction_commands = {
    "Right": (0, 30, 0, 0),    # Move right
    "Left": (0, -30, 0, 0),    # Move left
    "Forward": (30, 0, 0, 0),  # Move forward
    "Backward": (-30, 0, 0, 0) # Move backward
}

# Direction mapping display text
direction_mapping = {
    "Right": "Moving Right",
    "Left": "Moving Left",
    "Forward": "Moving Forward",
    "Backward": "Moving Backward",
    "No Direction": "No Direction"
}

while True:
    # Read frame from Tello video stream
    ret, frame = cap.read()

    if ret:
        # Convert the frame to RGB for Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with Mediapipe hands
        results = hands.process(frame_rgb)

        # Initialize direction as "No Direction"
        direction = "No Direction"

        # Check if hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the landmarks for the hand
                for landmark in hand_landmarks.landmark:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # Calculate the horizontal and vertical differences between thumb and index/middle fingers
                thumb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
                thumb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
                index_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                index_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                middle_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x
                middle_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y

                horizontal_diff = thumb_x - index_x
                vertical_diff = thumb_y - (index_y + middle_y) / 2

                # Determine the direction based on the differences
                if abs(horizontal_diff) > abs(vertical_diff):
                    if horizontal_diff > 0:
                        direction = "Right"
                    else:
                        direction = "Left"
                else:
                    if vertical_diff < 0:
                        direction = "Forward"
                    else:
                        direction = "Backward"
                
                # Secure Command: Encrypt the command and send to the drone
                if authenticate(AUTH_TOKEN):
                    iv, encrypted_command = encrypt_message(aes_key, direction)
                    # Map the detected direction to drone commands
                    command = direction_commands.get(direction, (0, 0, 0, 0))
                    tello.send_rc_control(*command)
                else:
                    print("Authentication failed!")

        # Display the frame with direction
        cv2.putText(frame, f"Direction: {direction_mapping.get(direction, 'No Direction')}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Hand Gestures", frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        tello.land()
        break

# Land the Tello drone and release resources
tello.streamoff()
tello.disconnect()
cap.release()
cv2.destroyAllWindows()
