
$(document).ready(function() {
    var dropZone = $('#dropZone');
    
if (typeof(window.FileReader) == 'undefined') {
    dropZone.text('Не поддерживается браузером!');
    dropZone.addClass('error');
}

dropZone[0].ondragover = function() {
    dropZone.addClass('hover');
    return false;
};
    
dropZone[0].ondragleave = function() {
    dropZone.removeClass('hover');
    return false;
};

dropZone[0].ondrop = function(event) {
    event.preventDefault();
  

    var files = event.dataTransfer.files;
    sendFiles(files);

};


$('#file-input').change(function(event) {
  

    var files = event.target.files;
    sendFiles(files);

});


function uploadProgress(event) {
    var percent = parseInt(event.loaded / event.total * 100);
    dropZone.text('Загрузка: ' + percent + '%');
}

function stateChange(event) {
    if (event.target.readyState == 4) {
        if (event.target.status == 200) {
            dropZone.text('upload was successful!');
        } else {
            dropZone.text('error!');
            dropZone.addClass('error');
 
        }
    }
}
function stateChangeLast(event) {
    if (event.target.readyState == 4) {
        if (event.target.status == 200) {
            dropZone.text('upload was successful!');
            setTimeout(getToNormal, 3000);
        } else {
            dropZone.text('error!');
            dropZone.addClass('error');
 			setTimeout(getToNormal, 3000);
        }
    }
    
}

function getToNormal() {
	 dropZone.text('');
	 dropZone.removeClass('error');
	 dropZone.removeClass('hover');
    dropZone.removeClass('drop');
}

function sendFiles(files) {
	  $(files).each(function(index, file) {
          if (file.name.endsWith(".fb2")) {

    		dropZone.removeClass('hover');
    		dropZone.addClass('drop');

                let Data = new FormData();
   
    Data.append('path', file);

var xhr = new XMLHttpRequest();
xhr.upload.addEventListener('progress', uploadProgress, false);
          if(index==files.length-1){
          	xhr.onreadystatechange = stateChangeLast;
          }else{
xhr.onreadystatechange = stateChange;}
xhr.open('POST', 'http://193.111.0.203/InfSearch/Controller/save.php');
xhr.setRequestHeader('X-FILE-NAME', file.name);
xhr.send(Data);
          } 

     });
	  
}



    });