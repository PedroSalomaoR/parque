function verSaldo() {
    let qr = document.getElementById("qr").value;

    fetch("http://127.0.0.1:5000/saldo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qr_code: qr })
    })
        .then(res => res.text())
        .then(data => {
            document.getElementById("resposta").innerText = "Saldo: R$ " + data;
        });
}