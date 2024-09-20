let utilityChart;
const utilityChartLocation = document.getElementById('utilityChart').getContext('2d');

function drawUtilityChart(){   
    if(utilityChart){
        utilityChart.destroy();     // Destroy it to prevent redrawing issues 
    }

    if (utilityValues.length === 0 || utilityValues.every(value => value === 0)){      // No data/everything is 0 we will draw a blank chart with the no data message
        // No idea why .update() does not redraw it with an empty template despite clearing values and labels and why drawNoDataChart doesn't appear for July
        // Workaround: Make a blank chart and slap the no data message on top of there 
        utilityChart = new Chart(utilityChartLocation, {
            type: 'pie',
            data: {
                labels: [],     // No labels
                datasets: [{
                    data: []        // No data
                }]
            },
            options: {
                plugins: {
                    legend: {
                        display: false      // Hide legend
                    }
                }
            }
        });
        drawUtilityNoDataChart(utilityChart, "No Data For This Month");        // Place this on top of the empty chart
    }else{      // Draw chart normally with data
        utilityChart = new Chart(utilityChartLocation, {
            type: 'pie',
            data: {     
                labels: utilityLabels,
                datasets: [{
                    label: 'Utilities Breakdown',
                    data: utilityValues,
                    backgroundColor: ['#ff9999', '#66b3ff', '#99ff99'],  
                    borderWidth: 2,
                    hoverOffset: 4      // To make it look like it is moving out of the chart as you hover over it
                }]
            },
            options: {
                plugins: {
                    legend: {
                        display: false
                    },
                    datalabels:{        
                        color: '#000',
                        display: true,
                        // Grabs the label from the array at an index and displays it on the chart
                        formatter: function(value, context){    // value is data value (price) and context is basically all the other data you can access
                            return context.chart.data.labels[context.dataIndex];    // .chart to access the chart, .data to the data, .labels to refer to the labels on the chart
                        },
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        anchor: 'center',
                        align: 'center',
                    },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            label: function(data){
                                const value = data.raw || 0.0;
                                return `$${value.toFixed(2)}`;      // Display the utility cost
                            },
                            title: function(){
                                return '';      // To get rid of the title part of the tooltip message because it seemed redundant to display the utility name 2x
                            }
                        }
                    }
                }
            },
            plugins: [ChartDataLabels]      // To include ChartDataLabels (a plugin that lets you to place labels directly on the chart)
        });
    }
}

function drawUtilityNoDataChart(chart, message) {
    const chart_data = chart.ctx;       // Grabs chart data
    const width = chart.width;
    const height = chart.height;

    chart_data.save();      
    chart_data.textAlign = 'center';
    chart_data.textBaseline = 'middle';
    chart_data.font = '16px Arial';  
    chart_data.fillStyle = '#666';  
    chart_data.fillText(message, width / 2, height / 2);        // Draw the message in the middle of the chart
    chart_data.restore(); 
}

// To get the charts to update whenever a different month is selected without having the page refresh you will send a AJAX request to the route to get the data for that month
function getUtilityData(utilitySelectedMonth){
    fetch(`/redraw_utility_chart?month=${utilitySelectedMonth}`)       // Sends a AJAX request to / route for the selected month
        .then(response => response.json())        // response is the raw data that is converted to JSON
        .then(data => {
            // Updating the lists with selected months data and redrawing it with that new data
            utilityValues = data.utility_values;
            utilityLabels = data.utility_labels;
            // updateUtilityChart(data.utility_labels, data.utility_values)
            drawUtilityChart(); 

            // Debugging: Log the updated utility labels and values
            console.log("Data from Flask end:", data);  
            console.log("Updated utilityLabels:", utilityLabels);
            console.log("Updated utilityValues:", utilityValues);
        });
}

// To delay pressing the buttons so that the No Data message displays properly
function debounce(func, timeout = 100){
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

drawUtilityChart();        // Initial Draw

// Handles the functionality left button for previous month
document.getElementById('prevUtilityMonth').addEventListener('click', debounce(function(){
    // int of January is 1
    // If January and I press the back button it is going set selectedMonth to 12 which is December. Basically it allows for it to circle back
    utilitySelectedMonth = utilitySelectedMonth > 1 ? utilitySelectedMonth - 1 : yearToDateMonths.length;    
    document.getElementById('displayUtilityMonth').textContent = yearToDateMonths[utilitySelectedMonth - 1];
    getUtilityData(utilitySelectedMonth);
}));

// Handles the functionality right button for next month
document.getElementById('nextUtilityMonth').addEventListener('click', debounce(function(){
    // If December and I press the go forward button it is going set selectedMonth to 1 which is January
    utilitySelectedMonth = utilitySelectedMonth < yearToDateMonths.length ? utilitySelectedMonth + 1 : 1;    
    document.getElementById('displayUtilityMonth').textContent = yearToDateMonths[utilitySelectedMonth - 1];
    getUtilityData(utilitySelectedMonth);  
}));



// Redraws the chart with the data from the selected month  
// function updateUtilityChart(labels, values) {
//     if (values.length === 0 || values.every(value => value === 0)) {        // Checks if there is data or if every entry is 0
//         // Clear the chart's data and labels if there is no data
//         utilityChart.data.labels = [];
//         utilityChart.data.datasets[0].data = [];
//         utilityChart.update();      // Redraw the chart to reflect that it's empty
//         drawNoDataChart(utilityChart, "No Data For This Month");        // Display No Data
//     } else {
//         utilityChart.data.labels = labels;       // Updating the X axis
//         utilityChart.data.datasets[0].data = values;        // Updating the Y axis. [0] because datasets is an array. There is only 1 entry in that array
//         utilityChart.update();      // Redraws the chart with updated data
//     }
// }






