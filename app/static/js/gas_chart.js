// Making bar chart for gas 
const gasChartLocation = document.getElementById('gasChart').getContext('2d');
const gasChart = new Chart(gasChartLocation, {
    type: 'bar',    // Setting chart type as barchart
    data: {
        labels: yearToDateMonths,  // X axis labels
        datasets: [{
            label: 'Gas Spending',
            data: gasTotalSpending,    // Y axis data 
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            barThickness: 40,    
            maxBarThickness: 50
        }]
    },
    options: {      // Configuring how the chart looks and behaves
        scales:{    // Configuring X and Y axes
            y: {
                beginAtZero: true,  // To ensure the Y-axis starts at 0
                title: {
                    display: true
                }                    
            },
            x: {
                ticks: {
                    autoSkip: false,    // To ensure that no labels are missed and displayed
                    maxRotation: 45,    // Rotating the words to easier readability 
                    minRotation: 45
                },
                title: {
                    display: true
                }     
            }
        },
        plugins: {      // Configuring the interactions and appearance
            legend:{    
                display: false      // Don't want a legend
            },
            tooltip:{   // Allows it show information whenever you hover 
                displayColors: false,       // Disable colored box in tooltip message
                callbacks:{     // Defines how the tooltip looks and behaves
                    label: function(data){    
                        const currentMonthValue = data.raw || 0;      // data.raw refers to the raw value of where it is being hovered over. 0 if it is null/ undefined
                        const previousMonthValue = data.dataset.data[data.dataIndex - 1] || 0;

                        // Calculates the percent difference from the previous month and displays if there is an increase/decrease in spending from previous month
                        let percentChangeStr = '';
                        if (previousMonthValue > 0){
                            const percentChange = ((currentMonthValue - previousMonthValue) / previousMonthValue) * 100;
                            if(percentChange > 0){
                                percentChangeStr = `Spending Increased By: ${percentChange.toFixed(2)}%`;
                            }else{
                                percentChangeStr = `Spending Decreased By: ${percentChange.toFixed(2)}%`;
                            }
                        }else{
                            percentChangeStr = 'No Previous Month Data';
                        }

                        return [`$${currentMonthValue}`, percentChangeStr];     // So that the messages are in 2 lines instead of 1
                    }
                }
            }
        },
        responsive: true, // Makes the chart responsive to container size
        maintainAspectRatio: false, // Allows flexibility in chart sizing
        layout: {
            padding: {
                top: 10,
                bottom: 10
            }
        },
        barThickness: 'flex'
    }
});