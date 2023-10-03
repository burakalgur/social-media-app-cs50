document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".like-button").forEach((button) => {
    button.onclick = function () {
      likeDislike(this);
    };
  });

  async function likeDislike(element) {
    const headers = new Headers({
      "Content-Type": "application/json",
    });

    await fetch(`/like/${element.dataset.postId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.liked) {
          element.querySelector("i").classList.remove("far");
          element.querySelector("i").classList.add("fas");
        } else {
          element.querySelector("i").classList.remove("fas");
          element.querySelector("i").classList.add("far");
        }
        element.querySelector("span").innerHTML = data.total_likes;
      });
  }

  const followButton = document.querySelector(".follow-button");
  if (followButton) {
    followButton.addEventListener("click", (event) => {
      const userId = event.currentTarget.dataset.userId;

      const followText = document.querySelector(".follow-button-text");
      const followersCount = document.querySelector("#followers");

      fetch(`/follow/${userId}`)
        .then((response) => response.json())
        .then((data) => {
          if (data.followed) {
            followText.innerHTML = "Unfollow";
          } else {
            followText.innerHTML = "Follow";
          }
          followersCount.innerHTML = `Followers: ${data.total_followers}`;
          console.log(data);
        });
    });
  }
  function toggleVisibility(postId, elementsToShow, elementsToHide) {
    elementsToShow.forEach((element) => {
      document.querySelector(`#${element}_${postId}`).style.display = "block";
    });

    elementsToHide.forEach((element) => {
      document.querySelector(`#${element}_${postId}`).style.display = "none";
    });
  }

  // Edit post
  document.querySelectorAll(".edit-button").forEach((button) => {
    button.addEventListener("click", function () {
      const postId = this.dataset.id;
      toggleVisibility(
        postId,
        ["edit_form", "cancel_button"],
        ["post_content", "edit_link"]
      );
    });
  });

  // Close edit post
  document.querySelectorAll(".btn-secondary").forEach((button) => {
    button.addEventListener("click", function () {
      const postId = this.dataset.id;
      toggleVisibility(
        postId,
        ["post_content", "edit_link"],
        ["edit_form", "cancel_button"]
      );
    });
  });

  // Update post
  document.querySelectorAll(".save-button").forEach((button) => {
    button.onclick = function (event) {
      event.preventDefault();

      const postId = event.currentTarget.dataset.id;
      const postTextContent = document.querySelector(`#post_content_${postId}`);
      const frmEdit = document.querySelector(`#edit_form_${postId}`);

      fetch(frmEdit.dataset.url, {
        method: "POST",
        body: new FormData(frmEdit),
        headers: {
          "X-CSRFToken": document.querySelector(
            'input[name="csrfmiddlewaretoken"]'
          ).value,
        },
      })
        .then((response) => response.json())
        .then((result) => {
          if (result.message) {
            toggleVisibility(
              postId,
              ["post_content", "edit_link"],
              ["edit_form", "cancel_button"]
            );
            postTextContent.innerHTML = result.content;
          } else {
            toggleVisibility(
              postId,
              ["edit_form", "cancel_button"],
              ["post_content", "edit_link"]
            );
          }
        });
    };
  });
});
