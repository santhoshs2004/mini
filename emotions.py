import cv2
from flask import Flask, render_template, Response
from deepface import DeepFace

# Initialize Flask app
app = Flask(__name__, template_folder='C:/Users/Admin/realtimeemotions')


# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Define wellness recommendations based on emotions
wellness_recommendations = {
    'happy': "Keep smiling! ",
    'sad': "try to be with loved ones",
    'angry': "Try some relaxation",
    'fear': "be strong and brave",
    'surprise': "Channel the excitement! ",
    'neutral': "Try to engage in activities "
}

# Capture video feed
def gen_frames():
    cap = cv2.VideoCapture(0)
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Extract the face region of interest (ROI)
            face_roi = frame[y:y + h, x:x + w]

            # Perform emotion analysis on the face ROI
            result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            
            # Get the predicted emotion
            emotion = result[0]['dominant_emotion']

            # Wellness recommendation based on the emotion
            recommendation = wellness_recommendations.get(emotion, "Take a break and relax!")

            # Draw rectangle around face and display the emotion
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, f"{emotion}: {recommendation}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame to display on the webpage
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()

# Route to display the video feed in the browser
@app.route('/')
def index():
    return render_template('index.html')

# Route to stream the video
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
