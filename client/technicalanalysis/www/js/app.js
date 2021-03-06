
moment.locale("pt-BR");

$(document).ready(function() {

	let inputPeriods = $('#input-periods');
	let inputTimeFrame = $('#input-time-frame');
	let inputCurrency = $('#input-currency');

	inputTimeFrame.material_select();
	inputTimeFrame.change(sendTimeFrameAndPeriods);
	inputPeriods.change(sendTimeFrameAndPeriods);
    
	let progressBar = $(".progress");
    let chartContainer = $("#chart-container");

	const SOCKET_URL = "http://consultoriasantana.com.br:5000";
	const SPACE_BETWEEN_POINTS = 17;

	let candlestick_data = [];
	let slow_ma_data = [];
	let fast_ma_data = [];
	let trend_line_data = [];

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

	let trend_line = {        
		type: "line",   
		showInLegend: true,    
		dataPoints: trend_line_data
	}

	let chart = new CanvasJS.Chart("chart-container", {
		animationEnabled: true,
		theme: "light2", 
		zoomEnabled:true,
		title:{
			text: "Bitcoin Price"
		},
		axisY: {
			includeZero: false, 
			prefix: "$",
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
		data: [candlestick, slow_ma_line, fast_ma_line, trend_line]
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
        
            
		progressBar.fadeOut();
        chartContainer.fadeIn();
		initializeChart();
	}

	function createDataPoint(data) {
		let color = null;
		let legend = null;

		if(data["peak-point"]) {
			color = "green";
			legend = "Peak";
		} else if(data["trough-point"]) {
			color = "orange";
			legend = "Trough";
		}

		return {  
				x: data["date"], 
				y: [
					parseFloat(data["open"]), 
					parseFloat(data["high"]), 
					parseFloat(data["low"]), 
					parseFloat(data["close"])
					],
				color: color,
				legendMarkerColor: color,
				legendText: legend,
				click: drawLineBetweenPoints,
			   };
	}
	
	function drawLineBetweenPoints(e) {
		let dataPoint = e.dataPoint;
		let index = e.dataPointIndex;
		let dataPointIndex = index;

		trend_line_data.length = 0;
		if(dataPoint.color) {
			trend_line.name = dataPoint.legendText;
			while (index < candlestick_data.length - 1){
				index += 1;
				
				let nextDataPoint = candlestick_data[index];
				let distance = index - dataPointIndex;
				
				if(dataPoint.color == nextDataPoint.color && distance >= SPACE_BETWEEN_POINTS  ) {
					
					trend_line_data.push({x: dataPoint.x, y: dataPoint.y[3]})
					trend_line_data.push({x: nextDataPoint.x, y: nextDataPoint.y[3]});
					dataPoint = nextDataPoint;
					dataPointIndex = index;
				}
			}

			initializeChart();
		}
	}

	function sendTimeFrameAndPeriods() {

		emitRequestEvent(inputTimeFrame.val(), inputPeriods.val(), 
			inputCurrency.val());
        
		progressBar.show();
        chartContainer.hide();
	}

	function emitRequestEvent(timeFrame, periods, currency) {

		socket.emit('request analysis data', {time_frame: timeFrame, 
											  "periods": periods,
											  "currency": currency});
	}

	function initializeChart() {
        chart.render();
        let buttonClasses = "white-text btn yellow darken-4 white-text";
        $(".canvasjs-chart-toolbar button").addClass(buttonClasses);
    }

    function initialize() {

    	$.get(`${SOCKET_URL}/currencies`, function(response) {
    		
    		$.each(response, function() {
    			var key = Object.keys(this)[0];
    			var value = this[key];
    			var option = $("<option>");
    			option.val(value);
    			option.text(key);
    			inputCurrency.append(option);
    		});

    		inputCurrency.material_select();
    		inputCurrency.change(sendTimeFrameAndPeriods);

			sendTimeFrameAndPeriods();
    	});
    }

	var socket = io.connect(SOCKET_URL);
  
	socket.on('get analysis data', function(jsonString) {
		let json = JSON.parse(jsonString);
		
		updateChart(json);
	});

	initialize();

});
