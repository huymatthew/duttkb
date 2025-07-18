from PIL import Image, ImageDraw, ImageFont
import random
import json
import re

# Define colors for courses
COLORS = [
    "#FFB6C1", "#87CEEB", "#98FB98", "#F0E68C", "#DDA0DD",
    "#FFA07A", "#20B2AA", "#87CEFA", "#FFEFD5", "#D3D3D3"
]

def parse_schedule(schedule_str):
    """
    Parse schedule string like "Thứ 6,1-4,H201" or "Thứ 4,7-10,D211; Thứ 6,1-4,D211"
    Returns list of (day, start_period, end_period, room)
    """
    if not schedule_str or schedule_str.strip() == "":
        return []
    
    schedules = []
    
    try:
        # Split by semicolon for multiple sessions
        sessions = schedule_str.split(';')
        
        for session in sessions:
            session = session.strip()
            if not session:
                continue
                
            # Split by comma
            parts = re.split(r'[,:]', session)
            if len(parts) < 2:
                continue
                
            # Parse day (Thứ 2 = Monday = 2, ..., Thứ 7 = Saturday = 7)
            day_part = parts[0].strip()
            day_match = re.search(r'Thứ (\d+)', day_part)
            if not day_match:
                continue
            day = int(day_match.group(1))
            
            # Parse periods (1-4 means from period 1 to period 4)
            period_part = parts[1].strip()
            period_match = re.search(r'(\d+)-(\d+)', period_part)
            if not period_match:
                # Try single period
                single_match = re.search(r'(\d+)', period_part)
                if single_match:
                    start_period = end_period = int(single_match.group(1))
                else:
                    continue
            else:
                start_period = int(period_match.group(1))
                end_period = int(period_match.group(2))
            
            # Parse room
            room = parts[2].strip() if len(parts) > 2 else ""
            
            schedules.append((day, start_period, end_period, room))
            
    except:
        pass
    
    return schedules

def parse_json_data(json_data):
    """
    Parse JSON data and convert to course format
    """
    courses = {}
    _type = ()
    if 'Column_7' in json_data[0] and 'Column_8' in json_data[0]:
        _type = ("Thông tin lớp học phần", "Khảo sát ý kiến cuối học kỳ" ,'Column_7', 'Column_8')
    else:
        _type = ('Mã lớp học phần', 'Tên lớp học phần', 'Giảng viên', 'Thời khóa biểu')
    print(_type)
    for item in json_data:
        # Skip header row and summary row
        if not isinstance(item.get("TT"), int):
            print("Skipping non-data row:", item)
            continue

        
        course_code = item.get(_type[0], "")
        course_name = item.get(_type[1], "")
        teacher = item.get(_type[2], "")
        schedule_str = item.get(_type[3], "")

        print(f"&&&Processing course: {course_code}, {course_name}, {teacher}, {schedule_str}")

        # Parse schedule (now returns list of schedules)
        schedule_list = parse_schedule(schedule_str)
        if not schedule_list:
            continue
        
        # Create separate course entry for each schedule session
        course_id_base = str(item.get("TT"))
        
        for i, (day, start_period, end_period, room) in enumerate(schedule_list):
            # Use suffix for multiple sessions of same course
            course_id = f"{course_id_base}_{i}" if i > 0 else course_id_base
            
            courses[course_id] = {
                'course_code': course_code,
                'course_name': course_name,
                'teacher': teacher,
                'room': room,
                'schedule': [day, start_period, end_period, room],
                'session_index': i  # To identify which session this is
            }
    
    return courses
def draw_text_with_max_width(draw, text, position, font, max_width, fill):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
            line = line + (words.pop(0) + ' ')
        lines.append(line)
    
    y = position[1]
    for line in lines:
        draw.text((position[0] + 20, y), line, font=font, fill=fill)
        y += draw.textbbox((0, 0), line, font=font)[3]
def generator(json_data):
    print("json_data:", json_data)
    image_path = 'tbk.png'
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("SVN-Segoe UI.ttf", 40, encoding="utf-8")
    max_width = 340  # Set your max width here
    position = (513, 385)
    
    # Parse JSON data to course format
    if isinstance(json_data, str):
        data = parse_json_data(json.loads(json_data))
    elif isinstance(json_data, list):
        data = parse_json_data(json_data)
    else:
        data = json_data
    
    def add_course(course):
        text = course['course_name'] + '\n - ' + str(course['schedule'][3])
        cpos = (position[0] + (course['schedule'][0] - 2) * 64 * 6, position[1] + (course['schedule'][1] - 1) * 128)
        rect_x0 = cpos[0]
        rect_y0 = cpos[1]
        rect_x1 = cpos[0] + 384
        rect_y1 = cpos[1] + (course['schedule'][2] - course['schedule'][1] + 1) * 128
        draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], outline="black", fill=random.choice(COLORS), width=4)
        draw_text_with_max_width(draw, text, cpos, font, max_width, fill=(0, 0, 0))
    
    for course in data.values():
        add_course(course)
    return image

