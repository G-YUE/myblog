function changeCode() {
    $("#code").prop("src", $("#code").prop("src") + "?");
}
$(function () {
    bindAvatar();
});
function bindAvatar() {
    if (window.URL.createObjectURL) {
        bindAvatar2();
    } else(window.FileReader)
    {
        bindAvatar3()
    }
}

/*
 本地上传预览
 */
function bindAvatar2() {
    $('#imgSelect').change(function () {
        var obj = $(this)[0].files[0];

        var v = window.URL.createObjectURL(obj);
        $('#previewImg').attr('src', v);
        $('#previewImg').load(function () {
        window.URL.revokeObjectURL(v); //从内存中释放
        });

    })
}

function bindAvatar3() {
    $('#imgSelect').change(function () {
        var obj = $(this)[0].files[0];
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#previewImg').attr('src', this.result);
        };
        reader.readAsDataURL(obj);
    })
}