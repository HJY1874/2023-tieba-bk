"""
表单定义 - 百度百科风格项目
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Article, Comment, Category


class ArticleForm(forms.ModelForm):
    """词条表单"""
    class Meta:
        model = Article
        fields = ['title', 'slug', 'category', 'summary', 'content', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入词条标题'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL标识（英文或数字）'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '请输入词条摘要（可选）',
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '请输入词条详细内容',
                'rows': 15
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': '词条标题',
            'slug': 'URL标识',
            'category': '分类',
            'summary': '摘要',
            'content': '内容',
            'status': '状态',
        }
        help_texts = {
            'slug': '用于URL的标识符，只能包含字母、数字、连字符和下划线',
            'summary': '简要描述词条内容，将在列表页显示',
        }
    
    def clean_slug(self):
        """验证slug字段"""
        slug = self.cleaned_data.get('slug')
        if not slug:
            raise ValidationError('URL标识不能为空')
        
        # 检查slug是否只包含允许的字符
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
            raise ValidationError('URL标识只能包含字母、数字、连字符和下划线')
        
        # 检查slug是否唯一（排除当前实例）
        if self.instance and self.instance.pk:
            if Article.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                raise ValidationError('该URL标识已被使用，请选择其他标识')
        else:
            if Article.objects.filter(slug=slug).exists():
                raise ValidationError('该URL标识已被使用，请选择其他标识')
        
        return slug
    
    def clean_content(self):
        """验证内容字段"""
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 10:
            raise ValidationError('词条内容不能少于10个字符')
        return content


class CommentForm(forms.ModelForm):
    """评论表单"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '请输入您的评论...',
                'rows': 3
            }),
        }
        labels = {
            'content': '评论内容',
        }
    
    def clean_content(self):
        """验证评论内容"""
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 2:
            raise ValidationError('评论内容不能少于2个字符')
        if len(content) > 1000:
            raise ValidationError('评论内容不能超过1000个字符')
        return content


class CategoryForm(forms.ModelForm):
    """分类表单"""
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入分类名称'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '请输入分类描述（可选）',
                'rows': 3
            }),
        }
        labels = {
            'name': '分类名称',
            'description': '分类描述',
        }
    
    def clean_name(self):
        """验证分类名称"""
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('分类名称不能为空')
        
        # 检查分类名称是否唯一（排除当前实例）
        if self.instance and self.instance.pk:
            if Category.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise ValidationError('该分类名称已存在')
        else:
            if Category.objects.filter(name=name).exists():
                raise ValidationError('该分类名称已存在')
        
        return name


class SearchForm(forms.Form):
    """搜索表单"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索词条...'
        }),
        label='搜索'
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='所有分类',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='分类'
    )