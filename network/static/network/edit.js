document.addEventListener('DOMContentLoaded', function() {
    //console.log("hello world!");
    //alert("Hello, world!");

    //const post = document.querySelector('.allpost');
    //console.log(post);

    // Select the posts from the document
    var posts = document.getElementsByClassName("allpost");
    //console.log(posts);

    // Convert HTMLCollection into an array
    var posts_arr = Array.from(posts);
    console.log(posts_arr);

    // Iterate through array of allpost divs
    posts_arr.forEach(add_edit_link);

    // Add edit link to each allpost div.
    function add_edit_link (div_content) {

        // Get text content of post_user from allposts div
        const post_user = div_content.querySelector('#post_user').textContent;
        //console.log(post_user);

        // Get text content of current user from layout.html
        const current_user = document.querySelector('#current_user').textContent;
        //console.log(current_user);

        // Test if post_user is the same as current_user
        if (post_user == current_user)  {
            // Create anchor object
            var a = document.createElement('a');
            // Create text for anchor object
            var linkText = document.createTextNode("Edit");
            // Append text to anchor
            a.appendChild(linkText);
            // Set values of anchor
            a.title = "Edit";
            a.href = "#";
            //a.id = "edit"
            // Append anchor object to each allpost div
            div_content.querySelector('#post').appendChild(a);

            // Add on click function
            a.addEventListener('click', function()  {
                //alert("Edit link was clicked!");
                // Create textarea element
                var text_area = document.createElement("textarea");
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
                    alert("Save button was clicked!");
                })

            })




        }




    }

});
