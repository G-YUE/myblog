/**
 * Created by YUE on 2017/7/21.
 */
function del(nid,url) {
    x = confirm("确定要删除吗？")
    if (x) {
        $.ajax({
            url: "/manage/"+url+"/del.html/?nid=" + nid,
            type: "GET",
            dataType: "JSON",
            success: function (arg) {
                alert(arg.msg);
                if (arg.status) {
                    window.location.reload();
                }
            }
        })
    }
}

function submitForm() {
    document.getElementById('ifr').onload = loadIframe;
    document.getElementById('f1').submit();

}
function loadIframe() {
    var content = document.getElementById('ifr').contentWindow.document.body.innerText;
    res = JSON.parse(content);
    if (res.status) {
        alert(res.msg);
        if (res.url){
            window.location.href=res.url;
        }
        else{
            window.location.reload();
        }
    } else {
        $(".error").text(res.msg);
    }
}
