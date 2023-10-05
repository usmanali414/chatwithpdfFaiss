var isNavOpen = false;

    function toggleNav() {
        if (isNavOpen) {
            openNav();
        } else {
            closeNav();
        }
    }

    function openNav() {
        document.getElementById("mySidenav").style.width = "300px";
        document.getElementById("main").style.marginLeft = "300px";
        document.getElementById("mySidenav").style.paddingLeft ="20px";
        document.getElementById("mySidenav").style.paddingRight ="20px";

        isNavOpen = false;
    }

    function closeNav() {
        document.getElementById("mySidenav").style.width = "0";
        document.getElementById("main").style.marginLeft= "0";
        document.getElementById("mySidenav").style.paddingLeft ="0";
        document.getElementById("mySidenav").style.paddingRight ="0";
        isNavOpen = true;
    }