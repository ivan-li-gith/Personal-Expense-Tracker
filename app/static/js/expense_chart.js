let expenseChart;
const expenseChartLocation = document.getElementById('expenseChart').getContext('2d');

function drawExpenseChart(){
    if(expenseChart){
        expenseChart.destroy();     // Destroy it to prevent redrawing issues 
        console.log("Destroyed chart");
    }else {
        console.log('No chart to destroy');
    }


    if (expenseValues.length === 0 || expenseValues.every(value => value === 0)) {      
        console.log("Drawing empty canvas for No Data");

        // Clear the canvas to start fresh
        clearCanvas(expenseChartLocation);

        // Draw the No Data message
        drawExpenseNoDataMessage(expenseChartLocation, "No Data For This Month");
    }else{
        console.log("Drawing chart with expenseDates:", expenseDates);
        console.log("Drawing chart with expenseValues:", expenseValues);
        expenseChart = new Chart(expenseChartLocation, {
            type: 'line',
            data: {
                labels: expenseDates,
                datasets: [{
                    label: 'Expenses',
                    data: expenseValues,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false,  // Do not fill under the line
                    tension: 0.1  // Controls the curve of the line (0 is straight, 1 is curved)
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,   
                        title: {
                            display: true
                        }
                    },
                    x: {
                        title: {
                            display: true
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {                        
                        displayColors: false,
                        callbacks: {
                            title: function(data){
                                return '';
                            },
                            label: function(data){
                                const value = data.raw || 0.0;
                                return 'Total: $' + value.toFixed(2);      // Display the utility cost
                            },
                            afterLabel: function(data){     // Displays what items were bought and the costs
                                let breakdown = expenseBreakdown[data.dataIndex]        
                                return breakdown.join('\n');
                            }
                        }
                    }
                }
            }
        });
    }
}

// Helper function to clear the canvas
function clearCanvas(chartLocation) {
    const width = chartLocation.canvas.width;
    const height = chartLocation.canvas.height;

    // Clear the canvas
    chartLocation.clearRect(0, 0, width, height);
    console.log("Cleared canvas.");
}

// Function to draw "No Data" message on empty canvas
function drawExpenseNoDataMessage(chartLocation, message) {
    const width = chartLocation.canvas.width;
    const height = chartLocation.canvas.height;

    // Draw the "No Data" message on the empty canvas
    chartLocation.save();
    chartLocation.textAlign = 'center';
    chartLocation.textBaseline = 'middle';
    chartLocation.font = '16px Arial';
    chartLocation.fillStyle = '#666';
    chartLocation.fillText(message, width / 2, height / 2);
    chartLocation.restore();

    console.log("Drew 'No Data' message.");
}



// To get the charts to update whenever a different month is selected without having the page refresh you will send a AJAX request to the route to get the data for that month
function getExpenseData(expenseSelectedMonth){
    fetch(`/redraw_expense_chart?month=${expenseSelectedMonth}`)       // Sends a AJAX request to / route for the selected month
        .then(response => response.json())        // response is the raw data that is converted to JSON
        .then(data => {
            // console.log("Data from Flask end:", data);  
            // console.log("Current expenseDates:", expenseDates);
            // console.log("Current expenseValues:", expenseValues);
            // console.log("Current expenseBreakdown:", expenseBreakdown);
            expenseValues = data.expense_total_values;
            expenseDates = data.expense_date_labels;
            expenseBreakdown = data.expense_breakdown;
            // console.log("Updated expenseValues:", expenseValues);
            // console.log("Updated expenseDates:", expenseDates);
            // console.log("Updated expenseBreakdown:", expenseBreakdown);
            drawExpenseChart();
            // console.log("Final expenseValues in drawChart:", expenseValues);
            // console.log("Final expenseDates in drawChart:", expenseDates);
        });
}

// // Redraws the chart with the data from the selected month  
// function updateExpenseChart(dates, prices, breakdown){
//     expenseChart.data.labels = dates;       // Updating the X axis
//     expenseChart.data.datasets[0].data = prices;        // Updating the Y axis. [0] because datasets is an array. There is only 1 entry in that array
//     expenseChart.options.plugins.tooltip.callbacks.afterLabel = function(data) {     // Updating the tooltip message 
//         let breakdownData = breakdown[data.dataIndex];
//         return breakdownData.join('\n');
//     };
//     expenseChart.update();      // Redraws the chart with updated data
// }

// To delay pressing the buttons so that the No Data message displays properly
function debounce(func, timeout = 100){
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

drawExpenseChart();

// Handles the functionality of the month selector for left arrow key
document.getElementById('prevExpenseMonth').addEventListener('click', debounce(function(){
    expenseSelectedMonth = expenseSelectedMonth > 1 ? expenseSelectedMonth - 1 : yearToDateMonths.length;
    document.getElementById('displayExpenseMonth').textContent = yearToDateMonths[expenseSelectedMonth - 1];     // Updates the month display properly. Before it wasnt updating to the correct month
    getExpenseData(expenseSelectedMonth);
    // console.log("Fetching data for month:", expenseSelectedMonth);
}));

// Handles the functionality of the month selector for right arrow key
document.getElementById('nextExpenseMonth').addEventListener('click', debounce(function(){
    expenseSelectedMonth = expenseSelectedMonth < yearToDateMonths.length ? expenseSelectedMonth + 1 : 1;    
    document.getElementById('displayExpenseMonth').textContent = yearToDateMonths[expenseSelectedMonth - 1];
    getExpenseData(expenseSelectedMonth);
    // console.log("Fetching data for month:", expenseSelectedMonth);
}));



