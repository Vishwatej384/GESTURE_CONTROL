import cv2
import numpy as np
import time
from volume_control.volume_control import get_volume_controller
from volume_control.smooth_value import SmoothValue
from volume_control.gestures import distance, fingers_up
from volume_control.utils import mp_hands, mp_drawing

def main():
    vol = get_volume_controller()
    vol_min, vol_max = vol.get_range()

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    smooth = SmoothValue(alpha=0.35)
    locked = False
    last_mute_toggle = 0

    pinch_min = 25
    pinch_max = 225
    fps_time = time.time()
    fps = 0

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            h, w, _ = frame.shape
            current_volume = vol.get_volume()

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                lm = {}
                for i, lm_obj in enumerate(hand_landmarks.landmark):
                    lm[i] = (int(lm_obj.x * w), int(lm_obj.y * h))

                p1 = lm[4]
                p2 = lm[8]
                d = distance(p1, p2)

                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                cv2.circle(frame, p1, 8, (0, 255, 0), -1)
                cv2.circle(frame, p2, 8, (0, 255, 0), -1)
                cv2.line(frame, p1, p2, (255, 255, 255), 2)

                up = fingers_up(lm)

                if up == 2:
                    locked = True
                    cv2.putText(frame, "LOCKED", (20, 120),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)
                else:
                    if up >= 3:
                        locked = False

                now = time.time()
                if up == 0 and now - last_mute_toggle > 0.8:
                    vol.toggle_mute()
                    last_mute_toggle = now

                if not locked:
                    d_clamped = np.clip(d, pinch_min, pinch_max)
                    raw_level = np.interp(d_clamped, [pinch_min, pinch_max], [vol_min, vol_max])
                    level = smooth.update(raw_level)
                    vol.set_volume(int(level))

                bar_level = vol.get_volume()
                bar_x = 50
                cv2.rectangle(frame, (bar_x, 150), (bar_x + 30, 450), (50, 50, 50), 2)
                bar_h = int(np.interp(bar_level, [0, 100], [450, 150]))
                cv2.rectangle(frame, (bar_x, bar_h), (bar_x + 30, 450), (100, 200, 100), -1)
                cv2.putText(frame, f"Vol: {bar_level}%", (bar_x - 10, 480),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            new_time = time.time()
            fps = 1.0 / (new_time - fps_time) if new_time != fps_time else fps
            fps_time = new_time
            cv2.putText(frame, f"FPS: {int(fps)}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            cv2.putText(frame, "Pinch thumb-index to change volume", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2)
            cv2.putText(frame, "Fist=mute, Two fingers=lock", (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2)

            cv2.imshow("Gesture Volume Control", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
