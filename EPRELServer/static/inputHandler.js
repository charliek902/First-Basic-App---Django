document.getElementById('clear').addEventListener('click', function(){
  var tableHeader = document.getElementById('tableHeader');
  while (tableHeader.firstChild) {
    tableHeader.removeChild(tableHeader.firstChild);
  }

  var tableBody = document.getElementById('tableBody');
  while (tableBody.firstChild) {
    tableBody.removeChild(tableBody.firstChild);
  }
});



document.getElementById('JSON').addEventListener('click', function(event){
  event.preventDefault();

  // Create a new XMLHttpRequest object
  var xhr = new XMLHttpRequest();

  // Configure the AJAX request
  xhr.open('GET', 'http://localhost:8000/api/data/', true);
  xhr.responseType = 'blob'; // Set the response type to 'blob' for binary data
  xhr.setRequestHeader('Content-Type', 'application/json');

  // Send the AJAX request
  xhr.send();

  // Handle the AJAX response
  xhr.onload = function() {
    if (xhr.status === 200) {
      // Create a download link element
      var downloadLink = document.createElement('a');
      downloadLink.href = window.URL.createObjectURL(xhr.response);
      downloadLink.download = 'output.txt'; // Specify a .txt file extension
      // Trigger the download
      downloadLink.click();
    }
  };
});


document.getElementById('myForm').addEventListener('submit', function(event) {
  event.preventDefault();

  var tableHeader = document.getElementById('tableHeader');
  while (tableHeader.firstChild) {
    tableHeader.removeChild(tableHeader.firstChild);
  }

  var tableBody = document.getElementById('tableBody');
  while (tableBody.firstChild) {
    tableBody.removeChild(tableBody.firstChild);
  }

  var manufacturer = document.getElementById('manufacturer').value.trim();
  var model_number = document.getElementById('model_number').value.trim();
  var filter = document.getElementById('FilterDatabase').value;

  var xhr = new XMLHttpRequest();

  xhr.open('POST', 'http://localhost:8000/api/search/', true);
  xhr.setRequestHeader('Content-Type', 'application/json');

  var data = {
    'manufacturer': manufacturer,
    'model_number': model_number,
    'filter': filter
  };

  var jsonData = JSON.stringify(data);

  // Send the AJAX request with the data
  xhr.send(jsonData);

  // Make the searching feature more dynamic...
  var searchingBar = document.getElementById('searchingBar');
  searchingBar.innerHTML = 'Searching...';
  searchingBar.style.display = 'block';

  xhr.onload = function() {
    if (xhr.status === 200) {
      var response = JSON.parse(xhr.responseText);

      var tableHeader = document.getElementById('tableHeader');

      if (response.data.length === 0) {
        searchingBar.style.display = 'none';
        var tableContainer = document.getElementById('tableContainer');
        const responseMessage = document.createElement('p');
        responseMessage.innerHTML = 'No data corresponds with your request';
        tableContainer.appendChild(responseMessage);
        return;
      }

      else {
        var header1 = document.createElement('th');
        var header2 = document.createElement('th');
        var header3 = document.createElement('th');
        header1.innerText = 'Brand';
        header2.innerHTML = 'Model Number';
        if (filter === 'Overall Energy Class') {
          header3.innerHTML = filter + ' (A-G)';
        } else if (filter === 'Energy Class HDR') {
          header3.innerHTML = filter + ' (A-G)';
        } else if (filter === 'Energy Class SDR') {
          header3.innerHTML = filter + ' (A-G)';
        } else if (filter === 'High Dynamic Range' || filter === 'Standard Dynamic Range') {
          header3.innerHTML = filter + ' (Watts)';
        }
        tableHeader.appendChild(header1);
        tableHeader.appendChild(header2);
        tableHeader.appendChild(header3);
      }

      searchingBar.style.display = 'none';
      const table = document.getElementById('tableBody');

      // Generate table rows
      response.data.forEach(rowData => {
        const tableRow = document.createElement('tr');
        for (const property in rowData) {
          if (Object.hasOwnProperty.call(rowData, property)) {
            const tableCell = document.createElement('td');
            tableCell.textContent = rowData[property];
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

  document.getElementById('myForm').reset();
});


document.getElementById('parse').addEventListener('submit', function(event) {
  event.preventDefault();

  var xhr = new XMLHttpRequest();

  xhr.open('POST', 'http://localhost:8000/api/parse_excel/', true);
  var fileInput = document.getElementById('FileInput');
  var file = fileInput.files[0];

  var data = new FormData();
  data.append('file', file);  // Add the file object to the FormData object

  // Configure the response type to 'blob'
  xhr.responseType = 'blob';


  // Handle the response
  xhr.onload = function() {
    if (xhr.status === 200) {
      // Create a download link element
      var downloadLink = document.createElement('a');
      downloadLink.href = window.URL.createObjectURL(xhr.response);
      downloadLink.download = 'output.xlsx';
      
      // Trigger the download
      downloadLink.click();
    }
  };

  // Send the AJAX request with the FormData object
  xhr.send(data);
});
