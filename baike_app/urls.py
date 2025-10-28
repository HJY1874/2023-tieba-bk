"""
URL路由配置 - 百度百科风格项目
"""
from django.urls import path
from . import views

app_name = 'baike_app'

urlpatterns = [
    # 首页
    path('', views.home, name='home'),
    
    # 词条相关
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('articles/<slug:slug>/like/', views.like_article, name='article_like'),
    path('articles/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    
    # 分类相关
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
]