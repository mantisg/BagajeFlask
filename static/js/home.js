document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to the delete button for posts
    const deletePostButtons = document.querySelectorAll('#delete-post');
    deletePostButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            deletePost(event.target);
        });
    });

    // Attach event listeners to the delete button for comments
    const deleteCommentButtons = document.querySelectorAll('#delete-comment');
    deleteCommentButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            deleteComment(event.target);
        });
    });
});

function deletePost(buttonElement) {
    const postElement = buttonElement.closest('.post-item');
    const postId = postElement.dataset.id;

    // Remove the post element from the DOM
    postElement.remove();

    fetch(`/posts/${postId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete post from database');
            }
            return response.json();
        })
        .then(data => {
            console.log('Post successfully deleted:', data);
        })
        .catch(error => {
            console.error('Error deleting post:', error);
        });
}

function deleteComment(buttonElement) {
    const commentContainer = buttonElement.closest('.comm-cont');
    const postElement = buttonElement.closest('.post-item');
    const postId = postElement.dataset.id;
    const commentIndex = [...postElement.querySelectorAll('.comm-cont')].indexOf(commentContainer);

    // Remove the comment element from the DOM
    commentContainer.remove();

    fetch(`/posts/${postId}/comments/${commentIndex}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete comment from database');
            }
            return response.json();
        })
        .then(data => {
            console.log('Comment successfully deleted:', data);
        })
        .catch(error => {
            console.error('Error deleting comment:', error);
        });
}

function submitResponse(button) {
    const form = button.closest('form');
    const postId = form.getAttribute('data-comment-id');
    const commentInput = form.querySelector('.comment-input');
    const commentBody = commentInput.value.trim();

    if (!commentBody) {
        alert('Comment cannot be empty.');
        return;
    }

    const comment = {
        CommentBody: commentBody,
        CreatedBy: 'Anonymous',
        CreatedAt: new Date().toISOString()
    };

    addCommentToDOM(postId, comment);

    fetch(`/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(comment)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok.');
            }
            return response.json();
        })
        .then(data => {
            console.log('Comment added:', data);
            // Optionally, update the UI to reflect the new comment
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was a problem adding the comment.');
        });
    commentInput.value = '';
}

function addCommentToDOM(postId, comment) {
    const postElement = document.querySelector(`.post-item[data-id="${postId}"]`);
    const commentsContainer = postElement.querySelector('.comments');

    // Create a new comment element
    const commentElement = document.createElement('p');
    commentElement.classList.add('comment-item');
    commentElement.innerHTML = `<span class="comment-body">${comment.CommentBody}</span><br> - ${comment.CreatedBy} at ${new Date(comment.CreatedAt).toLocaleString()} <button class="delete-btn" onclick="deleteComment">Delete</button><br><br>`;
    

    // Append the new comment to the comments container
    commentsContainer.appendChild(commentElement);
}