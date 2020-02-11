//get all books and output them in modal window
$("#buttonChoseBooks").click(function () {
	$.ajax({
		url: "http://193.111.0.203:5000/getBooks",
		success: function (data) {
			$("#booksList").children().remove();
			$("#booksList").append( '<div class="row border-bottom border-primary">'  +'<div class="col-sm-1 border-right"> <p class="w-100 text-center">id</p></div>'+ '<div class="col-sm-7 border-right"> <p class="w-100 text-center">name</p></div>'+'<div class="col-sm-3 border-right"> <p class="w-100 text-center">size</p></div>'+'<div class="col-sm-1"> </div>'+'</div>');
			for(var i = 1; i<=Object.keys(data).length; i++){
				var id = data[i]["id"];
				var name = data[i]["name"]
				var size = data[i]["size"]/1024
				var str = '<div class=\"row border-bottom\"><div class=\"col-sm-1 border-right\"> <p class=\"w-100 text-center\">'+id+'</p></div><div class=\"col-sm-7 border-right\"> <p id="book_name_'+id+'" class=\"w-100 text-center\">'+name+'</p></div><div class=\"col-sm-3 border-right\"> <p class=\"w-100 text-center\">'+size.toFixed(1)+'</p></div><div class=\"col-sm-1\"><div class=\"form-check\"> <input class=\"checkBoxBook form-check-input position-static\" type=\"checkbox\" id=\"book_'+id+'\" value=\"option_'+id+'\" aria-label=\"...\"></div></div></div>'
				$("#booksList").append(str);
			}
			$("#booksList").append('<input id="dictID" class="form-control" type="text" placeholder="name">');
		}
	});
})

//change dictionary
$("#buttonChange").click(function () {
	$("#dictionariesList").height(document.documentElement.clientHeight/3);
	$.ajax({
		url: "http://193.111.0.203:5000/getDictionaries",
		type: "GET",
		success: function (data) {
			console.log(data);
			$("#dictionariesList").children().remove();
			//create title
         	var str1 = '<button type="button" class="btn w-100 btn-lg" disabled><div class="row border-bottom border-primary">';
            var str3 ='        <div class="col-sm-2 border-right"> <p class="w-100 text-center">id</p></div>';
            var str4 ='        <div class="col-sm-4 border-right"> <p class="w-100 text-center">name</p></div>';
            var str5 ='        <div class="col-sm-2 border-right"> <p class="w-100 text-center">N</p></div>';
            var str6 ='        <div class="col-sm-2"><p class="w-100 text-center">size</p></div>';
            var str7 ='    </div></button>';
       		var names = [];
       		var sizes = [];
       		var books = [];
       		var allWords = [];
       		var uniqueWords = [];
       		var time = [];
       		var ids = [];
			$("#dictionariesList").append(str1+str3+str4+str5+str6+str7);
			for(var i = 1; i<=Object.keys(data).length; i++){
				var id = data[i]["id"];
         		names[id] = data[i]["name"]; 
         		sizes[id] =  data[i]["collectionSize"]; 
				books[id] = data[i]["booksNum"]; 
				allWords[id] = data[i]["allWords"]; 
				uniqueWords[id] = data[i]["uniqueWords"]; 
				time[id] = data[i]['timeToCreate'] ;
				ids[id] = data[i]['ids'];
				//create all dictionaries
			  	str1 = '<button type="button" id="choose_book_'+id+'"  class="btn w-100"><div class="row  border-bottom border-primary">';
              	str3 ='        <div class="col-sm-2 border-right"> <p class="w-100 text-center">'+id+'</p></div>';
              	str4 ='        <div class="col-sm-4 border-right"> <p class="w-100 text-center">'+names[id]+'</p></div>';
              	str5 ='        <div class="col-sm-2 border-right"> <p class="w-100 text-center">'+books[id]+'</p></div>';
              	str6 ='        <div class="col-sm-2"><p class="w-100 text-center">'+sizes[id].toFixed(1)+' kb</p></div>';
              	str7 ='    </div></button>';
			  	$("#dictionariesList").append(str1+str3+str4+str5+str6+str7);
			  	//event to change dictionary
			  	$(document).on('click', '#choose_book_'+id, function () {
			  		var id = $(this).attr("id").split("_")[2];
					$("#dictName").text(names[id]);
					$("#infoBooksNum").text("Books in collection: "+books[id]);
					$("#infoSize").text("Collection size: "+sizes[id].toFixed(1) + " kb");
					$("#infoAllWords").text("All words: "+allWords[id]);
					$("#infoUniqueWords").text("Unique words: "+uniqueWords[id]);
					$("#infoTime").text("Time to create: "+time[id].toFixed(3) + " s");
					$(".booksNameInInfo").detach();
					var booksName = [];
					var idList = ids[id].split(" ");
					//get books name
					$.ajax({
						url: "http://193.111.0.203:5000/getBooks",
						success: function (data) {
							$(".booksNameInInfo").detach();
							console.log(data);
							var allIds = [];
							for (var i = 1; i <= Object.keys(data).length; i++) {
								allIds[data[i]['id']] = data[i]['name'];
							}
							idList.forEach(el=> booksName[parseInt(el)] =  allIds[parseInt(el)]);
							booksName.forEach(el=> $("#infoColumn").append('<div class="booksNameInInfo row border-bottom border-secondary">'+el+'</div>'));
						}
					});
			  	});
			}		
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})

//show dictionary
$("#showWords").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/getFile",
		data: res,
		success:function (data) {
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/,/g, "<br>"));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})
//show 2-wordIndex
$("#showWords2Index").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/get2WordIndex",
		data: res,
		success:function (data) {
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/, \"/g, "<br> \""));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})

