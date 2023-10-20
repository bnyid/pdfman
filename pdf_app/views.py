# 기존의 views.py 코드를 수정하여 상대 경로를 설정

from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.urls import reverse  # reverse 추가
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter  # PdfFileReader와 PdfFileWriter 대신 이를 사용
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import PyPDF2
import io





# 현재 views.py 파일의 위치를 기준으로 상대 경로 설정
current_dir = os.path.dirname(__file__)
# 현재 스크립트 위치와 폰트 파일 이름을 이용해서 폰트 파일의 절대 경로를 만든다
ttf_path = os.path.join(current_dir, 'NanumGothic.ttf')
pdfmetrics.registerFont(TTFont('NanumGothic', ttf_path))  # 'NanumGothic'는 사용하려는 폰트의 이름


# 각 디렉토리에 대한 상대 경로 설정
dirs = ["preview", "preview_test", "preview_test_solution", "lesson", "review_test", "review_test_solution", "bsr_test", "bsr_test_solution"]
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

def index(request):
    all_pdf_files = []
    for d in dirs:
        pdf_dir = os.path.join(current_dir, d)
        pdf_files = get_pdf_list(pdf_dir)
        all_pdf_files.append({
            'title': dir_titles[d],
            'dir': d,
            'pdf_files': pdf_files
        })

    return render(request, 'index.html', {'all_pdf_files': all_pdf_files})

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
    y = page_height - 8  # 페이지 높이에서 50 포인트를 뺀 위치에 텍스트를 배치

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
        cover_text = request.POST['cover_text']
        selected_pdfs = request.POST.getlist('pdf_files')
        merger = PyPDF2.PdfMerger()

        for pdf in selected_pdfs:
            dir_name, pdf_name = pdf.split('__', 1)
            pdf_dir = os.path.join(current_dir, dir_name)
            merger.append(os.path.join(pdf_dir, pdf_name))

        output_pdf_path = os.path.join(current_dir, 'merged.pdf')
        merger.write(output_pdf_path)
        merger.close()

        # cover_text가 비어 있지 않을 경우에만 add_text_to_pdf 함수를 호출
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

def get_pdf_list(pdf_dir):
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    sorted_pdf_files = sorted(pdf_files)  # 오름차순으로 정렬
    return sorted_pdf_files

# 이렇게 수정하면, 'Lesson_PDFs' 폴더를 프로젝트의 views.py와 같은 위치에 두면 됩니다.
