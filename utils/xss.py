from bs4 import BeautifulSoup

def xss(old):
    valid_tag = {
        'p': ['class','id'],
        'img':['src'],
        'div': ['class'],
        'strong':[],
        'em':[],
        'h1':[],
        'h2':[],
        'h3':[],
        'h4':[],
        'h5':[],
        'a':[],
        'pre':[],
        'code':[],
    }
    soup = BeautifulSoup(old,'html.parser')

    tags = soup.find_all()
    for tag in tags:
        if tag.name not in valid_tag:
            tag.decompose()
        if tag.attrs:
            for k in list(tag.attrs.keys()):
                if k not in valid_tag[tag.name]:
                    del tag.attrs[k]
    content_str = soup.decode()
    return content_str
