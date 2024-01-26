# 기존의 views.py 코드를 수정하여 상대 경로를 설정



# 설치해야할 프레임 워크 = pip install django
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.urls import reverse  # reverse 추가

# 설치할 패키지 : pip install reportlab   << canvas, letter, pdfmetrics, TTfont 라이브러리가 포함되어 있음
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# 설치할 라이브러리2 : pip install PyPDF2 << PdfReader, PdfWriter 라이브러리가 포함되어 있음.
from PyPDF2 import PdfReader, PdfWriter  # PdfFileReader와 PdfFileWriter 대신 이를 사용


import os
import PyPDF2
import io





# 현재 views.py 파일의 위치를 기준으로 상대 경로 설정하기 위한 setting
current_dir = os.path.dirname(__file__)   

# os.path.dirname(path)는 주어진 파일 경로(path)에서 그 파일이 속한 경로까지를 추출함.
# ex) views.py 가 실행되는 '/home/폴더1/폴더2/폴더3/pdf_app/views.py'이 경로에서 /home/폴더1/폴더2/폴더3/pdf_app 을 반환해줌
# __file__ 경로는 현재 파일(views.py)이 실행되고 있는 경로를 나타냄.
# 즉 위 코드는 본인이 속한 view.py 의 경로를 current_dir 변수로 선언함.



"""
[개념 정리]

os = 운영체제와 상호작용하는 표준 "라이브러리" 중 하나
path = os라이브러리 내의 "모듈"로, 시스템 경로와 관련한 함수들을 포함하고 있음

라이브러리란 = 모듈들의 집합
모듈 = 함수, 클래스, 변수 등을 포함하는 단일 py파일 (.py 파일) 다른 Python 프로그램에서도 import 문을 통해 해당 모듈의 기능을 사용할 수 있음

"""





# 현재 스크립트 위치와 폰트 파일 이름을 이용해서 폰트 파일의 절대 경로를 만든다
ttf_path = os.path.join(current_dir, 'NanumGothic.ttf')   # current_dir/NanumGothic.ttf 로 경로를 생성해서 변수로 할당함
pdfmetrics.registerFont(TTFont('NanumGothic', ttf_path))  # 'NanumGothic'는 사용하려는 폰트의 이름


"""
pdfmetrics =  ReportLab 라이브러리의 모듈, PDF 문서 생성 시 폰트와 관련된 다양한 설정과 메트릭스를 다룸
registerFont() = 새로운 폰트를 ReportLab의 폰트 시스템에 등록함 이를 통해 PDF 문서 생성 시 해당 폰트를 사용할 수 있게 됨
"""



# 상대경로에서 각 폴더로 접근하기 위해 폴더의 이름을 리스트[] 로 할당함     
# 리스트(list)와 배열(array)은 같은말임

dirs = ["preview", "preview_test", "preview_test_solution", "lesson", "review_test", "review_test_solution", "bsr_test", "bsr_test_solution"]

# 각 폴더 이름(키=key) 에 제목열에 들어갈 텍스트(값:value)를 딕셔너리로 선언함
dir_titles = {             
    "preview": "Preview",
    "preview_test": "PT",
    "preview_test_solution": "PT 답안",
    "lesson": "진도교재",
    "review_test": "RT",
    "review_test_solution": "RT 답안",
    "bsr_test": "BSR",
    "bsr_test_solution": "BSR 답안",
}



def index(request):           #index라는 함수는, 요청(request)을 받으면,
    all_pdf_files = []        # all_pdf_files 라는 변수를 리스트로 선언하고
    for d in dirs:        # 폴더이름을 순차적으로 불러와서
        pdf_dir = os.path.join(current_dir, d) # 경로 + 폴더이름을 합쳐서 정확한 폴더경로를 변수에 저장
        pdf_files = get_pdf_list(pdf_dir)      # 그 정확한 폴더에 있는 pdf들을 리스트로 만들어서 pdf_files 변수에 저장
        all_pdf_files.append({                 # all_pdf_files 리스트에 (1)열제목 (2)PDF폴더 이름 (3)그 폴더안의 파일들을 {딕셔너리}로 append함. -> 키 : 값의 형태로 저장함
            'title': dir_titles[d],            # (1) tilte키에는 각 폴더별로 dir_titles에 저장해놨던 값이 오게끔
            'dir': d,                          # (2) 폴더이름 키값 저장
            'pdf_files': pdf_files             # (3) 각 PDF 파일 리스트 할당
        })

    return render(request,                         # 요청을 받으면
                'index.html',                      # index.html에서
                {'all_pdf_files': all_pdf_files}   # all_pdf_files(=전자)변수를 요청하면 : 그 값으로 방금 내가 위에서 만든 리스트인 all_pdf_files를 할당해줘
                )


