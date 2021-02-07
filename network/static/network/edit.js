document.addEventListener('DOMContentLoaded', function() {

    // Select the posts from the document
    var posts = document.getElementsByClassName("allpost");
    //console.log(posts);

    // Convert HTMLCollection into an array
    var posts_arr = Array.from(posts);
    console.log(posts_arr);

    // Iterate through array of allpost divs
    posts_arr.forEach(add_buttons);

    // Add like button to each post and edit button to those posts where post is from the current_user.
    function add_buttons(div_content) {

        // Add like button to all posts
        // Create like_btn
        const like_btn = document.createElement("button");
        like_btn.innerHTML = "Like";
        like_btn.className = "btn btn-sm btn-outline-primary";

        // Append button to allpost div
        div_content.querySelector('#likes').appendChild(like_btn);

        //like_btn Onclick function goes here...
        like_btn.addEventListener('click', function()   {
            //Capture post id from index.html
            let id = div_content.querySelector('#post').dataset.id;
            // console.log("The post id is: " + id);

            //Ensure post_id is integer and not string
            let post_id = parseInt(id);

            // Test if press Like button
            if (like_btn.innerHTML === "Like")  {

                //Likes can be updated by add_like
                fetch(`/posts/${post_id}`,  {
                    method: 'PUT',
                    body: JSON.stringify({
                        likes_flag: true
                    })
                })
                .then(response => response.json())
                .then(result => {
                    console.log(result);
                    // Change button label to Unlike
                    like_btn.innerHTML = "Unlike";

                // GET likes count
                // GET request to retrieve likes count from post. This should follow PUT request
                // so that likes count has been updated.
                    fetch(`/posts/${post_id}`,  {
                        method: 'GET'
                    })
                    .then(response => response.json())
                    .then(post => {
                        console.log(post.likes);

                // Create p element and set innerHTML to likes count
                        const likes_pElem = document.createElement("p");
                        likes_pElem.innerHTML = 'Likes: ' + post.likes;

                        // Get DOM reference to likes paragraph from HTML page
                        const likes_para = div_content.querySelector('#likes_para');

                // Replace likes_para with likes p element
                        likes_para.parentNode.replaceChild(likes_pElem, likes_para);
                // Set id of p element to likes_para so can press like button more than once.
                        likes_pElem.id = "likes_para";

                    });

                });

            }

            // Test if press Unlike button
            else if (like_btn.innerHTML === "Unlike")   {

                //Likes can be updated by subtract_like
                fetch(`/posts/${post_id}`,  {
                    method: 'PUT',
                    body: JSON.stringify({
                        likes_flag: false
                    })
                })
                .then(response => response.json())
                .then(result => {
                    console.log(result);
                    //Change button label to Like
                    like_btn.innerHTML = "Like";

                    // GET likes count
                    // GET request to retrieve likes count from post. This should follow PUT request
                    // so that likes count has been updated.
                        fetch(`/posts/${post_id}`,  {
                            method: 'GET'
                        })
                        .then(response => response.json())
                        .then(post => {
                            console.log(post.likes);

                    // Create p element and set innerHTML to likes count
                            const likes_pElem = document.createElement("p");
                            likes_pElem.innerHTML = 'Likes: ' + post.likes;

                            // Get DOM reference to likes paragraph from HTML page
                            const likes_para = div_content.querySelector('#likes_para');

                    // Replace likes_para with likes p element
                            likes_para.parentNode.replaceChild(likes_pElem, likes_para);
                    // Set id of p element to likes_para so can press like button more than once.
                            likes_pElem.id = "likes_para";

                        });

                    });

                }
        })


        // Add edit button to those posts where post is from current_user
        // Get text content of post_user from allposts div
        const post_user = div_content.querySelector('#post_user').textContent;
        //console.log(post_user);

        // Get text content of current user from layout.html
        const current_user = document.querySelector('#current_user').textContent;
        //console.log(current_user);

        // Test if post_user is the same as current_user
        if (post_user == current_user)  {

            //Create edit button
            const edit_btn = document.createElement("button");
            edit_btn.innerHTML = "Edit";
            edit_btn.className = "btn btn-sm btn-outline-primary";

            // Append button to each allpost div
            div_content.querySelector('#post').appendChild(edit_btn);

            // Add on click function
            edit_btn.addEventListener('click', function()  {

                // Create textarea element
                var text_area = document.createElement("textarea");
                // Add id for reference
                text_area.id = "text_area"

                // Get post_content node
                var post_content = div_content.querySelector('#post_content');
                // Get text from post_content and insert in text_area
                text_area.innerHTML = post_content.textContent;
                // Replace post_content with text_area
                post_content.parentNode.replaceChild(text_area, post_content);
                // autofocus on text_area
                text_area.focus();

                //Add a save button
                const save_btn = document.createElement("button");
                save_btn.innerHTML = "Save";
                save_btn.className = "btn btn-primary";

                // Append save button
                text_area.parentNode.append(save_btn);

                //Add on click function
                save_btn.addEventListener('click', function()   {
                    //Capture post id from index.html
                    let id = div_content.querySelector('#post').dataset.id;
                    // console.log("The post id is: " + id);

                    //Ensure post_id is integer and not string
                    let post_id = parseInt(id);
                    // Get edited content from text_area.
                    var content = div_content.querySelector('#text_area').value;
                    // Test purposes
                    console.log(content);

                    //POST request to update content in post. Issue: doesn't always seem to update.
                    fetch(`/posts/${post_id}`,   {
                        method: 'POST',
                        body: JSON.stringify({
                            content: `${content}`
                        })
                    })
                    .then(response => response.json())
                    .then(result => {
                        console.log(result);


                    // GET request to retrieve content from post. This should follow POST request
                    // so that post.content has been updated.
                        fetch(`/posts/${post_id}`,  {
                            method: 'GET'
                        })
                        .then(response => response.json())
                        .then(post => {
                            console.log(post.content);

                    // Create paragraph element and set innerHTML to post.content
                    // Set id of paragraph element to post_content so can edit more than once.
                            var edit_post_content = document.createElement("p");
                            edit_post_content.id = "post_content";
                            edit_post_content.innerHTML = '<b>' + post.content + '</b>';

                    // Replace text_area with new paragraph element
                            text_area.parentNode.replaceChild(edit_post_content, text_area);

                    // Remove save_btn
                            save_btn.remove();
                        });
                });


                })

            })




        }




    }

});
