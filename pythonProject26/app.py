from flask import Flask,render_template,redirect,request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join
from models import *

student_main_id=2121002
teacher_main_id=254633
admin_main_id=0



@app.route('/')
def hello_world():
    return render_template("index.html")
@app.route('/table')
def table():
    return render_template("tables.html",student_courses=get_student_courses(student_main_id))

@app.route('/table_withdraw/<course_id>')     #学生退课
def table_withdraw(course_id):
    delete_student_course(student_main_id, course_id=course_id)
    return render_template("tables.html",student_courses=get_student_courses(student_main_id))

@app.route('/CC/<course_id>')        #学生选课
def CC(course_id):
    add_student_course(student_main_id, course_id=course_id)
    return render_template("tables.html",student_courses=get_student_courses(student_main_id))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/ChooseCourse')
def choose_course():
    return render_template("ChooseCourse.html",student_courses=get_student_unselected_courses(student_main_id))

@app.route('/teacher_course')
def teacher_course():
    return render_template("teacher_Course.html",teacher_courses=get_teacher_allcourses(teacher_main_id))


@app.route('/teacher_grade')
def teacher_grade():
    students = get_teacher_students_scores(teacher_main_id)
    print(students)
    return render_template("teacher_grade.html", students=students)

@app.route('/process_login', methods=['POST'])
def process_login():
   account = request.form['account']
   password = request.form['password']
   role = request.form['role']
   if role=='student':
       student = Student.query.filter_by(student_id=account).first()
       if student.student_passwd==password:
          student_main_id=account
          print(get_student_courses(student_main_id))
          return redirect('/table')
       else:
           return redirect_table()
   if role == 'teacher':
       teacher = Teacher.query.filter_by(teacher_id=account).first()
       if teacher.teacher_passwd == password:
          teacher_main_id=account
          return redirect("/teacher_course")
       else:
           return redirect('/login')
   if role == 'admin':
       admin = UserModel.query.filter_by(id=account).first()
       if admin._password == password:
           admin_main_id=account
       else:
           return redirect('/login')



# 在这里处理表单数据
   return 'Form submitted'


def login():
    return render_template("login.html")

@app.route('/redirect_teacher_course')
def redirect_teacher_course():
    return redirect("/teacher_course")

@app.route('/redirect_teacher_grade')
def redirect_teacher_grade():
    return redirect("/teacher_grade")
@app.route('/redirect_index')
def redirect_index():
    return redirect('/')

@app.route('/redirect_table')
def redirect_table():
    return redirect('/table')

@app.route('/redirect_login')
def redirect_login():
    return redirect('/login')

@app.route('/redirect_ChooseCourse')
def redirect_ChooseCourse():
    return redirect('/ChooseCourse')




@app.route('/withdraw_course', methods=['POST'])
def withdraw_course():
    course_id = request.json['course_id']
    # 在这里执行相应的退课操作，比如从数据库中删除该课程记录等
    return jsonify({'message': 'Course withdrawn successfully'})


#-----------------
def get_student_unselected_courses(student_id):# 查询该学生的所有未选课名单
    selected_courses = [enrollment.course_id for enrollment in Enrollment.query.filter_by(student_id=student_id).all()]
    all_courses = Course.query.all()
    unselected_courses = [course for course in all_courses if course.course_id not in selected_courses]

    return unselected_courses

def get_teacher_allcourses(teacher_id):
    course=Course.query.filter_by(employee_id=teacher_id).all()
    return course

def delete_student_course(student_id, course_id):      #学生退课
    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
        return True
    else:
        return False

def add_student_course(student_id, course_id):     # 学生选课
    existing_enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing_enrollment:
        return False
    else:
        new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        return True








#--------------
def get_student_info_json(student_id):     #查找对应学生的基本信息
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        student_info = {
            'student_id': student.student_id,
            'student_name': student.student_name,
            'student_sex': student.student_sex,
            'student_major': student.student_major,
            'student_class': student.student_class,
            'student_age': student.student_age,
            'student_passwd': student.student_passwd
        }
        return json.dumps(student_info)
    else:
        return None

