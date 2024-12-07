const ctx = document.getElementById("timeChart").getContext("2d");
const tbody = document.getElementById("sersor_data");

let config = {
  type: "line",
  data: {
    labels: ["5분전", "4분전", "3분전", "2분전", "현재"],
    datasets: [
      {
        label: "온도",
        backgroundColor: "rgba(0, 153, 255, 1)",
        borderColor: "rgba(0, 153, 255, 1)",
        fill: false,
        data: [],
      },
      {
        label: "습도",
        backgroundColor: "rgba(153, 255, 102, 1)",
        borderColor: "rgba(153, 255, 102, 1)",
        fill: false,
        data: [],
      },
    ],
  },
  options: {
    maintainAspectRatio: false,
    title: {
      display: true,
      text: "온도 및 습도 변화",
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "값",
        },
      },
    },
  },
};

// 전역 차트 객체
let myChart = new Chart(ctx, config);

// 센서 데이터를 가져오는 함수
async function fetchData() {
  try {
    const response = await fetch("http://localhost:8080/api");
    const result = await response.json();
    const data = result.data;
    if (data && data.length > 0) {
      const latestData = data[data.length - 1];
      console.log(latestData);

      // HTML 요소 업데이트
      document.getElementById("temperature").textContent =
        latestData.Temperature || "0";
      document.getElementById("humidity").textContent =
        latestData.Humidity || "0";
      document.getElementById("pressure").textContent =
        latestData.Pressure || "0";
      document.getElementById("wind_speed").textContent =
        latestData.WindSpeed || "0";
      document.getElementById("wind_direction").textContent =
        latestData.WindDirection || "0";
      document.getElementById("rainfall").textContent =
        latestData.Rainfall || "0";
      document.getElementById("dust").textContent = latestData.Dust || "0";

      // 창문 상태 업데이트
      document.getElementById("WindowState").textContent =
        latestData.WindowState || "0";

      // 차트 업데이트
      updateCharts(data);
      updateData(data);
    }
  } catch (error) {
    console.error("Error fetching sensor data:", error);
  }
}
function controlWindow() {
  const openBtn = document.getElementById("openBtn");
  const closeBtn = document.getElementById("closeBtn");
  openBtn.addEventListener("click", async () => {
    console.log("open");
    await fetch("http://192.168.0.90:5000/open", {
      method: "POST",
    });
  });
  closeBtn.addEventListener("click", async () => {
    console.log("close");

    await fetch("http://192.168.0.90:5000/close", {
      method: "POST",
    });
  });
}
// 차트 데이터를 업데이트하는 함수
function updateCharts(sensorData) {
  if (sensorData.length >= 5) {
    const recentData = sensorData.slice(-5); // 최신 5개 데이터
    config.data.datasets[0].data = recentData.map((item) => item.Temperature);
    config.data.datasets[1].data = recentData.map((item) => item.Humidity);

    // 기존 차트를 업데이트
    myChart.update();
  } else {
    console.error("Not enough data to update the chart");
  }
}

function updateData(sensorData) {
  const tbody = document.getElementById("sersor_data"); // <tbody> 가져오기

  // 최신 10개 데이터 추출 (전체 데이터가 10개면 그대로 사용)
  const recentData = sensorData.slice(-10);

  // 테이블 초기화 (필요한 경우)
  tbody.innerHTML = ""; // 기존 데이터를 지우고 새 데이터로 갱신

  // 최신 데이터를 순회하며 테이블 행 추가
  recentData.forEach((data) => {
    const tr = document.createElement("tr"); // 각 데이터 행 생성

    // 데이터 속성 순서대로 <td>에 추가
    const fields = [
      data.Temperature || 0,
      data.Humidity || 0,
      data.Pressure || 0,
      data.WindSpeed || 0,
      data.WindDirection || "N/A",
      data.Rainfall || 0,
      data.WindowState || "N/A",
    ];

    fields.forEach((field) => {
      const td = document.createElement("td");
      td.textContent = field; // 데이터 삽입
      tr.appendChild(td); // <td>를 <tr>에 추가
    });

    tbody.appendChild(tr); // 완성된 <tr>을 <tbody>에 추가
  });
}

// 최초 데이터 가져오기
fetchData();
document.addEventListener("DOMContentLoaded", controlWindow);
