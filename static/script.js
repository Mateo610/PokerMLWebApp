function playerAction(action) {
    let raiseAmount = 0;
    if (action === 'raise') {
        raiseAmount = document.getElementById('raise-amount').value;
        if (raiseAmount <= 0) {
            alert('Please enter a valid raise amount.');
            return;
        }
    }

    fetch('/player_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: action, raise_amount: raiseAmount })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh the page or update the game state dynamically
            location.reload();
        } else {
            alert(data.message);
        }
    });
}
