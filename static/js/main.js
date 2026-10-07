document.addEventListener("DOMContentLoaded", function () {


    /* ==========================================
       LIKE BUTTONS
    ========================================== */

    const likeButtons =
        document.querySelectorAll(".like-button");


    likeButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            fetch(button.dataset.url)

                .then(response => response.json())

                .then(data => {

                    const likeCount =
                        button
                            .closest(".card-body")
                            .querySelector(".like-count");


                    likeCount.textContent =
                        data.likes + " likes";


                    if (data.liked) {

                        button.textContent =
                            "💔 Unlike";

                    } else {

                        button.textContent =
                            "❤️ Like";

                    }

                });

        });

    });



    /* ==========================================
       MOBILE SEARCH
    ========================================== */

    const searchButton =
        document.getElementById(
            "mobile-search-button"
        );


    const searchPanel =
        document.getElementById(
            "mobile-search-panel"
        );


    if (searchButton && searchPanel) {

        searchButton.addEventListener(
            "click",
            function () {

                searchPanel.classList.toggle(
                    "hidden"
                );

            }
        );

    }

});