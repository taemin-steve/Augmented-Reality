import cv2

vid_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
# Check if the webcam is opened correctly
if not vid_cap.isOpened():
    raise IOError("Cannot open webcam")

imgW = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
imgH = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


# Check if the VideoCapture object was successfully created
if not vid_cap.isOpened():
    print("Error opening video capture.")
    exit()

num = 0
key = cv2.waitKey()

# Loop through frames of the video
while True:
    # Read a frame from the video
    ret, frame = vid_cap.read()

    # Check if the frame was successfully read
    if not ret:
        print("Error reading frame.")
        break

    # Display the frame
    cv2.imshow("Video", frame)
    if key == ord('c'):
        cv2.imwrite("./checkerboard/frame" + str(num) + ".jpg" ,frame )
        num += 1
    # Exit the loop if the user presses the "q" key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite("./checkerboard/frame" + str(num) + ".png" ,frame )
        num += 1

# Release the VideoCapture object and close the window
vid_cap.release()
cv2.destroyAllWindows()
