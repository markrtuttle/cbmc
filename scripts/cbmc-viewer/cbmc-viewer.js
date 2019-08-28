function expandBlock(event) {
  event.currentTarget.classList.remove("hidden");
}

function expandButton(event) {
  // the button is contained in a span followed by the div with function body
  var elt = event.target.closest(".line").nextElementSibling;
  if (elt) {
    elt.classList.remove("hidden");
  }
  event.stopPropagation();
}

function collapseButton(event) {
  var elt = event.target.closest(".block");
  if (elt) {
    elt.classList.add("hidden");
  }
  event.stopPropagation();
}

function focusButton(event) {
  for (var elt of document.getElementsByClassName("block")) {
    elt.classList.add("hidden");
  }
  event.target.click();
}

function unfocusButton(event) {
  for (var elt of document.getElementsByClassName("block")) {
    elt.classList.remove("hidden");
  }
}
