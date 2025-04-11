async function predict(location) {
  const response = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ location })
  });

  const data = await response.json();

  document.getElementById("result").innerHTML = `
    <h3>Prediction for ${data.location}</h3>
    <p><strong>Day:</strong> ${data.day}</p>
    <p><strong>Time Block:</strong> ${data.time}</p>
    <p><strong>Availability:</strong> ${data.availability} (${data.confidence}% confident)</p>
    <p><strong>Estimated Spaces:</strong> ${data.spaces}</p>
  `;
}