if __name__ == '__main__':
    # Sample JSON data for testing
    sample_json_data = [
        {
            'TT': 1,
            'Mã lớp học phần': '0130590.2510.24.04',
            'Tên lớp học phần': 'B24-GDTC3-CL-04',
            'T.chỉ': 0,
            'Giảng viên': 'Khoa Giáo dục thể chất',
            'Thời khóa biểu': 'Thứ 4: 1-4,GDTC',
            'Tuần học': '2-16',
            'Đ.ký lúc': '7/18/2025 3:04:12 PM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '50/50', 'CLC': '', 'Column_16': ''
        },
        {
            'TT': 2,
            'Mã lớp học phần': '1023290.2510.24.10',
            'Tên lớp học phần': 'Cơ sở dữ liệu',
            'T.chỉ': 2,
            'Giảng viên': 'Võ Đức Hoàng',
            'Thời khóa biểu': 'Thứ 6: 3-4,E110A',
            'Tuần học': '1-16',
            'Đ.ký lúc': '7/14/2025 10:01:27 AM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '53/53', 'CLC': '', 'Column_16': ''
        },
        {
            'TT': 3,
            'Mã lớp học phần': '2170020.2510.24.99',
            'Tên lớp học phần': 'Kinh tế chính trị Mác - Lênin',
            'T.chỉ': 2,
            'Giảng viên': 'Nguyễn Thị Kiều Trinh',
            'Thời khóa biểu': 'Thứ 3: 1-2,E402',
            'Tuần học': '1-16',
            'Đ.ký lúc': '7/18/2025 3:35:49 PM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '57/57', 'CLC': '', 'Column_16': ''
        },
        {
            'TT': 4,
            'Mã lớp học phần': '1023693.2510.24.10',
            'Tên lớp học phần': 'Lập trình hướng đối tượng',
            'T.chỉ': 2.5,
            'Giảng viên': 'Lê Thị Mỹ Hạnh',
            'Thời khóa biểu': 'Thứ 5: 8-10,E104',
            'Tuần học': '1-14',
            'Đ.ký lúc': '7/14/2025 10:00:43 AM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '51/53', 'CLC': '', 'Column_16': ''
        },
        {
            'TT': 5,
            'Mã lớp học phần': '1022913.2510.24.10',
            'Tên lớp học phần': 'Nguyên lý hệ điều hành',
            'T.chỉ': 2.5,
            'Giảng viên': 'Trần Hồ Thủy Tiên',
            'Thời khóa biểu': 'Thứ 3: 6-8,E301B',
            'Tuần học': '1-14',
            'Đ.ký lúc': '7/14/2025 10:00:43 AM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '51/53', 'CLC': '', 'Column_16': ''
        },
        {
            'TT': 6,
            'Mã lớp học phần': '1023690.2510.24.10A',
            'Tên lớp học phần': 'PBL 2: Đồ án cơ sở lập trình',
            'T.chỉ': 2,
            'Giảng viên': 'Nguyễn Văn Hiệu',
            'Thời khóa biểu': 'Thứ 7: 1-2,C102',
            'Tuần học': '1-16',
            'Đ.ký lúc': '7/14/2025 10:02:37 AM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '30/30', 'CLC': '', 'Column_16': ''
        },
        {
            'TT': 7,
            'Mã lớp học phần': '1022830.2510.24.10',
            'Tên lớp học phần': 'Phân tích & thiết kế giải thuật',
            'T.chỉ': 2,
            'Giảng viên': 'Đặng Thiên Bình',
            'Thời khóa biểu': 'Thứ 6: 6-7,F109',
            'Tuần học': '1-16',
            'Đ.ký lúc': '7/14/2025 10:00:43 AM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '53/53', 'CLC': '', 'Column_16': ''
        },
        {
            'TT': 8,
            'Mã lớp học phần': '3190041.2510.24.78',
            'Tên lớp học phần': 'Xác suất thống kê',
            'T.chỉ': 3,
            'Giảng viên': 'Nguyễn Thị Hải Yến',
            'Thời khóa biểu': 'Thứ 5: 3-5,F210',
            'Tuần học': '1-15;17-17',
            'Đ.ký lúc': '7/18/2025 3:09:43 PM',
            '(Đ)': '', '(K)': '', '(T)': '', '(G)': '',
            'Học lại': '', 'Đ.ký': '65/65', 'CLC': '', 'Column_16': ''
        }
    ]
    
    image = generator(sample_json_data)
    image.show()