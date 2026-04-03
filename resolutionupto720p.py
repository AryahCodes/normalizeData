import cv2
from cv2 import dnn_superres

# 1. Initialize the Super Resolution object
sr = dnn_superres.DnnSuperResImpl_create()

# 2. Load the pre-trained model (EDSR_x4.pb)
path = "EDSR_x4.pb"
sr.readModel(path)
sr.setModel("edsr", 4) # 'edsr' is the model type, 4 is the scale factor

# 3. Open the input video
input_video = "input.mp4"
cap = cv2.VideoCapture(input_video)

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)


fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('upscaled_video.mp4', fourcc, fps, (width * 4, height * 4))

print("Processing video... This may take a while depending on your hardware.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    upscaled_frame = sr.upsample(frame)

    out.write(upscaled_frame)

    cv2.imshow("Upscaling", upscaled_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
print("Upscaling complete!")