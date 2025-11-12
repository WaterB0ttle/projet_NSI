function openNav() {
    document.getElementById("mySidenav").style.width = "25%";
    document.getElementById("mySidenav").style.visibility = "visible";
}
  
function closeNav() {
    document.getElementById("mySidenav").style.width = "0px";
    document.getElementById("mySidenav").style.visibility = "hidden";

}

// let isClicked = true;

// function openOrCloseNav() {
//     isClicked = -isClicked;
//     let a = document.getElementById("mySidenav").style.visibility;  
//     if(a=="visibile") {
//         document.getElementById("mySidenav").style.height = "0";
//         document.getElementById("mySidenav").style.visibility = "hidden";
//     }
//     else if(a=="hidden") {
//         document.getElementById("mySidenav").style.height = "100%";
//         document.getElementById("mySidenav").style.visibility = "visible";
//     }
// }