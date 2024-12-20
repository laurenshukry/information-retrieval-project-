function likeProduct(productName) {
    fetch("/like_product", {
        method: "POST",
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `product_id=${encodeURIComponent(productName)}`
    }).then(response => response.json())
      .then(data => alert(`Liked: ${productName}`))
      .catch(error => console.error('Error:', error));
}

function dislikeProduct(productName) {
    fetch("/dislike_product", {
        method: "POST",
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `product_id=${encodeURIComponent(productName)}`
    }).then(response => response.json())
      .then(data => alert(`Disliked: ${productName}`))
      .catch(error => console.error('Error:', error));
}



function fetchSuggestions(query) {
    if (query.length === 0) {
        document.getElementById("suggestions-box").innerHTML = "";
        return;
    }

    fetch(`/suggest?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const suggestionsBox = document.getElementById("suggestions-box");
            suggestionsBox.innerHTML = ""; // Clear previous suggestions

            data.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                li.style.padding = "10px";
                li.style.cursor = "pointer";

                li.onclick = () => {
                    document.getElementById("search-input").value = item;
                    suggestionsBox.innerHTML = ""; // Clear suggestions
                };
                suggestionsBox.appendChild(li);
            });
        });
}
