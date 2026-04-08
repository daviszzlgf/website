#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb
import pymysql
import os
import sys
import json
import uuid

# 启用CGI错误跟踪
cgitb.enable()

# 数据库配置 - 请修改为您的实际数据库信息
DB_CONFIG = {
    'host': '10.197.1.202',
    'port': 3306,
    'user': 'root',  # 替换为您的数据库用户名
    'password': 'vesystem',  # 替换为您的数据库密码
    'database': 'website',
    'charset': 'utf8mb4'
}

# 上传目录配置
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    """获取数据库连接"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def save_uploaded_file(file_item, upload_folder):
    """保存上传的文件"""
    if not file_item or not file_item.filename:
        return None
    
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(file_item.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_item.file.read())
        
        return file_path
    except Exception as e:
        print(f"文件保存失败: {e}")
        return None

def main():
    # 设置响应头
    print("Content-Type: application/json; charset=utf-8")
    print()
    
    # 获取表单数据
    form = cgi.FieldStorage()
    
    response = {
        'success': False,
        'message': ''
    }
    
    try:
        # 获取基本字段
        name = form.getvalue('name', '').strip()
        gender = form.getvalue('gender', '').strip()
        age = form.getvalue('age', '').strip()
        phone = form.getvalue('phone', '').strip()
        address = form.getvalue('address', '').strip()
        email = form.getvalue('email', '').strip()
        education = form.getvalue('education', '').strip()
        major = form.getvalue('major', '').strip()
        school = form.getvalue('school', '').strip()
        enrollment_date = form.getvalue('enrollmentDate', '').strip()
        
        # 验证必填字段
        required_fields = {
            '姓名': name, 
            '性别': gender, 
            '年龄': age, 
            '电话': phone,
            '地址': address, 
            '邮箱': email, 
            '学历': education,
            '专业': major, 
            '学校': school, 
            '入学时间': enrollment_date
        }
        
        missing_fields = []
        for field_name, field_value in required_fields.items():
            if not field_value:
                missing_fields.append(field_name)
        
        if missing_fields:
            response['message'] = f"以下字段不能为空: {', '.join(missing_fields)}"
            print(json.dumps(response, ensure_ascii=False))
            return
        
        # 处理兴趣爱好
        hobbies_list = []
        hobby_mapping = {
            'hobby1': '计算机编程',
            'hobby2': '网页设计',
            'hobby3': '篮球运动',
            'hobby4': '阅读技术书籍',
            'hobby5': '音乐',
            'hobby6': '摄影'
        }
        
        for hobby_key, hobby_label in hobby_mapping.items():
            if form.getvalue(hobby_key):
                hobbies_list.append(hobby_label)
        
        hobbies = ','.join(hobbies_list)
        
        # 处理照片上传
        photo_file_item = form['photoInput'] if 'photoInput' in form else None
        photo_path = None
        
        if photo_file_item and hasattr(photo_file_item, 'filename') and photo_file_item.filename:
            photo_path = save_uploaded_file(photo_file_item, UPLOAD_FOLDER)
        
        # 连接数据库并插入数据
        connection = get_db_connection()
        if not connection:
            response['message'] = '数据库连接失败'
            print(json.dumps(response, ensure_ascii=False))
            return
        
        cursor = connection.cursor()
        
        sql = """
        INSERT INTO studentinfo 
        (name, gender, age, phone, address, email, photo_path, education, major, school, enrollment_date, hobbies)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            name, gender, int(age), phone, address, email, photo_path,
            education, major, school, enrollment_date, hobbies
        ))
        
        connection.commit()
        student_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        response['success'] = True
        response['message'] = '个人信息提交成功！'
        response['student_id'] = student_id
        
    except Exception as e:
        response['message'] = f'提交失败：{str(e)}'
        # 记录错误到服务器日志
        print(f"Error: {e}", file=sys.stderr)
    
    # 输出JSON响应
    print(json.dumps(response, ensure_ascii=False))

if __name__ == '__main__':
    main()