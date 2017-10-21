
moment.locale("pt-BR");

$(document).ready(function() {

	
	$('select').material_select();
	$('select').change(sendFrequencyAndPeriods);
	let progressBar = $(".progress");
    let card = $("#card-panel");

	const SOCKET_URL = "http://www.consultoriasantana.com.br:5000";

	let candlestick_data = [];
	let slow_ma_data = [];
	let fast_ma_data = [];

	let candlestick = {
		type: "candlestick",
		showInLegend: true,
		name: "Bitcoin Price",
		yValueFormatString: "$#,##0.00",
		dataPoints: candlestick_data
	}

	let slow_ma_line = {
		type: "line",
		showInLegend: true,
		name: "72-EMA",
		yValueFormatString: "$#,##0.00",
		dataPoints: slow_ma_data
	}

	let fast_ma_line = {
		type: "line",
		showInLegend: true,
		name: "17-EMA",
		yValueFormatString: "$#,##0.00",
		dataPoints: fast_ma_data
	}

	let chart = new CanvasJS.Chart("chart-container", {
		animationEnabled: true,
		theme: "light2", 
		exportEnabled: true,
		zoomEnabled:true,
		title:{
			text: "Bitcoin Price"
		},
		axisY: {
			includeZero: false, 
			prefix: "R$",
			title: "Price"
		},
		axisX: {
			labelFormatter: function(e) {
				return CanvasJS.formatDate( e.value, "HH:mm:ss");
			}
		},
		toolTip: {
			shared: true
		},     
		data: [candlestick, slow_ma_line, fast_ma_line]
	});

	function updateChart(json) {
		let timestamps = Object.keys(json);
			
		candlestick_data.length = 0;
		slow_ma_data.length = 0;
		fast_ma_data.length = 0;

		$.each(timestamps, function() {
			let data = json[this];
			
            data["date"] = moment(this.replace("Z","")).tz("America/Recife").toDate();

			candlestick_data.push(createDataPoint(data));

			slow_ma_data.push({x: data["date"], y: parseFloat(data["72-EMA"])});

			fast_ma_data.push({x: data["date"], y: parseFloat(data["17-EMA"])});
		});

		chart.render();
	}

	function createDataPoint(data) {
		return {  
				x: data["date"], 
				y: [
					parseFloat(data["open"]), 
					parseFloat(data["high"]), 
					parseFloat(data["low"]), 
					parseFloat(data["close"])
					]
			   };
	}

	function sendFrequencyAndPeriods() {
		let selectFrequency = $("#select-frequency");
		let selectPeriods = $("#select-periods");
		
		emitRequestEvent(selectFrequency.val(), selectPeriods.val());
        
		progressBar.show();
        card.hide();
	}

	function emitRequestEvent(frequency, periods) {
		periods = parseInt(periods) / parseInt(frequency);
		socket.emit('request analysis data', {freq: `${frequency}T`, 
											  "periods": periods});
	}

	var socket = io.connect(SOCKET_URL);
  
	socket.on('get analysis data', function(jsonString) {
		let json = JSON.parse(jsonString);
		
		updateChart(json);
        
		progressBar.fadeOut();
        card.fadeIn();
	});

	sendFrequencyAndPeriods();
});