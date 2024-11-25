function Search_stock() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("search_name");  // 搜尋框中的輸入
    filter = input.value.toUpperCase();  // 將輸入轉換為大寫，方便比對
    table = document.getElementById("stock_table");  // 找到表格
    tr = table.getElementsByTagName("tr");  // 所有的表格行
  
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {  // 跳過表頭（第0行）
      td = tr[i].getElementsByTagName("td")[1];  // 搜尋第二個單元格（股票名稱/代號）
      if (td) {
        txtValue = td.textContent || td.innerText;  // 獲取單元格中的文本
        if (txtValue.toUpperCase().indexOf(filter) > -1) {  // 搜尋文本中是否包含輸入的值
          tr[i].style.display = "";  // 顯示匹配的行
        } else {
          tr[i].style.display = "none";  // 隱藏不匹配的行
        }
      }
    }
  }
  