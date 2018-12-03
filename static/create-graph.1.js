/*
 * Parse the data and create a graph with the data.
 */
// function parseData(createGraph) {
// 	Papa.parse("static/train_log_loss.txt", {
// 		download: true,
// 		complete: function(results) {
// 			createGraph(results.data);
// 		}
// 	});
// }

// function createGraph(data) {
// 	var iter = [];
// 	var loss = ["loss"];
// 	for (var i = 0; i < data.length-1; i++) {		
// 		var data_s1 = data[i][0].split(":");
// 		var data_s2 = (data[i][1]).split(" ");		
// 		iter.push(data_s1[0]);
// 		loss.push( data_s2[1] );
// 	}
// 	console.log(iter);
// 	console.log(loss);

// 	var chart = c3.generate({
// 		bindto: '#chart',
// 	    data: {
// 	        columns: [
// 	        	loss
// 	        ]
// 	    },
// 	    axis: {
// 	        x: {
// 	            type: 'category',
// 	            categories: iter,
// 	            tick: {
// 	            	multiline: false,
//                 	culling: {
//                     	max: 15
//                 	}
//             	}
// 	        }
// 	    },
// 	    zoom: {
//         	enabled: true
//     	},
// 	    legend: {
// 	        position: 'right'
// 	    }
// 	});
// }

function parseData() {
	Papa.parse("static/train_log_loss.txt", {
		download: true,
		complete: function(results) {
			iter = [];
			var loss = ["loss"];
			for (var i = 0; i < results.data.length-1; i++) {		
				var data_s1 = results.data[i][0].split(":");
				var data_s2 = (results.data[i][1]).split(" ");
				iter.push(data_s1[0]);
				loss.push(data_s2[1]);
			}			
			createGraph(iter, loss);
		}
	});
}

function createGraph(iter, loss) {
	console.log(iter);
			console.log(loss);

	var chart = c3.generate({
		bindto: '#chart',
		data: {
			columns: [
				loss
			]
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

parseData();