def get_student_courses(student_id):       # 查询学生选课信息
    student_courses = Enrollment.query.filter_by(student_id=student_id).all()
    if student_courses:
        courses_info = []
        for enrollment in student_courses:
            course = Course.query.filter_by(course_id=enrollment.course_id).first()
            courses_info.append({
                'course_id': course.course_id,
                'course_name': course.course_name,
                'course_time': course.course_time,
                'course_hours': course.course_hours,
                'course_credit': course.course_credit,
                'grade': enrollment.grade
            })
        return courses_info
    else:
        return None






def get_teacher_students_scores(teacher_id):         # 查询老师教授的课程

    teacher_courses = Teach.query.filter_by(teacher_id=teacher_id).all()

    if teacher_courses:
        students_scores = {}
        for teach in teacher_courses:
            # 获取课程ID
            course_id = teach.course_id

            # 查询该课程下的学生及其分数
            enrollments = Enrollment.query.filter_by(course_id=course_id).all()

            for enrollment in enrollments:
                student_id = enrollment.student_id
                grade = enrollment.grade

                # 获取学生姓名
                student_name = Student.query.filter_by(student_id=student_id).first().student_name

                # 存储学生分数
                if course_id in students_scores:
                    students_scores[course_id].append({'student_id': student_id, 'student_name': student_name, 'grade': grade})
                else:
                    students_scores[course_id] = [{'student_id': student_id, 'student_name': student_name, 'grade': grade}]

        return students_scores
    else:
        return None


def update_student_info(student_id, new_info):            # 查询要修改的学生,new_info为键值对
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        for key, value in new_info.items():
            setattr(student, key, value)
        db.session.commit()
        return True
    else:
        return False


def delete_student(student_id):              #删除学生
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        deleted_student_id = student.student_id
        db.session.delete(student)
        db.session.commit()
        # 返回被删除的学生的ID
        return deleted_student_id
    else:
        # 如果找不到匹配的学生，则返回 None
        return None

def get_teacher_students_scores(teacher_id):          #返回该老师所教的全部学生的成绩
    # 使用join()进行表连接查询
    query = db.session.query(Student, Enrollment, Course).\
            join(Enrollment, Student.student_id == Enrollment.student_id).\
            join(Teach, Teach.course_id == Enrollment.course_id).\
            join(Course, Course.course_id == Teach.course_id).\
            filter(Teach.teacher_id == teacher_id).all()

    if query:
        students_scores = {}
        for student, enrollment, course in query:
            student_id = student.student_id
            student_name = student.student_name
            grade = enrollment.grade
            course_name=course.course_name

            course_id = course.course_id
            if course_id in students_scores:
                students_scores[course_id].append({'student_id': student_id, 'course_name':course_name,'student_name': student_name, 'grade': grade})
            else:
                students_scores[course_id] = [{'student_id': student_id, 'course_name':course_name,'student_name': student_name, 'grade': grade}]

        return students_scores
    else:
        return None

def get_student2courses(student_id,course_id,grade=-1):     #学生选课，如果分数未出则设为-1
    courses_chosen = Enrollment.query.filter_by(student_id=student_id).all()

    # 使用列表推导式检查学生是否选择了特定课程
    if any(enrollment.course_id == course_id for enrollment in courses_chosen):
        return None
    else:
        enroll=Enrollment(student_id=student_id,course_id=course_id,grade=grade)
        db.session.add(enroll)

def add_teacher_course(teacher_id, course_id,start_time):   #老师新增任课
    teach_course=Teach.query.filter_by(teacher_id=teacher_id).first()
    if teach_course:
        return None
    else:
        teachc=Teach(teacher_id=teacher_id,course_id=course_id,start_time=start_time)
        db.session.add(teachc)
#----------------------------




# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    with app.app_context():
        print(get_student_info_json(2121001))
        print(get_student_courses(2121001))
        print(get_teacher_students_scores(238901))

        get_student2courses(2121001, 2)
        app.run()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