//show permutationIndex
$("#permutationIndex").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/getPermutationIndex",
		data: res,
		success:function (data) {
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/], \"/g, "]<br> \""));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})
//show gramIndex
$("#gramIndex").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/getGramIndex",
		data: res,
		success:function (data) {
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/], \"/g, "]<br><br> \"").replace(/: \[/g, ":<br>\["));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})
$("#coordIndex").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/getCoordIndex",
		data: res,
		success:function (data) {
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/}, \"/g, "}<br><br> \"").replace(/, \"/g, "<br> \"").replace(/: {/g, ":<br>{ \""));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})
//show invert index
$("#showInvertIndex").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/getIndex",
		data: res,
		success:function (data) {
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/, \"/g, "<br> \""));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})

//show matrix
$("#showMatrix").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/getMatrix",
		data: res,
		success:function (data) {
			console.log(data);
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/,/g, "<br>"));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})

//show just matrix
$("#showJustMatrix").click(function () {
	namet = $("#dictName").text();
	var res = {
		name: namet
	};
	$.ajax({
		type:"GET",
		url: "http://193.111.0.203:5000/getMatrix",
		data: res,
		success:function (data) {
			$("#infoZone").height(document.documentElement.clientHeight);
			$("#infoZone").html(data.replace(/\"[^\"]+\": /g, " ").replace(/,/g, "<br>").replace(/\"/g, ""));
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})

//create search input
$("#boolSearch").click(function() {
	$("#infoZone").html('<div class="row"><input type="text" id="searchForm" class="form-control" placeholder="search"> <button type="submit" id = "buttonSearch" class="w-100 btn btn-primary mb-2">Search</button></div>')
})


//boolean search
$(document).on('click', '#buttonSearch', function (e) {
	namet = $("#dictName").text();
	req = $("#searchForm")[0].value;
	booksNum = $("#infoBooksNum").text().split(" ")[3];
	console.log(booksNum);
	var res = {
		name: namet,
		request: req,
		num: booksNum
	};
		$.ajax({
		type:"POST",
		url: "http://193.111.0.203:5000/boolSearch",
		data: res,
		dataType: "json",
		success:function (data) {
			console.log(data[0]);
			$(".searchRes").detach();
			$("#infoZone").append('<div class = "row w-100 searchRes">Time: '+ data['time']+ ' s</div>');
			$("#infoZone").append('<div class = "row w-100 searchRes">Search Result:<br> '+ data['names'].join("<br>").replace(/,/g, "<br>")+ '</div>');
		},
		error:function (argument) {
			console.log(argument);
			$(".searchRes").detach();
			$("#infoZone").append('<div class = "row w-100 searchRes">Search Result:<br> No result</div>');
		}
	});
	})


//create dictionary from books
$("#buttonCreateDictionary").click(function () {
	var checks = $(".checkBoxBook");
	var namet = ($("#dictID").prop("value"));
	var ids = []
	var names = []
	//save names and ids
	checks.each(function (index) {
		if($(this).prop("checked")){
			ids.push($(this).prop("id").split("_")[1]);
			names.push($("#book_name_"+$(this).prop("id").split("_")[1]).text());
		}
	});
	var res = {
		name: namet,
		id: ids
	};
	//send dictionary to server and create it on the server side
	$.ajax({
		type:"POST",
		url: "http://193.111.0.203:5000/createDictionary",
		data: res,
		dataType: "json",
		success:function (data) {
			//change info column
			$(".booksNameInInfo").detach();
			$("#dictName").text(data['name']);
			$("#infoBooksNum").text("Books in collection: "+data['booksNum']);
			$("#infoSize").text("Collection size: "+data['size'].toFixed(1) + " kb");
			$("#infoAllWords").text("All words: "+data['allWords']);
			$("#infoUniqueWords").text("Unique words: "+data['uniqueWords']);
			$("#infoTime").text("Time to create: "+data['time'].toFixed(3) + " s");
			for (var i = 0; i < names.length; i++) {
				$("#infoColumn").append('<div class="booksNameInInfo row border-bottom border-secondary">'+names[i]+'</div>');
			}
		},
		error:function (argument) {
			console.log(argument);
		}
	});
})

// drag and drop upload files
$(document).ready(function() {
	var dropZone = $('#dropZone');
	if (typeof(window.FileReader) == 'undefined') {
	    dropZone.text('error!');
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
	// send fb2 files to server when files are choosed
	dropZone[0].ondrop = function(event) {
	    event.preventDefault();
	    var files = event.dataTransfer.files;
	    sendFiles(files);
	};
	$('#file-input').change(function(event) {
	    var files = event.target.files;
	    sendFiles(files);
	});
	//progress monitoring
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
	//progress monitoring last file
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
	//set normal drag and drop zone state
	function getToNormal() {
		 dropZone.text('');
		 dropZone.removeClass('error');
		 dropZone.removeClass('hover');
	    dropZone.removeClass('drop');
	}
	//send files to server
	function sendFiles(files) {
		$(files).each(function(index, file) {
			//check file format
	        if (file.name.endsWith(".fb2")) {
	    		dropZone.removeClass('hover');
	    		dropZone.addClass('drop');
	    		//create file to send
				let Data = new FormData();
	    		Data.append('path', file);
	    		//create http request
				var xhr = new XMLHttpRequest();
				xhr.upload.addEventListener('progress', uploadProgress, false);
	          	if(index==files.length-1){
	          		xhr.onreadystatechange = stateChangeLast;
	          	}else{
					xhr.onreadystatechange = stateChange;
				}
				xhr.open('POST', 'http://193.111.0.203/InfSearch/Controller/save.php');
				xhr.setRequestHeader('X-FILE-NAME', file.name);
				xhr.send(Data);
	        } 
	    });
	}
});



