from django.urls import path
from . import views

urlpatterns = [                                               # URL 주소와 이를 처리할 뷰 함수 간의 매핑을 설정함.
    path('', views.index, name='index'),                      # path 함수는 웹 애플리케이션의 루트 URL ('')을 처리하는 함수로, ('URL',views.함수이름,name='URL패턴의 이름') 임. name은 index에서 이 URL를 참조할때 사용됨
                                                              # 빈문자열 '' 은 루트경로를 나타냄. 즉, 현재 웹주소를 나타내므로, 웹사이트 접속했을 때 바로 실행되도록 함수를 연결한 것이다.
    path('merge-pdf/', views.merge_pdf, name='merge_pdf'),    # ="merge_pdf/ 경로에 대해서 views.py에 있는 merge_pdf 함수를 연결해줘. 이 연결하는 패턴의 이름은 merge_pdf 야."" 
    path('serve-pdf/', views.serve_pdf, name='serve_pdf'),
]
