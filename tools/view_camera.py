#Show the live webcam feed. Press q to quit.#
import cv2
import time
from perception.camera import open_camera
from perception.fps import FpsCounter

def main() -> None:
    cap = open_camera()
    fps_counter = FpsCounter()
    start = time.perf_counter()
    count = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Camera returned no frame; stopping.")
                break
            count += 1
            frame = cv2.flip(frame, 1)
            fps = fps_counter.tick()
            cv2.putText(frame, f"{fps:.1f} FPS", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("PoseBridge M0", frame)
            #print(frame.shape, frame.dtype)

            key = cv2.waitKey(1) & 0xFF
            
            # Break if 'q' is pressed 
            if key == ord("q") or key == 27 :
                break

            #if the window's 'X' button was clicked
            try:
                if cv2.getWindowProperty("PoseBridge M0", cv2.WND_PROP_AUTOSIZE) < 0:
                    break
            except cv2.error:
                break
    finally:
        elapsed = time.perf_counter() - start
        print(f"AVG FPS: {count / elapsed:.1f}")
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
