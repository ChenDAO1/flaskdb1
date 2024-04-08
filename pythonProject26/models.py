
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

app=Flask(__name__)
class Config:
    SQLALCHEMY_DATABASE_URI='mysql://root:cs626824@127.0.0.1:3306/flaskdb1'
    SQLALCHEMY_TRACK_MODIFICATIONS= True
app.config.from_object(Config)

db=SQLAlchemy(app)

class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(100),primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    telephone = db.Column(db.String(11),nullable=False)
    _password = db.Column(db.String(100),nullable=False)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(25), nullable=False)
    student_sex = db.Column(db.String(5), nullable=False)
    student_major = db.Column(db.String(25), nullable=False)
    student_class = db.Column(db.Integer, nullable=False)
    student_age = db.Column(db.Integer, nullable=False)
    student_passwd = db.Column(db.String(15), nullable=False)

class Teacher(db.Model):
    __tablename__ = 'teacher'
    teacher_id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(50), nullable=False)
    teacher_sex = db.Column(db.String(5), nullable=False)
    teacher_major = db.Column(db.String(25), nullable=False)
    teacher_passwd = db.Column(db.String(25), nullable=False)
    teacher_age = db.Column(db.Integer, nullable=False)

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(50), nullable=False)
    course_time = db.Column(db.String(20), nullable=False)
    course_hours = db.Column(db.Integer, nullable=False)
    course_credit = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'))
    teacher = db.relationship('Teacher', backref=db.backref('courses', lazy=True))

class Teach(db.Model):
    __tablename__ = 'teach'
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), primary_key=True)
    start_time = db.Column(db.Date)
    teacher = db.relationship('Teacher', backref=db.backref('teaches', lazy=True))
    course = db.relationship('Course', backref=db.backref('teaches', lazy=True))

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), primary_key=True)
    grade = db.Column(db.Integer)
    student = db.relationship('Student', backref=db.backref('enrollments', lazy=True))
    course = db.relationship('Course', backref=db.backref('enrollments', lazy=True))

class Administrator(db.Model):
    __tablename__ = 'administrator'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(50), nullable=False)
    admin_sex = db.Column(db.String(5), nullable=False)
    admin_age = db.Column(db.Integer, nullable=False)
    admin_username = db.Column(db.String(25), nullable=False)
    admin_passwd = db.Column(db.String(15), nullable=False)

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

            course_id = course.course_id
            if course_id in students_scores:
                students_scores[course_id].append({'student_id': student_id, 'student_name': student_name, 'grade': grade})
            else:
                students_scores[course_id] = [{'student_id': student_id, 'student_name': student_name, 'grade': grade}]

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

