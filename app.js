document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("monitoringForm");
    const resultDisplay = document.getElementById("result");

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        
        fetch("/start", {
            method: "POST",
            body: new FormData(form)
        })
        .then(response => response.json())
        .then(data => {
            resultDisplay.innerText = data.status;
            resultDisplay.className = data.status.includes("Intrusion") ? "error" : "success";
        });
    });
});
