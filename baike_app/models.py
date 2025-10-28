"""
数据模型定义 - 百度百科风格项目
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    """百科分类模型"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})


class Article(models.Model):
    """百科词条模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='词条标题')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL标识')
    content = models.TextField(verbose_name='词条内容')
    summary = models.TextField(max_length=500, blank=True, verbose_name='摘要')
    
    # 关联关系
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                null=True, blank=True, verbose_name='分类')
    
    # 状态和时间
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, 
                            default='draft', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    
    # 统计信息
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    
    class Meta:
        verbose_name = '词条'
        verbose_name_plural = '词条'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        """保存时自动设置发布时间"""
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class ArticleImage(models.Model):
    """词条图片模型"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, 
                               related_name='images', verbose_name='所属词条')
    image = models.ImageField(upload_to='article_images/', verbose_name='图片')
    caption = models.CharField(max_length=200, blank=True, verbose_name='图片说明')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        verbose_name = '词条图片'
        verbose_name_plural = '词条图片'
    
    def __str__(self):
        return f"{self.article.title} - {self.caption}"


class Tag(models.Model):
    """标签模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    articles = models.ManyToManyField(Article, related_name='tags', blank=True, 
                                     verbose_name='关联词条')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Comment(models.Model):
    """评论模型"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, 
                              related_name='comments', verbose_name='所属词条')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论者')
    content = models.TextField(max_length=1000, verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username} 对 {self.article.title} 的评论"


class Like(models.Model):
    """点赞模型"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, 
                              related_name='likes', verbose_name='所属词条')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='点赞用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        unique_together = ['article', 'user']
    
    def __str__(self):
        return f"{self.user.username} 点赞了 {self.article.title}"