
function showPaymentDetails(method) {
    let detailsDiv = document.getElementById('payment-details');
    detailsDiv.innerHTML = ''; // Clear any previous payment details fields

    if (method === 'gpay') {
        detailsDiv.innerHTML = `
            <label for="gpay-number">Enter Your Google Pay Number:</label>
            <input type="text" id="gpay-number" name="gpay_number" placeholder="Google Pay Number" required>
        `;
    } else if (method === 'phonepe') {
        detailsDiv.innerHTML = `
            <label for="phonepe-number">Enter Your PhonePe Number:</label>
            <input type="text" id="phonepe-number" name="phonepe_number" placeholder="PhonePe Number" required>
        `;
    } else if (method === 'card') {
        detailsDiv.innerHTML = `
            <label for="card-number">Enter Your Card Number:</label>
            <input type="text" id="card-number" name="card_number" placeholder="Card Number" required>
            <label for="card-expiry">Enter Expiry Date:</label>
            <input type="text" id="card-expiry" name="card_expiry" placeholder="MM/YY" required>
            <label for="card-cvc">Enter CVC:</label>
            <input type="text" id="card-cvc" name="card_cvc" placeholder="CVC" required>
        `;
    } else if (method === 'paytm') {
        detailsDiv.innerHTML = `
            <label for="paytm-number">Enter Your Paytm Number:</label>
            <input type="text" id="paytm-number" name="paytm_number" placeholder="Paytm Number" required>
        `;
    } else if (method === 'netbanking') {
        detailsDiv.innerHTML = `
            <label for="netbanking-id">Enter Your Net Banking ID:</label>
            <input type="text" id="netbanking-id" name="netbanking_id" placeholder="Net Banking ID" required>
        `;
    }
}
