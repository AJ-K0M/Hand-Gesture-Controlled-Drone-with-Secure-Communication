# Hand Gesture Controlled Drone with AES Encryption

## Overview

This project integrates hand gesture recognition to control a Tello drone, using the `mediapipe` library for gesture recognition and `djitellopy` for drone control. AES encryption is utilized to securely manage commands sent to the drone.

## Features

- Hand gesture recognition using Mediapipe
- Control of Tello drone via hand gestures
- AES encryption for secure command transmission
- Real-time video streaming from both PC camera and Tello drone

## Installation

### Prerequisites

- Python 3.x
- Pip (Python package installer)

### Dependencies

Install the required Python libraries using pip:

```bash
pip install opencv-python mediapipe djitellopy cryptography
```

## Usage

1. **Set Up Environment Variables**

   Store sensitive information in environment variables for security:

   ```bash
   export AUTH_TOKEN="your_secure_token"
   export AES_KEY="your_base64_encoded_key"
   ```

2. **Run the Script**

   Execute the script to start the hand gesture control and AES encryption:

   ```bash
   python your_script_name.py
   ```

## Code Explanation

- **Encryption Setup:**

  The AES encryption functions ensure that commands sent to the drone are encrypted. The `encrypt_message` function encrypts the command, while the `decrypt_message` function decrypts it.

- **Hand Gesture Recognition:**

  The script uses the Mediapipe library to detect hand gestures from the PC camera feed. It calculates differences between hand landmarks to determine the direction of movement.

- **Drone Control:**

  The Tello drone is controlled based on detected hand gestures, such as moving up, down, left, right, forward, or backward.

- **Video Streaming:**

  Real-time video feeds from the PC camera and Tello drone are displayed using OpenCV.

## Security Considerations

- Ensure that AES keys and tokens are securely managed and rotated regularly.
- Use secure channels (e.g., HTTPS) for remote communications.
- Avoid logging sensitive information.

## Acknowledgements

- [Mediapipe](https://mediapipe.dev/) for hand gesture recognition
- [djitellopy](https://github.com/dji-sdk/djitellopy) for Tello drone control
- [Cryptography](https://cryptography.io/) for AES encryption


