import cv2

def main():
    cap = cv2.VideoCapture(0)  # 0 = default laptop camera

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Laptop Camera Preview (press q to quit)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


#python video_preview.py
# To run this script, ensure you have OpenCV installed: