dashboard = {
    initDashboardPageCharts: function (total_costs_last_12_months, costs_this_month_by_category, utility_costs) {

        chartColor = "#FFFFFF";

        var ctx = document.getElementById('bigDashboardChart').getContext("2d");

        var gradientStroke = ctx.createLinearGradient(500, 0, 100, 0);
        gradientStroke.addColorStop(0, '#80b6f4');
        gradientStroke.addColorStop(1, chartColor);

        var gradientFill = ctx.createLinearGradient(0, 200, 0, 50);
        gradientFill.addColorStop(0, "rgba(128, 182, 244, 0)");
        gradientFill.addColorStop(1, "rgba(255, 255, 255, 0.24)");

        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: total_costs_last_12_months['months'],
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
                    data: total_costs_last_12_months['total']
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

        // 円グラフ用
        bg_color = ["#3399FF", "#00CC33", "#C71585", "#DDDDDD", "#FF9933"]
        categories = [];
        percentages = [];

        // パーセンテージ大きい順にソート
        costs_this_month_by_category.sort(function (a, b) {
            if (a.amount < b.amount) {
                return 1;
            } else {
                return -1;
            }
        })

        for (let i in costs_this_month_by_category) {
            categories.push(costs_this_month_by_category[i]['category']);
            percentage = Math.round((costs_this_month_by_category[i]['amount'] / total_costs_last_12_months['total'].slice(-1)[0]) * 100);
            percentages.push(percentage);
        }

        // 各種料金
        const ELECTRIC_CHARGE = '電気代';
        electric_charges = [];
        const GAS_CHARGE = 'ガス代';
        gas_charges = [];
        const WATER_CHARGE = '水道代';
        water_charges = [];

        for (let key in utility_costs) {
            electric_charges.push(utility_costs[key][ELECTRIC_CHARGE]);
            gas_charges.push(utility_costs[key][GAS_CHARGE]);
            water_charges.push(utility_costs[key][WATER_CHARGE]);
        }

        // 月の割合
        ctx = document.getElementById('pieChart').getContext('2d');
        var chart = new Chart(ctx, {
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

        // 電気代
        ctx = document.getElementById('lineChartElectricCharge').getContext('2d');
        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: total_costs_last_12_months['months'],
                datasets: [{
                    label: ELECTRIC_CHARGE,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderColor: 'rgb(255, 21, 51)',
                    data: electric_charges,
                }]
            },
            options: {
                legend: {
                    display: false
                }
            }
        });

        // ガス代
        ctx = document.getElementById('lineChartGasCharge').getContext('2d');
        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: total_costs_last_12_months['months'],
                datasets: [{
                    label: GAS_CHARGE,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderColor: 'rgb(255, 163, 0)',
                    data: gas_charges,
                }]
            },
            options: {
                legend: {
                    display: false
                }
            }
        });

        // 水道代
        ctx = document.getElementById('lineChartWaterCharge').getContext('2d');
        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: total_costs_last_12_months['months'],
                datasets: [{
                    label: WATER_CHARGE,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderColor: 'rgb(0, 106, 182)',
                    data: water_charges,
                }]
            },
            options: {
                legend: {
                    display: false
                }
            }
        });
    },
};
