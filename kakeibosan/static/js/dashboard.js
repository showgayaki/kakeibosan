
function initDashboardPageCharts(
    thisMonth,
    totalCostsLastYear,
    totalCostsThisYear,
    costsThisMonthByCategory,
    utilityLastYear,
    utilityThisYear,
    viewCategory,
) {
    drawBigDashboardChart(totalCostsLastYear, totalCostsThisYear);
    drawPieChart(thisMonth, costsThisMonthByCategory, totalCostsThisYear.totals);
    drawUtilityCostChart(utilityLastYear, utilityThisYear, viewCategory);
}


function drawBigDashboardChart(lastYearData, thisYearData) {
    chartColor = "#FFFFFF";

    let ctx = document.getElementById('bigDashboardChart').getContext("2d");

    let gradientStroke = ctx.createLinearGradient(500, 0, 100, 0);
    gradientStroke.addColorStop(0, '#80b6f4');
    gradientStroke.addColorStop(1, chartColor);

    let gradientFill = ctx.createLinearGradient(0, 200, 0, 50);
    gradientFill.addColorStop(0, "rgba(128, 182, 244, 0)");
    gradientFill.addColorStop(1, "rgba(255, 255, 255, 0.24)");

    const chartStyle = {
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
    };

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: lastYearData.months,
            datasets: [
                {
                    ...chartStyle,
                    borderColor: hexToRgba(chartColor, 0.4),
                    pointBackgroundColor: hexToRgba(chartStyle.pointBackgroundColor, 0.4),
                    pointHoverBackgroundColor: hexToRgba(chartStyle.pointHoverBackgroundColor, 0.4),
                    label: `${lastYearData.year}年`,
                    data: lastYearData.totals,
                },
                {
                    ...chartStyle,
                    label: `${thisYearData.year}年`,
                    data: thisYearData.totals,
                },
            ]
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
                position: "top",
                fillStyle: "#FFF",
                display: true,
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


function drawPieChart(thisMonth, costsThisMonthByCategory, totalCosts) {
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
        percentage = Math.round((costsThisMonthByCategory[i]['amount'] / totalCosts[thisMonth - 1]) * 100);
        percentages.push(percentage);
    }

    // 月の割合
    ctx = document.getElementById('pieChart').getContext('2d');
    new Chart(ctx, {
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
                position: 'left',
            }
        }
    });
}


function drawUtilityCostChart(lastYearData, thisYearData, viewCategory) {
    // 各種料金のグラフ
    viewCategory.forEach(function (category) {
        console.log('category', category);
        console.log('lastYearData', lastYearData);
        let chartBaseColor = category['chart_color'];
        let chartName = category['in_english'];

        try {
            ctx = document.getElementById('lineChart' + chartName).getContext('2d');
        } catch (e) {
            return;
        }

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: lastYearData.months,
                datasets: [
                    {
                        // 去年: 半透明
                        label: `${lastYearData.year}年`,
                        backgroundColor: 'rgba(0,0,0,0)',
                        borderColor: hexToRgba(chartBaseColor, 0.6),
                        data: lastYearData.totals[category['id']],
                    },
                    {
                        // 今年: 通常カラー
                        label: `${thisYearData.year}年`,
                        backgroundColor: 'rgba(0,0,0,0)',
                        borderColor: chartBaseColor,
                        data: thisYearData.totals[category['id']],
                    },
                ]
            },
            options: {
                legend: {
                    display: true,
                }
            }
        });
    })
}


// hex -> rgba(…,0.4) へ変換する簡易関数
const hexToRgba = (hex, alpha) => {
    const c = hex.replace('#', '');
    const bigint = parseInt(c, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r},${g},${b},${alpha})`;
};
