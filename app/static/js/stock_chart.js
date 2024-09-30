let stockChart;
const stockChartLocation = document.getElementById('stockChart').getContext('2d');

function drawStockChart() {
    stockChart = new Chart(stockChartLocation, {
        type: 'line',
        data: {
            labels: dateList,  // X-axis labels (dates)
            datasets: [{
                label: 'Total Investments',
                data: eodInvestmentList,  // Y-axis data (investment values)
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false,  // Do not fill under the line
                tension: 0.1  // Controls the curve of the line (0 is straight, 1 is curved)
            }, {
                label: 'Initial Investment',
                data: new Array(dateList.length).fill(eodInitialInvestmentList[eodInitialInvestmentList.length - 1]),  // Ensure the line spans the whole chart
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                borderDash: [5, 5],  // Dashed line for the initial investment
                fill: false,  // No fill under the line
                // pointRadius: 0,  // Remove points
                // pointHoverRadius: 0  // Remove points when hovering
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,   
                    title: {
                        display: true,
                    }
                },
                x: {
                    title: {
                        display: true,
                    }
                }
            },
            plugins: {
                legend: {
                    display: true  // Display the legend for both datasets
                }
            }
        }
    });
}

function updatePortfolioTable(){
    fetch('/update_portfolio', { method: 'GET' })  // Use GET to fetch stock data
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();  // Parse the JSON data
    })
    .then(data => {
        // Clear form fields
        document.getElementById('symbol').value = "";
        document.getElementById('shares').value = "";
        document.getElementById('purchase_price').value = "";

        // Process and update the portfolio table
        let stockTable = document.getElementById('stockTable');
        stockTable.innerHTML = "";  // Clear the existing table content
  
        // Append new data to the table
        data.stocks.forEach(stock => {
            let row = `
            <tr>
                <td>${stock.symbol}</td>
                <td>${stock.shares}</td>
                <td>${stock.purchase_price}</td>
                <td>${stock.current_price}</td>
                <td>${(stock.current_price - stock.purchase_price).toFixed(2)}</td>
                <td>${(((stock.current_price - stock.purchase_price) / stock.purchase_price) * 100).toFixed(2)}</td>
            </tr>`;
            stockTable.insertAdjacentHTML('beforeend', row);  // Add row to the table
        });
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

// Function to update the chart dynamically
function updateChart() {
    fetch('/update_stock_chart', { method: 'GET' })  // Use GET to fetch stock data
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();  // Parse the JSON data
    })
    .then(data => {
        console.log("Updating chart with data:", data);  // Debug log

        stockChart.data.labels = data.date_list;  // Update X-axis labels
        stockChart.data.datasets[0].data = data.eod_investment_list;  // Update Y-axis data for total investments
        stockChart.data.datasets[1].data = new Array(data.date_list.length).fill(data.eod_initial_investment_list[data.eod_initial_investment_list.length - 1]);  // Update initial investment line
        stockChart.update();  // Redraw the chart
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

drawStockChart();

// I want to make it so that the page doesnt reload when a new entry is made.
// Use AJAX to handle that
document.getElementById("stock_form").addEventListener('submit', function(event) {
    event.preventDefault();  // Prevents the page from reloading when the submit button is hit

    // Getting values from the form
    let symbol = document.getElementById('symbol').value;
    let shares = document.getElementById('shares').value;
    let purchase_price = document.getElementById('purchase_price').value;

    // Creating a FormData object that will hold the form fields with their values
    let formData = new FormData();
    formData.append('symbol', symbol);
    formData.append('shares', shares);
    formData.append('purchase_price', purchase_price);

    fetch('/add_stock?ajax=true', {
        method: 'POST',  // Form submission should be POST
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();  // Expect a JSON response
    })
    .then(data => {
        console.log("here", data)
        updatePortfolioTable();  // Update the portfolio table after the stock is added
        updateChart();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
});

setInterval(() => {
    updateChart();
}, 3600000);  // 1 hours in milliseconds

