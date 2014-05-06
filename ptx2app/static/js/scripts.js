function evenPics () {
    var pics = document.getElementsByClassName("img-responsive");
    var biggest = 0;
    for (var i = 0; i < pics.length; i++) {
        if (pics[i].height > biggest) {
            biggest = pics[i].height;
        }
    }
    for (var i = 0; i < pics.length; i++) {
        var p = pics[i];
        var margin = (biggest - p.height) / 2.0;
        p.style.marginTop = margin;
        p.style.marginBottom = margin;
        p.style.display="inline-block";
    }
};
function equalizeThumbs () {
    $(function() { // Ensure equal heights on thumbnail boxes
        $('.thumbnail').equalHeights(400);
    });
};

$(window).load(function() {evenPics(); equalizeThumbs();});
