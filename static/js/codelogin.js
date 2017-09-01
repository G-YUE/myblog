/**
 * Created by YUE on 2017/9/1.
 */

$("#code").click(function () {
    $(this).addClass("hide");
    $("#userpa").removeClass("hide");
    $("#style1").addClass("hide");
    $("#style2").removeClass("hide");
    getcode()
});
$("#userpa").click(function () {
    $(this).addClass("hide");
    $("#code").removeClass("hide");
    $("#style2").addClass("hide");
    $("#style1").removeClass("hide");
    clearInterval(dingshi);
});

function getcode() {
    $.ajax(
        {
            url: "/erweima/",
            type: "GET",
            dataType: "JSON",
            success: function (res) {
                var equel = res["req"];
                var img_url = res["url"];
                $("#erweima").attr("src", img_url);
                wait(equel);
                dingshi = setInterval(function () {
                    wait(equel)
                }, 3000)
            }
        }
    );
}

function wait(equel) {
    var token = $.cookie('csrftoken');
    $.ajax(
        {
            url: "/erweima/",
            type: "POST",
            headers:{'X-CSRFToken':token},
            data: {"req": equel},
            dataType: "JSON",
            success: function (res) {
                if (res.status) {
                    if (res.msg != null) {
                        var img_url = res.msg;
                        $("#erweima").attr("src", img_url);
                        clearInterval(dingshi);
                        window.location.href="/";
                    }
                }
                else {
                    if (res.msg != null) {
                        clearInterval(dingshi);
                        alert(res.msg)
                    }
                }
            }
        }
    )
}