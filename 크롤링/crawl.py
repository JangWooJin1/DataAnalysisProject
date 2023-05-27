import MySQLdb
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import random
import re

host = 'localhost'
user = 'root'
passwd = '1234'
db = 'dataProject'

# 페이지타입(pid), 공지리스트(Nlist), 공지이름(Nname), 공지조회수(Nhits), 공지시간(Ntime)
pageType_list = [
    [0, 'div.board_list > ul > li', 'a > div.mark > span', 'a > div.top > p.tit', 'a > div.top > div.info > span:nth-child(3)', 'a > div.top > div.info > span:nth-child(1)'],
    [1, 'table.board > tbody > tr', 'td.td_num > span', 'td.td_tit > a', 'td:nth-child(5)', 'td:nth-child(4)']
]

# 카테고리이름(Cname), 카테고리링크(Clink), 페이지타입(pid)
category_list = [
        ['일반공지', 'http://www.dongguk.edu/article/GENERALNOTICES/list?pageIndex=', 0],
        ['학사공지', 'http://www.dongguk.edu/article/HAKSANOTICE/list?pageIndex=', 0],
        ['장학공지', 'http://www.dongguk.edu/article/JANGHAKNOTICE/list?pageIndex=', 0],
        ['입시공지', 'http://www.dongguk.edu/article/IPSINOTICE/list?pageIndex=', 0],
        ['국제공지', 'http://www.dongguk.edu/article/GLOBALNOLTICE/list?pageIndex=', 0],
        ['학술/행사공지', 'http://www.dongguk.edu/article/HAKSULNOTICE/list?pageIndex=', 0],
        ['행사공지', 'http://www.dongguk.edu/article/BUDDHISTEVENT/list?pageIndex=', 0],
        ['알림사항', 'http://www.dongguk.edu/article/ALLIM/list?pageIndex=', 0],
        ['AI융합대학', 'https://ai.dongguk.edu/article/notice/list?pageIndex=', 1],
        ['컴퓨터공학과', 'https://cse.dongguk.edu/article/notice1/list?pageIndex=', 1],
    ]

def getHtml(url):
    # 변경된 url로 이동하여 크롤링하기 위해 html 페이지를 파싱
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def getNoticeInfo(category, notice):
    # [0:Cid, 1:Cname, 2:Clink, 3:Pid, 4:Pid, 5:Nlist, 6:Nfixed, 7:Nname, 8:Nhits, 9:Ntime]
    page_type = category[4]

    # 고정 공지는 건너뛰기
    is_fixed = notice.select_one(category[6])
    if is_fixed != None: #고정 표시가 없는 경우 (예외처리)
        if (page_type == 0 and is_fixed.get("class") == ["fix"]) or \
                (page_type in [1] and is_fixed.get("class") == ["mark"]):
            return None

    # 게시글 제목
    name_tag = notice.select_one(category[7])
    if name_tag == None:    #제목이 없는 경우 (예외처리)
        return None

    name = name_tag.text.strip()

    # 게시글 조회수
    hits_tag = notice.select_one(category[8])
    if hits_tag == None:    #조회수가 없는 경우 (예외처리)
        return None

    hits = hits_tag.text.strip()

    # 게시글 날짜
    ntime_tag = notice.select_one(category[9])

    if ntime_tag == None:   #게시글 시간이 없는 경우 (예외처리)
        return None

    ntime = ntime_tag.text.strip()

    #### 테스트용 ####
    print("카테고리 : ", category[1])
    print("공지이름 : ", name.replace("\xa0", " "))
    print("조회수 : ", hits)
    print("시간 : ", ntime)

    return category, name.replace("\xa0", " "), hits, ntime

def crawlInitial(category_index=0, page_index=1):
    try:
        connection = MySQLdb.connect(
            host = host,
            user= user,
            passwd= passwd,
            db=db
        )
        cursor = connection.cursor()

        category_list_query = """
            SELECT *
            FROM category
            INNER JOIN pagetype ON category.Pid = pagetype.Pid
        """
        #[0:Cid, 1:Cname, 2:Clink, 3:Pid, 4:Pid, 5:Nlist, 6:Nfixed, 7:Nname, 8:Nhits, 9:Ntime]
        cursor.execute(category_list_query)
        category_list = cursor.fetchall()

        for category in category_list[category_index:]:
            url = category[2]
            page_type = category[4]

            category_index += 1
            page_index = 1

            while True:
                isNext = True

                print('\n----- Current Page : {}'.format(page_index), '------\noriginal url : ' + url)
                # 변경된 url에 페이지 번호를 붙임
                url_change = url + f'{page_index}'
                print('changed url : ' + url_change + '\n-------------------------------------------------')

                # 페이지가 변경됨에 따라 delay 발생 시킴
                time.sleep(random.uniform(4, 7))

                soup = getHtml(url_change)

                # 게시글 리스트 선택
                notice_list = soup.select(category[5])

                for notice in notice_list:
                    #마지막 페이지면 해당 게시판 크롤링 종료 (
                    if (page_type == 0) and notice.find('div', class_='board_empty'):
                        isNext = False
                        break
                    elif (page_type == 1) and notice.find('td', class_='no_data'):
                        isNext = False
                        break

                    notice_info = getNoticeInfo(category, notice)

                    if notice_info is not None: #일반 공지인 경우
                        category, name, hits, ntime = notice_info

                        insert_query = """
                            INSERT INTO notice (Cid, title, hits, time)
                            VALUES (%s, %s, %s, %s)
                        """
                        try:
                            cursor.execute(insert_query, (category[0], name, hits, ntime))
                            connection.commit()

                        except MySQLdb.IntegrityError as e:
                            # 중복된 항목 처리
                            print("이미 삽입된 항목입니다. 건너뜁니다.")


                if isNext:
                    #다음 페이지 탐색
                    page_index += 1
                else:
                    print('------------------ 게시판의 마지막 페이지라 크롤링 종료 ------------------')
                    break

        cursor.close()
        connection.close()

    except Exception as e:
        # 예외 처리
        print('An error occurred:', str(e))
        crawlInitial(category_index-1, page_index-1)

crawlInitial()