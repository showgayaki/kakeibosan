
function initDashboardPageCharts(totalCostsLast12Months, costsThisMonthByCategory, utilityCosts, viewCategory) {
    drawBigDashboardChart(totalCostsLast12Months['total'], totalCostsLast12Months['months']);
    drawPieChart(costsThisMonthByCategory, totalCostsLast12Months['total']);
    drawUtilityCostChart(utilityCosts, totalCostsLast12Months['months'], viewCategory);
}


function drawBigDashboardChart(totalCosts, months){
    chartColor = "#FFFFFF";

    let ctx = document.getElementById('bigDashboardChart').getContext("2d");

    let gradientStroke = ctx.createLinearGradient(500, 0, 100, 0);
    gradientStroke.addColorStop(0, '#80b6f4');
    gradientStroke.addColorStop(1, chartColor);

    let gradientFill = ctx.createLinearGradient(0, 200, 0, 50);
    gradientFill.addColorStop(0, "rgba(128, 182, 244, 0)");
    gradientFill.addColorStop(1, "rgba(255, 255, 255, 0.24)");

    let myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: "出費合計",
                borderColor: chartColor,
                pointBorderColor: chartColor,
                pointBackgroundColor: "#1e3d60",
                pointHoverBackgroundColor: "#1e3d60",
                pointHoverBorderColor: chartColor,
                pointBorderWidth: 1,
                pointHoverRadius: 7,
                pointHoverBorderWidth: 2,
                pointRadius: 5,
                fill: true,
                backgroundColor: gradientFill,
                borderWidth: 2,
                data: totalCosts
            }]
        },
        options: {
            layout: {
                padding: {
                    left: 20,
                    right: 20,
                    top: 0,
                    bottom: 0
                }
            },
            maintainAspectRatio: false,
            tooltips: {
                backgroundColor: '#fff',
                titleFontColor: '#333',
                bodyFontColor: '#666',
                bodySpacing: 4,
                xPadding: 12,
                mode: "nearest",
                intersect: 0,
                position: "nearest"
            },
            legend: {
                position: "bottom",
                fillStyle: "#FFF",
                display: false
            },
            scales: {
                yAxes: [{
                    ticks: {
                        fontColor: "rgba(255,255,255,0.4)",
                        fontStyle: "bold",
                        beginAtZero: true,
                        maxTicksLimit: 5,
                        padding: 10
                    },
                    gridLines: {
                        drawTicks: true,
                        drawBorder: false,
                        display: true,
                        color: "rgba(255,255,255,0.1)",
                        zeroLineColor: "transparent"
                    }

                }],
                xAxes: [{
                    gridLines: {
                        zeroLineColor: "transparent",
                        display: false
                    },
                    ticks: {
                        padding: 10,
                        fontColor: "rgba(255,255,255,0.4)",
                        fontStyle: "bold"
                    }
                }]
            }
        }
    });
}


function drawPieChart(costsThisMonthByCategory, totalCosts){
    // 円グラフ用
    bg_color = ["#3399FF", "#00CC33", "#C71585", "#DDDDDD", "#FF9933"]
    categories = [];
    percentages = [];

    // パーセンテージ大きい順にソート
    costsThisMonthByCategory.sort(function (a, b) {
        if (a.amount < b.amount) {
            return 1;
        } else {
            return -1;
        }
    })

    for (let i in costsThisMonthByCategory) {
        categories.push(costsThisMonthByCategory[i]['category']);
        percentage = Math.round((costsThisMonthByCategory[i]['amount'] / totalCosts.slice(-1)[0]) * 100);
        percentages.push(percentage);
    }

    // 月の割合
    ctx = document.getElementById('pieChart').getContext('2d');
    let chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{
                data: percentages,
                backgroundColor: bg_color
            }]
        },
        options: {
            legend: {
                display: true,
                position: 'left'
            }
        }
    });
}


function drawUtilityCostChart(utilityCosts, months, viewCategory){
    // 各種料金のグラフ
    viewCategory.forEach(function(category){
        console.log(category)
        let charges = [];
        let chartBorderColor = category['chart_color'];
        let chartName = category['in_english'];

        for(let month in utilityCosts){
            charges.push(utilityCosts[month][category['name']]);
        }

        ctx = document.getElementById('lineChart' + chartName).getContext('2d');
        let chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: chartName,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderColor: chartBorderColor,
                    data: charges,
                }]
            },
            options: {
                legend: {
                    display: false
                }
            }
        });
    })
}
