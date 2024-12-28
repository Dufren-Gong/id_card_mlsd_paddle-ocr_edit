import math
import cv2

def show_pic(img, name):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

class Line():
    def __init__(self, start_point, end_point) -> None:
        self.start_point = start_point
        self.end_point = end_point

def draw_lines_on_pic(img, lines, save_floader, dot_thickness=3, line_thickness=3):
    for l in lines:
        cv2.line(img, (int(l[0][0]), int(l[0][1])), (int(l[1][0]), int(l[1][1])), (0,0,255), line_thickness)
        cv2.circle(img, (int(l[0][0]), int(l[0][1])), color=(0,255,0), radius=dot_thickness, thickness=-1)
        cv2.circle(img, (int(l[1][0]), int(l[1][1])), color=(0,255,0), radius=dot_thickness, thickness=-1)
    cv2.imwrite(save_floader, img)

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def direction_vector(pt1, pt2):
    return (pt2[0] - pt1[0], pt2[1] - pt1[1])

def angle_between(v1, v2):
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude1 = math.sqrt(v1[0]**2 + v1[1]**2)
    magnitude2 = math.sqrt(v2[0]**2 + v2[1]**2)
    cos_theta = dot_product / (magnitude1 * magnitude2)
    return math.degrees(math.acos(cos_theta))

def point_to_line_distance(pt, line_start, line_end):
    num = abs((line_end[1] - line_start[1]) * pt[0] - (line_end[0] - line_start[0]) * pt[1] + line_end[0] * line_start[1] - line_end[1] * line_start[0])
    den = math.sqrt((line_end[1] - line_start[1])**2 + (line_end[0] - line_start[0])**2)
    return num / den

def almost_collinear_and_collinear(line1, line2, angle_tolerance=5, distance_tolerance=5):
    A, B = line1
    C, D = line2

    vec1 = direction_vector(A, B)
    vec2 = direction_vector(C, D)

    angle = angle_between(vec1, vec2)
    if angle > 90:
        angle = 180 - angle
    if angle > angle_tolerance:
        return False

    # Check if points C and D are on the line AB
    dist_C_to_AB = point_to_line_distance(C, A, B)
    dist_D_to_AB = point_to_line_distance(D, A, B)
    
    return dist_C_to_AB < distance_tolerance and dist_D_to_AB < distance_tolerance

def merge_lines(line1, line2):
    points = line1 + line2
    max_distance = 0
    end_points = [points[0], points[1]]
    
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = distance(points[i], points[j])
            if d > max_distance:
                max_distance = d
                end_points = [points[i], points[j]]
    return end_points

def process_lines(img, lines, save_path, angle_tolerance=5, distance_tolerance=5):
    merged_lines = []
    used = [False] * len(lines)

    for i in range(len(lines)):
        if used[i]:
            continue
        for j in range(i + 1, len(lines)):
            if used[j]:
                continue
            if almost_collinear_and_collinear(lines[i], lines[j], angle_tolerance, distance_tolerance):
                merged_line = merge_lines(lines[i], lines[j])
                lines[i] = merged_line
                used[j] = True
        if not used[i]:
            merged_lines.append(lines[i])
            used[i] = True
    draw_lines_on_pic(img, merged_lines, save_path, dot_thickness=10)
    return merged_lines

def process_squares(img, lines, save_path):
    pass
