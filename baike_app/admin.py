"""
Django管理后台配置
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Article, ArticleImage, Tag, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """分类管理"""
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']


class ArticleImageInline(admin.TabularInline):
    """词条图片内联编辑"""
    model = ArticleImage
    extra = 1
    fields = ['image', 'caption']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """词条管理"""
    list_display = ['title', 'author', 'category', 'status', 'view_count', 
                   'like_count', 'created_at', 'published_at']
    list_filter = ['status', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'like_count', 'created_at', 'updated_at']
    
    fieldsets = [
        ('基本信息', {
            'fields': ['title', 'slug', 'author', 'category', 'status']
        }),
        ('内容信息', {
            'fields': ['summary', 'content']
        }),
        ('统计信息', {
            'fields': ['view_count', 'like_count'],
            'classes': ['collapse']
        }),
        ('时间信息', {
            'fields': ['created_at', 'updated_at', 'published_at'],
            'classes': ['collapse']
        }),
    ]
    
    inlines = [ArticleImageInline]
    
    def save_model(self, request, obj, form, change):
        """保存模型时设置作者"""
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """标签管理"""
    list_display = ['name', 'get_article_count', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['articles']
    
    def get_article_count(self, obj):
        """获取关联词条数量"""
        return obj.articles.count()
    get_article_count.short_description = '关联词条数'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理"""
    list_display = ['article', 'author', 'content_preview', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'article__title', 'author__username']
    list_editable = ['is_active']
    
    def content_preview(self, obj):
        """评论内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """点赞管理"""
    list_display = ['article', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['article__title', 'user__username']