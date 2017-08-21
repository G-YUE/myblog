$(function () {
        $("#up,#down").click(function () {
            var nid = $(".count").attr("id");
            var type = $(this).attr("id");
            $.ajax(
                {
                    url: "/thumbs/",
                    type: "POST",
                    data: {"type": type, "nid": nid},
                    dataType: "Json",
                    success: function (arg) {
                        $("#message").text(arg.message);
                        if (arg.status == "up") {
                            $("#thumbs_up").text(arg.count)
                        }
                        else if (arg.status == "down") {
                            $("#thumbs_down").text(arg.count)
                        }
                    }
                }
            )
        });

        $('#btn_comment_submit').click(function () {
            var formData = new FormData();
            var nid = $(".count").attr("id");
            var token = $.cookie('csrftoken');
            formData.append('comment_content', $('#tbCommentBody').val());
            formData.append('article_id', nid);

            $.ajax({
                url: '/comment/',
                type: 'POST',
                headers: {'X-CSRFToken': token},
                dataType: 'JSON',
                data: formData,
                contentType: false,
                processData: false,
                success: function (arg) {
                    if (arg.status) {
                        $('#commnet_message').text(arg.message);
                        alert("评论成功！")
                        location.reload();
                    }
                    else {
                        $('#commnet_message').text(arg.message)
                    }

                }
            })
        })


    }
)
