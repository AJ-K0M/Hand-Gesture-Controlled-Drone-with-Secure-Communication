import cv2
import mediapipe as mp
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

# Initialize Mediapipe hands module
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)

# Encryption Key
aes_key = generate_aes_key()

# Initialize OpenCV video capture for PC camera
pc_camera_cap = cv2.VideoCapture(0)

# Direction mapping
direction_mapping = {
    "Right": "right",
    "Left": "left",
    "Forward": "forward",
    "Backward": "backward",
    "Up": "up",
    "Down": "down",
}

while True:
    # Read frame from PC camera
    ret_pc_camera, pc_camera_frame = pc_camera_cap.read()

    if ret_pc_camera:
        # Convert the PC camera frame to RGB for Mediapipe
        pc_camera_frame_rgb = cv2.cvtColor(pc_camera_frame, cv2.COLOR_BGR2RGB)

        # Process the PC camera frame with Mediapipe hands
        results = hands.process(pc_camera_frame_rgb)

        # Initialize direction as "No Direction"
        direction = "No Direction"

        # Check if hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the landmarks for the hand
                thumb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
                thumb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
                index_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                index_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                middle_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x
                middle_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y

                horizontal_diff = thumb_x - index_x
                vertical_diff = thumb_y - (index_y + middle_y) / 2
                avg_y = (index_y + middle_y) / 2

                # Directions
                if vertical_diff < -0.1:
                    direction = "Up"
                elif vertical_diff > 0.1:
                    direction = "Down"
                elif horizontal_diff > 0.1:
                    direction = "Right"
                elif horizontal_diff < -0.1:
                    direction = "Left"
                elif index_y < avg_y - 0.05:
                    direction = "Forward"
                elif index_y > avg_y + 0.05:
                    direction = "Backward"
                else:
                    direction = "No Direction"

                # Encrypt the command (direction)
                iv, encrypted_command = encrypt_message(aes_key, direction)
                decrypted_command = decrypt_message(aes_key, iv, encrypted_command)  # Just for demonstration
                
                # Print decrypted command for verification
                print(f"Encrypted Command: {encrypted_command}")
                print(f"Decrypted Command: {decrypted_command}")

                # Draw landmarks on the PC camera frame
                mp_drawing.draw_landmarks(pc_camera_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                          mp_drawing_styles.get_default_hand_landmarks_style(),
                                          mp_drawing_styles.get_default_hand_connections_style())

        # Display the PC camera frame with direction and landmarks
        cv2.putText(pc_camera_frame, f"Direction: {direction_mapping.get(direction, 'No Direction')}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Hand Gestures (PC Camera)", pc_camera_frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
pc_camera_cap.release()
cv2.destroyAllWindows()
