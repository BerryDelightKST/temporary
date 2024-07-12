const AT = document.getElementById("AT");
const PH = document.getElementById("PH");
const EC = document.getElementById("EC");
const humidity = document.getElementById("humidity");
const light = document.getElementById("light");
const UVLightSource = document.getElementById("uv-light-source");
const fan = document.getElementById("fan");
const pump = document.getElementById("pump");

selectedDataset = {
    "label": "",
    "index": 0
};
let datasets = {
    // "Ambient Temperature": {
    //     "xDataLabel": Time,
    //     "yDataLabel": Temperature (°C),
    //     "xData": []
    //     "yData": []
    // }
}

let dataChart = newLineChart("Ambient Temperature", "rgb(34, 142, 225)", "Time", "Temperature (°C)", 0.3);
let dataElement = document.getElementById("data");
dataElement.appendChild(dataChart.canvas);

addDataset(dataChart, "pH Level", "Time", "pH", 0.3);
addDataset(dataChart, "Electrical Conductivity", "Time", "Electrical Conductivity (mS/cm)", 0.3);
addDataset(dataChart, "Humidity", "Time", "Humidity (%)", 0.3);
addDataset(dataChart, "Light Level", "Time", "Light (lux)", 0.3);

let UVLightSourceChart = newLineChart("UV Light Source", "rgb(54, 162, 235)", "Time", "State (ON/OFF)", 0);
UVLightSource.appendChild(UVLightSourceChart.canvas);

let fanChart = newLineChart("Fan", "rgb(255, 99, 132)", "Time", "Speed", 0.3);
fan.appendChild(fanChart.canvas);

let pumpChart = newBarChart("Pump", "rgb(75, 192, 192)", "Time", "Number of Activations (ON/OFF)");
pump.appendChild(pumpChart.canvas);


async function getConfig() {
    const response = await fetch('/config');
    const config = await response.json();
    return config;
}

async function initWebSocket() {
    const config = await getConfig();
    const serverAddress = config.serverAddress;

    const socket = new WebSocket(`ws://${serverAddress}`);

    socket.onopen = function(event) {
        console.log('WebSocket open.');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // console.log('Message from server:', data);
        // console.log('data from server');

        updateDashboard(data);
    };

    socket.onclose = function(event) {
        console.log('WebSocket closed.');
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

initWebSocket();


function updateDashboard(data) {
    for (const [datasetLabel, dataset] of Object.entries(datasets)) {
        dataset.xData = data[datasetLabel].map(d => d[0]);
        dataset.yData = data[datasetLabel].map(d => d[1]);
    }
    dataChart.data.labels = datasets[selectedDataset["label"]].xData;
    dataChart.data.datasets[selectedDataset["index"]].data = datasets[selectedDataset["label"]].yData;
    dataChart.update();
}


function addDataset(chart, label, xLabel, yLabel, tension) {
    datasets[label] = {
        "xDataLabel": xLabel,
        "yDataLabel": yLabel,
        "xData": [],
        "yData": []
    }
    chart.data.datasets.push({
        label: label,
        data: [],
        borderColor: "black",
        fill: false,
        tension: tension,
        hidden: true
    });
    chart.update();
}


function newLineChart(label, colour, xLabel, yLabel, tension) {
    selectedDataset = {
        "label": label,
        "index": 0
    };
    datasets[label] = {
        "xDataLabel": xLabel,
        "yDataLabel": yLabel,
        "xData": [],
        "yData": []
    }
    chartNode = document.createElement("canvas");
    chart = new Chart(chartNode, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                borderColor: colour,
                fill: false,
                tension: tension
            }]
        },
        options: {
            responsive: true,
            devicePixelRatio: 1.8,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: xLabel,
                        font: {
                            family: 'Outfit',
                            size: 18
                        }
                    },
                    ticks: {
                        font: {
                            family: 'Outfit',
                            size: 14 // Change x-axis labels font size
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: yLabel,
                        font: {
                            family: 'Outfit',
                            size: 18
                        }
                    },
                    ticks: {
                        font: {
                            family: 'Outfit',
                            size: 14 // Change x-axis labels font size
                        }
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            family: 'Outfit',
                            size: 18
                        },
                        boxWidth: 26,
                        boxHeight: 14,
                        generateLabels: function(chart) {
                            const labels = Chart.defaults.plugins.legend.labels.generateLabels(chart);
                            labels.forEach(label => {
                                const dataset = chart.data.datasets[label.datasetIndex];
                                if (dataset.hidden) {
                                    label.fillStyle = 'gray';
                                    label.strokeStyle = 'gray';
                                    label.lineWidth = 0;
                                    // colour
                                    label.fontColor = 'gray';

                                } else {
                                    label.fillStyle = dataset.borderColor;
                                    label.strokeStyle = dataset.borderColor;
                                    label.lineWidth = 4;
                                    label.fontColor = 'black';
                                }
                            });
                            return labels;
                        },
                    },
                    onClick: (e, legendItem, legend) => {
                        const index = legendItem.datasetIndex;
                        const clickedDataset = legend.chart.data.datasets[index];
                        const xScale = legend.chart.scales['x'];
                        const yScale = legend.chart.scales['y'];
                        trueDataset = {}
                        legend.chart.data.datasets.forEach(dataset => {
                            if (dataset !== clickedDataset) {
                                dataset.hidden = true;
                                dataset.borderColor = "black";

                            }
                        });

                        trueDataset = datasets[clickedDataset.label];
                        clickedDataset.hidden = false;
                        clickedDataset.borderColor = colour;

                        selectedDataset = {
                            "label": clickedDataset.label,
                            "index": index
                        };
                        xScale.options.title.text = trueDataset.xDataLabel;
                        yScale.options.title.text = trueDataset.yDataLabel;
                        legend.chart.data.labels = trueDataset.xData;
                        clickedDataset.data = trueDataset.yData;

                        legend.chart.update();
                    }
                }
            }
        }
    });
    return chart
}

function newBarChart(label, colour, x_label, y_label) {
    chartNode = document.createElement("canvas");
    return new Chart(chartNode, {
        type: "bar",
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                backgroundColor: colour
            }]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: x_label
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: y_label
                    },
                    beginAtZero: true
                }
            }
        }
    });
}