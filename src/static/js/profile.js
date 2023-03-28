function open_popup() {
    var modal = document.getElementById("myModal");
    modal.style.display = "block";
}

function close_hide() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
}
  
  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }