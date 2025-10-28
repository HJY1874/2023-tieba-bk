"""
视图函数定义 - 百度百科风格项目
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from .models import Article, Category, Comment, Like, Tag
from .forms import ArticleForm, CommentForm


class ArticleListView(ListView):
    """词条列表视图"""
    model = Article
    template_name = 'baike_app/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        """获取已发布的词条"""
        queryset = Article.objects.filter(status='published').select_related('author', 'category')
        
        # 分类筛选
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # 搜索功能
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """添加上下文数据"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ArticleDetailView(DetailView):
    """词条详情视图"""
    model = Article
    template_name = 'baike_app/article_detail.html'
    context_object_name = 'article'
    
    def get_object(self, queryset=None):
        """获取词条对象并增加浏览次数"""
        obj = super().get_object(queryset)
        if obj.status == 'published':
            obj.view_count += 1
            obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        """添加上下文数据"""
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.filter(is_active=True).select_related('author')
        
        # 检查用户是否已点赞
        if self.request.user.is_authenticated:
            context['user_has_liked'] = Like.objects.filter(
                article=self.object, 
                user=self.request.user
            ).exists()
        else:
            context['user_has_liked'] = False
            
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """创建词条视图"""
    model = Article
    form_class = ArticleForm
    template_name = 'baike_app/article_form.html'
    success_url = reverse_lazy('article_list')
    
    def form_valid(self, form):
        """表单验证通过时设置作者"""
        form.instance.author = self.request.user
        messages.success(self.request, '词条创建成功！')
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    """编辑词条视图"""
    model = Article
    form_class = ArticleForm
    template_name = 'baike_app/article_form.html'
    
    def get_success_url(self):
        """成功后跳转到词条详情页"""
        messages.success(self.request, '词条更新成功！')
        return reverse_lazy('article_detail', kwargs={'slug': self.object.slug})
    
    def dispatch(self, request, *args, **kwargs):
        """检查权限"""
        obj = self.get_object()
        if obj.author != request.user and not request.user.is_superuser:
            messages.error(request, '您没有权限编辑此词条！')
            return redirect('article_detail', slug=obj.slug)
        return super().dispatch(request, *args, **kwargs)


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    """删除词条视图"""
    model = Article
    template_name = 'baike_app/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')
    
    def dispatch(self, request, *args, **kwargs):
        """检查权限"""
        obj = self.get_object()
        if obj.author != request.user and not request.user.is_superuser:
            messages.error(request, '您没有权限删除此词条！')
            return redirect('article_detail', slug=obj.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """删除成功提示"""
        messages.success(request, '词条删除成功！')
        return super().delete(request, *args, **kwargs)


@login_required
def like_article(request, slug):
    """点赞词条"""
    article = get_object_or_404(Article, slug=slug)
    
    # 检查是否已点赞
    like, created = Like.objects.get_or_create(
        article=article, 
        user=request.user
    )
    
    if not created:
        # 如果已点赞，则取消点赞
        like.delete()
        article.like_count -= 1
        liked = False
    else:
        # 新点赞
        article.like_count += 1
        liked = True
    
    article.save(update_fields=['like_count'])
    
    return redirect('article_detail', slug=slug)


@login_required
def add_comment(request, slug):
    """添加评论"""
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            messages.success(request, '评论添加成功！')
    
    return redirect('article_detail', slug=slug)


def category_list(request):
    """分类列表视图"""
    categories = Category.objects.all()
    return render(request, 'baike_app/category_list.html', {'categories': categories})


class CategoryDetailView(DetailView):
    """分类详情视图"""
    model = Category
    template_name = 'baike_app/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        """添加上下文数据"""
        context = super().get_context_data(**kwargs)
        articles = Article.objects.filter(
            category=self.object, 
            status='published'
        ).select_related('author')
        
        # 分页
        paginator = Paginator(articles, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # 统计信息
        total_views = articles.aggregate(total_views=models.Sum('view_count'))['total_views'] or 0
        total_likes = articles.aggregate(total_likes=models.Sum('like_count'))['total_likes'] or 0
        
        # 热门词条（按浏览次数排序）
        popular_articles = articles.order_by('-view_count')[:5]
        
        # 最新词条
        recent_articles = articles.order_by('-created_at')[:5]
        
        context['articles'] = page_obj
        context['page_obj'] = page_obj
        context['total_views'] = total_views
        context['total_likes'] = total_likes
        context['popular_articles'] = popular_articles
        context['recent_articles'] = recent_articles
        return context


def home(request):
    """首页视图"""
    # 获取热门词条（按浏览次数排序）
    popular_articles = Article.objects.filter(
        status='published'
    ).order_by('-view_count')[:5]
    
    # 获取最新词条
    latest_articles = Article.objects.filter(
        status='published'
    ).order_by('-created_at')[:5]
    
    # 获取所有分类
    categories = Category.objects.all()[:8]
    
    context = {
        'popular_articles': popular_articles,
        'latest_articles': latest_articles,
        'categories': categories,
    }
    
    return render(request, 'baike_app/home.html', context)