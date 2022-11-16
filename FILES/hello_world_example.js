(() => {
	var n = prompt('Program requested value for variable "n": ');
	if(n < 3) {
		console.log("Hello");
		var i = 0;
		[...Array(n - 0)].forEach(() => {
			console.log(i);
			i = i + 1;
		});
	};
})();