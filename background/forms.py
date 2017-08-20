from django.core.exceptions import ValidationError
from django import forms
from django.forms import fields
from django.forms import widgets
from app01 import models


class Article(forms.Form):
    title = fields.CharField(min_length=2, max_length=32, error_messages={
        'min_length': "标题至少两个字",
        'max_length': "标题最多32个字",
        'required': '标题不能为空',
    })
    summary = fields.CharField(max_length=64,error_messages={
        'required':"简介不能为空",
        'max_length':"简介最多64个字",

    })
    content = fields.CharField(widget=widgets.Textarea(attrs={"id": "i1"}),error_messages={
        "required":"文章内容不能为空！！"
    })

    article_type_id=fields.ChoiceField(widget=widgets.RadioSelect(),choices=models.Article.type_choices,error_messages={
        "required":"此项必选！"
    })
    category_id=fields.ChoiceField(required=False,widget=widgets.RadioSelect())
    tag_id=fields.MultipleChoiceField(required=False,widget=widgets.CheckboxSelectMultiple())

    def __init__(self,blog_obj,*args,**kwargs):
        super(Article,self).__init__(*args,**kwargs)
        self.user_id=blog_obj.nid
        self.fields['article_type_id'].choices = models.Article.type_choices
        self.fields['category_id'].choices = models.Category.objects.filter(blog_id=self.user_id).values_list("nid","title")
        self.fields['tag_id'].choices = models.Tag.objects.filter(blog_id=self.user_id).values_list("nid","title")