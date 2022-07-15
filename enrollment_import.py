import csv
import psycopg2
from datetime import date

conn_string = "host='10.1.10.26' dbname='prod' user='openerp' password='OpenErpAdmin001'"
#conn_string = "host='localhost' dbname='aun' user='michael' password=''"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# reader = csv.reader(open('mycsv.csv','rb'))
statement = "select id, level_id,quality_points,attempted,passed,earned,gpa,default_grade,repeat_indicator,refund from aun_registrar_grade ORDER by name ASC "
cursor.execute(statement)
conn.commit()
grade_info = cursor.fetchall()

statement = "DELETE FROM aun_registrar_level_grade"
cursor.execute(statement)
conn.commit()

for g in grade_info:
    default = g[7]
    refund = g[9]
    if not default:
        default=False
    if not refund:
        refund=False
    statement = "INSERT INTO aun_registrar_level_grade(grade_id,level_id,quality_points,attempted,passed,earned,gpa,default_grade,repeat_indicator,refund) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(g[0],g[1],g[2],g[3],g[4],g[5],g[6],default,g[8],refund)
    cursor.execute(statement)
    conn.commit()


    
# statement = "SELECT DISTINCT name FROM aun_registrar_grade ORDER by name ASC"
# cursor.execute(statement)
# conn.commit()
# grade = cursor.fetchall()
# 
# for a in grade:
#     print a[0]
#     statement = "INSERT INTO aun_registrar_grade(name,grademode_id,status_indicator,numeric_value,web_indicator,midterm,active) VALUES ('%s','%s')" %(c[0], c[1])















# course_statement = "select id, level_id, status_id from aun_registrar_course"
# cursor.execute(course_statement)
# conn.commit()
# course_info = cursor.fetchall()
# 
# statement = "DELETE FROM rel_course_level"
# cursor.execute(statement)
# conn.commit()
# 
# statement = "DELETE FROM rel_course_status"
# cursor.execute(statement)
# conn.commit()
# 
# for c in course_info:
#     
#     statement = "INSERT INTO rel_course_level(course_id,level_id) VALUES ('%s','%s')" %(c[0], c[1])
#     cursor.execute(statement)
#     conn.commit()
#     
#     statement = "INSERT INTO rel_course_status(course_id,status_id) VALUES ('%s','%s')" %(c[0], c[2])
#     cursor.execute(statement)
#     conn.commit()
#     
# status_statement = "select id, level_id, status_id from aun_registrar_section"
# cursor.execute(status_statement)
# conn.commit()
# status_info = cursor.fetchall()
# 
# statement = "DELETE FROM rel_section_level"
# cursor.execute(statement)
# conn.commit()
# 
# statement = "DELETE FROM rel_section_status"
# cursor.execute(statement)
# conn.commit()
# 
# for s in status_info:
#     
#     statement = "INSERT INTO rel_section_level(section_id,level_id) VALUES ('%s','%s')" %(s[0], s[1])
#     cursor.execute(statement)
#     conn.commit()
#     
#     statement = "INSERT INTO rel_section_status(section_id,status_id) VALUES ('%s','%s')" %(s[0], s[2])
#     cursor.execute(statement)
#     conn.commit()
    
# print 'It is finished!! Good Morning Linor!!!'


# for enr in enr_info:
#     l_statement = "SELECT id,level_id,term_id from aun_registrar_section where id='%s'" %enr[0]
#     s_statement = "SELECT id,student_state_id from res_partner where id='%s'" %enr[1]
#     cursor.execute(l_statement)
#     conn.commit()
#     section_info = cursor.fetchone()
#     cursor.execute(s_statement)
#     conn.commit()
#     student_info = cursor.fetchone()
#     
#     lg_statement = "SELECT id from level_gpa where student_id='%s' and level_id='%s'" %(student_info[0], section_info[1])
#     cursor.execute(lg_statement)
#     conn.commit()
#     level_gpa_id = cursor.fetchone()
#      
#     if not level_gpa_id:
#         lg_create = "INSERT INTO level_gpa (student_id,level_id,student_state_id) VALUES (" + str(student_info[0]) + "," + str(section_info[1]) + "," + str(student_info[1]) + ") Returning id"
#         cursor.execute(lg_create)
#         conn.commit()
#         level_gpa_id = cursor.fetchone()
#      
#     enr_insert = "update aun_registrar_enrollment set level_gpa_id=%s where student_id=%s and section_id=%s" %(level_gpa_id[0], student_info[0], section_info[0])
#     cursor.execute(enr_insert)
#     conn.commit()
#     gi_insert = "update gpa_info set level_gpa_id=%s where student_id=%s and term_id=%s" %(level_gpa_id[0], student_info[0], section_info[2])
#     cursor.execute(gi_insert)
#     conn.commit()
#     print enr