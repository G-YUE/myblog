from django.db import models


class UserInfo(models.Model):
    """
    用户表
    """
    nid = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=64)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    avatar = models.ImageField(verbose_name='头像', upload_to="static/image/", default="static/image/default.jpg")

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    fans = models.ManyToManyField(verbose_name='粉丝们',
                                  to='UserInfo',
                                  through='UserFans',
                                  related_name='f',
                                  through_fields=('user', 'follower'))


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客前缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32, default="blog")
    user = models.OneToOneField(to='UserInfo', to_field='nid')


class UserFans(models.Model):
    """
    互粉关系表
    """
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users')
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers')

    class Meta:
        unique_together = [
            ('user', 'follower'),
        ]


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    content = models.TextField(verbose_name='文章内容', )

    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid')


class UpDown(models.Model):
    """
    文章顶或踩
    """
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid')
    user = models.ForeignKey(verbose_name='赞或踩用户', to='UserInfo', to_field='nid')
    up = models.BooleanField(verbose_name='是否赞')

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey(verbose_name='回复评论', to='self', related_name='back', null=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid')
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid')


class Tag(models.Model):
    """
    个人标签表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')


class Article(models.Model):
    """
    文章表
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章简介', max_length=255)
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')
    category = models.ForeignKey(verbose_name='文章个人类型', to='Category', to_field='nid', null=True)

    type_choices = [
        (1, "Python"),
        (2, "Linux"),
        (3, "GoLang"),
        (4, "Django"),
    ]

    article_type_id = models.IntegerField(verbose_name='文章类型', choices=type_choices, default=None)

    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )


class Article2Tag(models.Model):
    """
    文章标签表
    """
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid')

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]

class Application(models.Model):
    """
    申请开通博客
    """
    nid = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(to='UserInfo', to_field='nid',verbose_name="申请用户")
    text=models.CharField(max_length=128,verbose_name="开通博客理由")
    type_choices = [
        (0, "未处理"),
        (1, "拒绝"),
        (2, "已开通"),
    ]
    status = models.IntegerField(verbose_name='申请状态', choices=type_choices, default=0)
    create_time=models.DateTimeField(auto_now_add=True,verbose_name="申请时间")

class Erweima(models.Model):
    """
    存储二维码唯一标识
    """
    req=models.CharField(max_length=32,verbose_name="二维码唯一标识")
    choice=[(0,0),(1,1)]
    status=models.IntegerField(choices=choice,verbose_name="状态",default=0)
    ctime=models.IntegerField(default=100,verbose_name="超时时间")
    create_time=models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    def __str__(self):
        return "%s-%s"%(self.req,self.choice)

class Login(models.Model):
    """
    二维码和扫码用户绑定
    """
    user=models.ForeignKey("UserInfo",verbose_name="扫码用户")
    erweima=models.ForeignKey("Erweima",verbose_name="二维码")

    def __str__(self):
        return "%s-%S"%(self.user.username,self.erweima.req)