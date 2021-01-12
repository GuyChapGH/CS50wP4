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

    // TRY to add edit link to each allpost div. (NOT WORKING).
    function add_edit_link (div_content) {
        var a = document.createElement('a');
        var linkText = document.createTextNode("Edit");
        a.appendChild(linkText);
        a.title = "Edit";
        a.href = "#";
        div_content.querySelector('#post').appendChild(a);
        //document.body.appendChild(a);
        //console.log (div_content);


    }

});
