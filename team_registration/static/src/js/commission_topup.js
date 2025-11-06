function topUpWallet(btn) {
    console.log("topUpWallet function called");
    var userId = btn.getAttribute("data-user");
    var amount = parseFloat(btn.getAttribute("data-amount") || "0");
    
    console.log("User ID:", userId, "Amount:", amount);

    if (amount <= 0) {
        console.warn("No commission balance available.");
        showNoBalanceModal();
        return;
    }


    // Make AJAX request using traditional form data for Odoo
    var formData = new FormData();
    formData.append('user_id', userId);
    formData.append('amount', amount);
    
    console.log("Making request to /commission/topup with form data");
    
    fetch('/commission/topup', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData,
        credentials: 'same-origin'
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP error! status: ' + response.status);
        }
        return response.json();
    })
    .then(function(result) {
        console.log("Response received:", result);
        if (result.success) {
            console.log('Wallet topped up with ' + result.amount + ' JOD.');

            // Update commission balance in UI
            var commissionEl = document.getElementById("commission-balance");
            if (commissionEl) {
                commissionEl.innerText = result.new_balance.toFixed(2);
                // also update button data-amount for next time
                btn.setAttribute("data-amount", result.new_balance);
            }

            // Update wallet balance in UI
            var walletEl = document.getElementById("wallet-balance");
            if (walletEl) {
                walletEl.innerText = result.wallet_balance.toFixed(2);
            }


            // Show success popup
            showSuccessModal(result.amount, result.new_balance, result.wallet_balance);
            
            // Refresh the page to ensure all data is up-to-date and consistent
            setTimeout(function() {
                window.location.reload();
            }, 300000);
        } else {
            console.error("Top-up failed:", result);
            var errorMsg = result.error || result.message || "Top-up failed.";
            alert("Error: " + errorMsg);
            btn.disabled = false;
            btn.innerText = "Top Up";
        }
    })
    .catch(function(err) {
        console.error(err.message || "Something went wrong.");
        alert("Top-up failed. Please try again.");
        btn.disabled = false;
        btn.innerText = "Top Up";
    });
}

// Make function globally available
window.topUpWallet = topUpWallet;
