document.getElementById('clear').addEventListener('click', function(){
  event.preventDefault();
  var tableHeader = document.getElementById('tableHeader');
  if(tableHeader){
    while (tableHeader.firstChild) {
      tableHeader.removeChild(tableHeader.firstChild);
    }
  }

  var tableBody = document.getElementById('tableBody');
  if(tableBody.firstChild){
    while (tableBody.firstChild) {
      tableBody.removeChild(tableBody.firstChild);
    }
    while (tableBody.firstChild) {
      tableBody.removeChild(tableBody.firstChild);
    }
  }

    document.getElementById('myForm').reset();
});

document.getElementById('myForm').addEventListener('submit', function(event) {
  event.preventDefault();

  var tableHeader = document.getElementById('tableHeader');
  if(tableHeader){
    while (tableHeader.firstChild) {
      tableHeader.removeChild(tableHeader.firstChild);
    }
  }

  var tableBody = document.getElementById('tableBody');
  if(tableBody){
    while (tableBody.firstChild) {
      tableBody.removeChild(tableBody.firstChild);
    }
  }

  var manufacturer = document.getElementById('manufacturer').value.trim();
  var model_number = document.getElementById('model_number').value.trim();
  var filter = document.getElementById('FilterDatabase').value;

  var xhr = new XMLHttpRequest();

  xhr.open('POST', 'http://localhost:8000/api/search/', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.setRequestHeader('X-CSRFToken', csrfToken); // Include the CSRF token

  var data = {
    'manufacturer': manufacturer,
    'model_number': model_number,
    'filter': filter
  };

  var jsonData = JSON.stringify(data);

  xhr.send(jsonData);

  // Make the searching feature more dynamic...
  var searchingBar = document.getElementById('searchingBar');
  searchingBar.innerHTML = 'Searching...';
  searchingBar.style.display = 'block';

  var dots = 0;
  setInterval(function() {
    searchingBar.innerHTML = 'Searching' + '.'.repeat(dots);
    dots = (dots + 1) % 4; 
  }, 500);

  xhr.onload = function() {
    if (xhr.status === 200) {
      var response = JSON.parse(xhr.responseText);
      const table = document.getElementById('tableBody');
      table.style.width = "100%"; // Set the table to 100% width

      if(response.error){
        searchingBar.style.display = 'none';
        var tableContainer = document.getElementById('tableBody');
        const responseMessage = document.createElement('p');
        responseMessage.innerHTML = 'No data corresponds with your request. If you are having difficulties, simply search the main brand name such as TCL, LG or samsung and be sure to accurately type in the model number';
        tableContainer.appendChild(responseMessage);
      }

      if (response.data.length === 0) {
        searchingBar.style.display = 'none';
        var tableContainer = document.getElementById('tableBody');
        const responseMessage = document.createElement('p');
        responseMessage.innerHTML = 'No data corresponds with your request. If you are having difficulties, simply search the main brand name such as TCL, LG or samsung and be sure to accurately type in the model number';
        tableContainer.appendChild(responseMessage);
        return;
      }
      else {
        var header1 = document.createElement('th');
        header1.style.color = "white"
        header1.style.width = "100vh"

        var header2 = document.createElement('th');
        header2.style.color = "white"
        header2.style.width = "100vh"
        var header3 = document.createElement('th');
        header3.style.color = "white"
        header3.style.width = "100vh"
        header1.innerText = 'Brand';
        header2.innerHTML = 'Model Number';

        if (filter === 'Overall Energy Class') {
          header3.innerHTML = filter + ' (A-G)';
        } else if (filter === 'Energy Class HDR') {
          header3.innerHTML = filter + ' (A-G)';
        } else if (filter === 'Energy Class SDR') {
          header3.innerHTML = filter + ' (A-G)';
        } else if (filter === 'High Dynamic Range' || filter === 'Standard Dynamic Range') {
          header3.innerHTML = filter + ' (Watts per second)';
        }
        table.appendChild(header1);
        table.appendChild(header2);
        table.appendChild(header3);
      }

      searchingBar.style.display = 'none';

      response.data.forEach(rowData => {
        const tableRow = document.createElement('tr');
        for (const property in rowData) {
          if (Object.hasOwnProperty.call(rowData, property)) {
            const tableCell = document.createElement('td');
            tableCell.textContent = rowData[property];
            tableCell.style.color = "white"
            tableCell.style.width = "100vh";
            tableRow.appendChild(tableCell);
          }
        }
        table.appendChild(tableRow);
      });

    } else {
      console.error('Error:', xhr.status);
      var errorResponse = JSON.parse(xhr.responseText);
      console.log(errorResponse);
    }
  };
});





