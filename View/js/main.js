$("#change").click(function function_name(argument) {

});
$.ajax({
	type: "GET",
	url: "http://193.111.0.203:5000",
	success: function (data) {
		console.log(data);
	},
	error: function(error){
		console.log(error);
	}


});