document.getElementById('parse').addEventListener('submit', function(event) {
    event.preventDefault();
  
    var xhr = new XMLHttpRequest();

    xhr.open('POST', parserUrl, true);
    xhr.setRequestHeader('X-CSRFToken', csrfToken); // Include the CSRF token
    var fileInput = document.getElementById('FileInput');
    var file = fileInput.files[0];
  
    var data = new FormData();
    data.append('file', file);  // Add the file object to the FormData objec
  
    xhr.send(data);

    xhr.responseType = 'blob';
  
    xhr.onload = function() {
      if (xhr.status === 200) {
        // Create a download link element
        var downloadLink = document.createElement('a');
        downloadLink.href = window.URL.createObjectURL(xhr.response);
        downloadLink.download = 'output.xlsx';
        
        downloadLink.click();
      }
      
      /*
      elif (xhr.status === 500){
        console.log('gets here');
        var errorResponse = document.createElement('p');
        errorResponse.innerHTML = 'Error when parsing. Refer to the documentation page';
        var space = document.getElementById('parseError');
        space.append(errorResponse);
      }
      */
    };
  });


  
