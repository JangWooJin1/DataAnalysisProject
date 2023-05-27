import csv
import MySQLdb

# MySQL 연결 정보
host = 'localhost'
user = 'root'
passwd = '1234'
db = 'dataProject'

def makecsv():
    # MySQL 연결
    connection = MySQLdb.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=db
    )
    cursor = connection.cursor()

    # 쿼리 실행
    query = "SELECT * FROM Notice"
    cursor.execute(query)
    results = cursor.fetchall()

    # CSV 파일 저장
    csv_filename = '공지사항.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([i[0] for i in cursor.description])  # 헤더 쓰기
        writer.writerows([str(value) for value in row] for row in results)  # 데이터 쓰기

    cursor.close()
    connection.close()

makecsv()