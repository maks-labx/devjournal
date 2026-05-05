const ratingButtons = document.querySelectorAll('.rating-buttons');

ratingButtons.forEach(container => {
    container.addEventListener("click", event => {
        const button = event.target.closest("button[data-value]");

        if (!button) {
            return;
        }

        const value = parseInt(button.dataset.value);
        const postId = parseInt(button.dataset.post);
        const ratingSum = container.querySelector('.rating-sum');

        if (!ratingSum) {
            return;
        }

        const formData = new FormData();
        formData.append('post_id', postId);
        formData.append('value', value);

        fetch("/rating/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        }).then(response => response.json())
        .then(data => {
            if (data.rating_sum !== undefined) {
                ratingSum.textContent = data.rating_sum;
            }
        })
        .catch(error => console.error(error));
    });
});