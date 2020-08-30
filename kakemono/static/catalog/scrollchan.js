var videoGrid = document.getElementById("grid");

window.onload = () => {
    //document.getElementById("feed").requestFullscreen();
}

var vids = document.getElementsByClassName("vid");
/* maybe whatever video is in the center of the screen? */
window.addEventListener('scroll', () => {

    /* some attempts at improving scrolling; not really what I want */
    // animate scroll, stretch between windows, etc. hop between webms.
    // also reduce loading (probably w/ basic paging on the back end)

    for (var i = 0; i < vids.length; i++) {
        var dim = vids[i].getBoundingClientRect();

        if (Math.abs(dim.top) < window.innerHeight / 2) {
            vids[i].play();
        } else {
            vids[i].pause();
        }
    }
});
