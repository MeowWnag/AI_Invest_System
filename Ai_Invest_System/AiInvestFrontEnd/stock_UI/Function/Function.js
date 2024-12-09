function Search_stock() {
    // 宣告變數
    var input, filter, table, tr, td, i, j, txtValue;

    // 取得搜尋框輸入值
    input = document.getElementById("search_name");
    filter = input.value.toUpperCase(); // 將輸入轉成大寫（不區分大小寫比對）

    // 獲取表格和所有的行
    table = document.getElementById("main_table");
    if (!table) {
        console.error("Error: 表格 'main_table' 不存在！");
        return;
    }
    tr = table.getElementsByTagName("tr");

    // 遍歷表格行，從第1行（忽略表頭）開始
    for (i = 1; i < tr.length; i++) {
        let rowMatch = false; // 預設行不匹配
        td = tr[i].getElementsByTagName("td");

        for (j = 0; j < td.length; j++) { // 遍歷每個單元格
            if (td[j]) {
                txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    rowMatch = true; // 若匹配則設為 true
                    break;
                }
            }
        }

        // 根據是否匹配決定顯示或隱藏行
        tr[i].style.display = rowMatch ? "" : "none";
    }
}
