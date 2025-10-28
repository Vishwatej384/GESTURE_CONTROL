import math

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def fingers_up(lm):
    ids = {
        "thumb_tip": 4, "index_tip": 8, "middle_tip": 12,
        "ring_tip": 16, "pinky_tip": 20,
        "index_pip": 6, "middle_pip": 10, "ring_pip": 14, "pinky_pip": 18,
    }
    up = 0
    if lm[ids["index_tip"]][1] < lm[ids["index_pip"]][1]: up += 1
    if lm[ids["middle_tip"]][1] < lm[ids["middle_pip"]][1]: up += 1
    if lm[ids["ring_tip"]][1] < lm[ids["ring_pip"]][1]: up += 1
    if lm[ids["pinky_tip"]][1] < lm[ids["pinky_pip"]][1]: up += 1
    return up
