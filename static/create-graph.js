var filepath = Server.filepath
function parseData(is_first) {
	console.log("static/task/"+filepath+"/train_log_loss.txt")
	Papa.parse("static/task/"+filepath+"/train_log_loss.txt", {
		download: true,
		complete: function(results) {
			iter = [];
			var loss = ["loss"];
			console.log("~~~~~~~~~!!!!!!!!~~~~~~~~~~");
			console.log(results.data.length);
			console.log("~~~~~~~~~!!!!!!!!~~~~~~~~~~");
			for (var i = 0; i < results.data.length-1; i++) {		
				var data_s1 = results.data[i][0].split(":");
				var data_s2 = (results.data[i][1]).split(" ");
				iter.push(data_s1[0]);
				loss.push(data_s2[1]);
				console.log("= = = = = Data = = = = ")
				console.log(results.data);
				console.log("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");
				console.log(iter);
				console.log(loss);
				console.log("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");
				createGraph(iter, loss);
		   
			}
		}
	});
}

function createGraph(iter, loss) {
	// console.log(iter);
	console.log("~~~~~~~~~~~~~  createGraph  ~~~~~~~~~~~");

	var chart = c3.generate({
		bindto: '#chart',
		data: {
			columns: [loss]
		},
		axis: {
			x: {
				type: 'category',
				categories: iter,
				tick: {
					multiline: false,
					culling: {
						max: 15
					}
				}
			}
		},
		zoom: {
			enabled: true
		},
		legend: {
			position: 'right'
		}
	});
}