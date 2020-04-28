var search = document.getElementById("search");
var senddata = {
    userName: "",
    attendType: "1",  // 打卡类型
    attendState: "1",  // 打卡状态
    startDate: "",  // 开始日期
    endDate: "",  // 结束日期
    page: "1",  // 当前页
    rows: "15",  // 每页多少条数据
};
// 获取输入的名字
$("#name").blur(function () {
    senddata.userName = $(this).val();
});
$(".startTime").blur(function () {
    senddata.startDate = $(this).val();
});
$(".endTime").blur(function () {
    senddata.endDate = $(this).val();
});

search.onclick = function () {
    // 获取打卡类型
    senddata.attendType = $("input[name='attendType']:checked").val();
    senddata.attendState = $("input[name='attendState']:checked").val();
    $.post(baseUrl + "users/get_card_list/",
        senddata,
        function (data, status) {
            if (data["success"] === "false") {
                var dataInfo = [];
                window.dataInfo = dataInfo;
                alert("查询失败")
            } else {
                $("#tbMain").empty();
                var dataInfo = data["rows"];
                window.dataInfo = dataInfo;
                $.each(dataInfo, function (i, json) {
                    if (dataInfo[i]["attendType"] === "1") {
                        attendType = "上班"
                    } else {
                        attendType = "下班"
                    }
                    if (dataInfo[i]["attendState"] === "1") {
                        attendState = "正常"
                    } else if (dataInfo[i]["attendState"] === "2") {
                        attendState = "迟到"
                    } else {
                        attendState = "早退"
                    }
                    var time_list = dataInfo[i]["pushTime"].split("T");
                    var time_time = time_list[1].split(".");
                    var pushTime = time_list[0] + " " + time_time[0];
                    var $tr = $("<tr></tr>");
                    var $td = $(
                        '<td>' + (parseInt(i) + 1).toString() + '</td>' +
                        '<td>' + dataInfo[i]["userName"] + '</td>' +
                        '<td>' + dataInfo[i]["userCode"] + '</td>' +
                        '<td>' + attendType + '</td>' +
                        '<td>' + pushTime + '</td>' +
                        '<td>' + attendState + '</td>'
                    );
                    $tr.append($td);
                    $("#tbMain").append($tr);

                });
            }
        });
};

// 导出数据
function tableToExcel() {
    var jsonData = window.dataInfo;
    //列标题
    let str = '<tr><td>员工id</td><td>员工姓名</td><td>员工编号</td><td>打卡时间</td><td>打卡状态</td><td>打卡类型</td></tr>';
    //循环遍历，每行加入tr标签，每个单元格加td标签
    for (let i = 0; i < jsonData.length; i++) {
        str += '<tr>';
        for (let item in jsonData[i]) {
            //增加\t为了不让表格显示科学计数法或者其他格式
            if (item === 'attendState') {  //打卡状态
                if (jsonData[i][item] === '1') {
                    jsonData[i][item] = "正常"
                } else if (jsonData[i][item] === '2') {
                    jsonData[i][item] = "迟到"
                } else if (jsonData[i][item] === '3') {
                    jsonData[i][item] = "早退"
                } else {
                    jsonData[i][item] = "缺卡"
                }
            }
            if (item === "attendType") {  // 打卡类型
                if (jsonData[i][item] === '1') {
                    jsonData[i][item] = "上班"
                } else {
                    jsonData[i][item] = "下班"
                }

            }
            if (item === "pushTime") {
                var time_list = jsonData[i][item].split("T");
                var time_time = time_list[1].split(".");
                jsonData[i][item] = time_list[0] + " " + time_time[0];
            }
            str += `<td>${jsonData[i][item] + '\t'}</td>`;
        }
        str += '</tr>';
    }
    //Worksheet名
    let worksheet = 'Sheet1'
    let uri = 'data:application/vnd.ms-excel;base64,';

    //下载的表格模板数据
    let template = `<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:x="urn:schemas-microsoft-com:office:excel"
      xmlns="http://www.w3.org/TR/REC-html40">
      <head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet>
        <x:Name>${worksheet}</x:Name>
        <x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet>
        </x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]-->
        </head><body><table>${str}</table></body></html>`;
    //下载模板
    window.location.href = uri + base64(template)
}

//输出base64编码
function base64(s) {
    return window.btoa(unescape(encodeURIComponent(s)))
}