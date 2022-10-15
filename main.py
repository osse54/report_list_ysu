import threading
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import re
from datetime import datetime, timedelta

# 과목리스트가 있는 페이지
courseListPage = 'https://cyber.ysu.ac.kr/Main.do?cmd=moveMenu&mainDTO.parentMenuId=menu_00026&mainDTO.menuId=menu_00031'
driver = webdriver.Chrome('chromedriver.exe')
reg = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
now = datetime.now()
completeImg = '/lmsdata/img_common/icon/set1/icon_full_print.gif'
"""
날짜 연산  
식1 = (강의 마지막 날짜 - 강의 시작 날짜) >= (오늘 - 강의 시작 날짜) # 강의 기간 - 강의 시작한 날짜 // 강의 기간 중인지 알아보는 식 //해당 강의의 수강 기간이 지났다면 False가 나올 것
식2 = (오늘 - 강의 시작 날짜) >= 0 # 강의가 시작했는지 알아보는 식 // 강의가 시작하지 않았다면 음수로 나옴
if 식2:
    if 식1:
        # 여기 온다면 해당 강의(수업)는 현재 수강 기간(출석체크 중 )인 강의
"""

# 홈페이지
driver.get("https://cyber.ysu.ac.kr/index.jsp")

# frame전환으로 홈페이지 접속 시 다른 프레임 포커스로 요소 탐색을 하지 못하는 것을 해결
driver.switch_to.frame('main')

# 로그인
driver.find_element(By.CSS_SELECTOR, '#id').send_keys('')
driver.find_element(By.CSS_SELECTOR, '#pw').send_keys('')
driver.find_element(By.CSS_SELECTOR, '.loginBtn').click()

# 팝업창 닫기
pages = driver.window_handles
for handle in pages:
    if handle != pages[0]:
        driver.switch_to.window(handle)
        driver.close()

# 팝업창 모두 닫은 후 메인 페이지로 포커스 전환
driver.switch_to.window(pages[0])

"""
수강 과목 목록 페이지 접속
테이블에 있는 과목명과 해당 과목 페이지 접속 스크립트로 Dictionary에 추가
과목명 : 과목 접속 스크립트  
"""
driver.get(courseListPage)
tbody = driver.find_element(By.CSS_SELECTOR, 'tbody')
rows = tbody.find_elements(By.CSS_SELECTOR, 'tr')
courseDic = {}
for row in rows:
    courseDic[row.find_element(By.CSS_SELECTOR, '.first').text] = row.find_element(By.CSS_SELECTOR, '.btn.small.fr').get_attribute('href')

# 수강해야 할 강의 목록 탐색 및 과제 탐색, 공지사항 탐색
for course in courseDic.keys():

    # 수강 과목 페이지 Course.do페이지에서 스크립트가 안먹힘
    if driver.current_url != courseListPage:
        driver.get(courseListPage)

    # 페이지 이동
    driver.execute_script(courseDic[course])

    # 강의 목록 태그 찾기
    targetEle = None
    for ele in driver.find_elements(By.CSS_SELECTOR, 'a'):
        if ele.get_attribute('innerHTML') == '강의 목록':

            # 조건 만족으로 반복 중지
            driver.get(ele.get_attribute('href'))
            break

    # 강의 목록에서 각 강의를 정의한 박스들 찾기 // <div>
    eleList = driver.find_elements(By.CSS_SELECTOR, '#listBox')

    # 날짜 텍스트를 가진 박스를 찾아서 강의 목록에 올리기
    for box in eleList:

        # 날짜를 가지고 오는 코드
        tag = box.find_element(By.CSS_SELECTOR, '.f14.fontB')
        lTime = tag.get_attribute('innerHTML')
        dateList = reg.findall(lTime) # dateList[0] = 수강 시작 날짜, dateList[1] = 수강 마지막 날짜

        # 수강 기간인 강의인지 알아내는 코드
        if (now - dateList[0]) >= 0:
            if (dateList[0] - dateList[1]) >= (now - dateList[0]):
                # 수강 기간인 강의로 판단

                # 테이블
                body = box.find_element(By.CSS_SELECTOR, 'tbody')

                # 강의들 긁어오기
                videos = body.find_elements(By.CSS_SELECTOR, 'tr')

                # 강의 갯수 0개 이상일 경우
                if len(videos) > 0:
                    for video in videos:
                        # 수강 완료 여부 - 이미지 위치로 판단
                        if video.find_element(By.CSS_SELECTOR, 'img').get_attribute('src') != completeImg:
                            # 버튼이 없을 시 나오는 예외 넘기기
                            try:
                                btn = video.find_element(By.CSS_SELECTOR, '.btn')
                                
                            except NoSuchElementException as e:
                                
                            except Exception as e:
                                print(e)
                            # TODO 버튼을 인식하는 것까지 완료, TODO리스트를 Dictionary를 이용하여 만들기, 아직 정상적인 실행 하는 지 확은 못함
