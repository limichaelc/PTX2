function evenPics (classname) {
    var pics = document.getElementsByClassName(classname);
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
function equalizeThumbs (classname) {
    $(function() { // Ensure equal heights on thumbnail boxes
        $(classname).equalHeights();
    });
};

$(window).load(function() {
    //if we're on the bookshelf, do each section separately
    if (document.getElementById("needtobuy")) {
        evenPics("img-needed");
        equalizeThumbs('.thumb-needed');
        evenPics("img-selling");
        equalizeThumbs('.thumb-selling');
        evenPics("img-owned");
        equalizeThumbs('.thumb-owned');
    } else {
        evenPics("img-responsive");
        equalizeThumbs(".thumbnail");
    }
    });