"""

[개념 정리]
리스트에 요소를 추가하는 두가지 메서드
1. append 메서드 : 마지막에 추가해줌
2. insert 메서드 : 사이에 끼워 넣을 수 있음
        fruit = ['apple','banana','kiwi']
        fruit.insert(2,'mango') 
        print(fruit)
        ----------------------------------
        ['apple', 'banana', 'mango', 'kiwi']


"""




def add_text_to_pdf(pdf_path, text):
    # 병합된 PDF를 읽습니다.
    pdf_reader = PdfReader(pdf_path)
    first_page = pdf_reader.pages[0]

    # 첫 페이지에 들어갈 텍스트를 생성합니다.
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    # setFont 메서드를 사용해 폰트와 크기 설정
    c.setFont('NanumGothic', 12)  

    # 문자열의 너비를 계산합니다.
    text_width = c.stringWidth(text, 'NanumGothic', 12)

    # 페이지의 너비와 높이를 가져옵니다.
    page_width, page_height = letter

    # 텍스트를 상단 중앙에 배치하기 위한 x, y 좌표를 계산합니다.
    x = (page_width - text_width) / 2
    y = page_height - 10  # 페이지 높이에서 50 포인트를 뺀 위치에 텍스트를 배치

    c.drawString(x, y, text)
    c.save()

    # 생성한 텍스트를 첫 페이지에 추가합니다.
    packet.seek(0)
    new_pdf = PyPDF2.PdfReader(packet)
    page = new_pdf.pages[0]
    first_page.merge_page(page)

    # 수정된 첫 페이지를 원래의 PDF에 덮어씁니다.
    pdf_writer = PdfWriter()
    pdf_writer.add_page(first_page)

    for i in range(1, len(pdf_reader.pages)):
        page = pdf_reader.pages[i]
        pdf_writer.add_page(page)

    with open(pdf_path, 'wb') as f:
        pdf_writer.write(f)

def merge_pdf(request):
    if request.method == 'POST':
        cover_text = request.POST['cover_text']   # cover_text라는 변수에 POST요청의 바디에서 입력값으로 들어온 cover_text를 할당
        selected_pdfs = request.POST.getlist('pdf_files') # 요청사항에 들어온 값중 pdf_files의 리스트를 변수에 저장하고
        merger = PyPDF2.PdfMerger() # PDF를 합친다?

        for pdf in selected_pdfs:
            dir_name, pdf_name = pdf.split('__', 1)
            pdf_dir = os.path.join(current_dir, dir_name)
            merger.append(os.path.join(pdf_dir, pdf_name))

        output_pdf_path = os.path.join(current_dir, 'merged.pdf')
        merger.write(output_pdf_path)
        merger.close()

        # 입력창(cover_text)에 값이 있을 경우에만 add_text_to_pdf 함수를 호출
        if cover_text.strip():  
            add_text_to_pdf(output_pdf_path, cover_text)

        pdf_url = request.build_absolute_uri(reverse('serve_pdf'))
        return JsonResponse({'message': 'PDFs merged successfully', 'pdf_url': pdf_url})
    else:
        return JsonResponse({'message': 'Invalid request'})

def serve_pdf(request):
    pdf_path = os.path.join(current_dir, 'merged.pdf')
    
    f = open(pdf_path, 'rb')  # 파일을 열고 닫지 않습니다. FileResponse가 닫을 것입니다.
    return FileResponse(f, content_type='application/pdf')

def get_pdf_list(pdf_dir): # 특정 경로를 매개변수로 받아서
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]  # 해당 경로의 모든 파일들의 이름 리스트중,  ".pdf" 로 끝나는 파일들의 이름들로 구성된 리스트를 선언함
    sorted_pdf_files = sorted(pdf_files)  # 오름차순으로 정렬해서 변수 리스트로 할당함
    return sorted_pdf_files  # 그 변수를 반환함

"""
[개념정리]
os.listdir(경로) 는, 해당 경로에 있는 모든 파일과 디렉토리의 "이름"을 리스트로 반환함
endswith('글자') 는, 해당 글자로 끝나는 경우에 true를 반환함

# 리스트 컴프리헨션(List Comprehension) 이란?

for 루프와 조건문을 사용하여 새로운 리스트를 만드는 표현식으로 기본 구조는 아래와 같음
    [expression for item in iterable if condition]   (* if는 선택적임)

        예시) numbers = [1, 2, 3, 4, 5]
             squares = [n ** 2 for n in numbers] = [1,4,9,16,25]
             even_squares = [n ** 2 for n in numbers if n % 2 == 0] = [4,16]

        








"""

# 이렇게 수정하면, 'Lesson_PDFs' 폴더를 프로젝트의 views.py와 같은 위치에 두면 됩니다.
