/****************************************************************/

function isFunction(element) {
  return element.classList && element.classList.contains("function");
}

function isFunctionCall(element) {
  return element.classList && element.classList.contains("function-call");
}

function isFunctionBody(element) {
  return element.classList && element.classList.contains("function-body");
}

function isFunctionReturn(element) {
  return element.classList && element.classList.contains("function-return");
}

function isHidden(element) {
  return element.classList && element.classList.contains("hidden");
}

/****************************************************************/

function hideFunctionBody(element) {
  if (isFunctionBody(element)) {
    element.classList.add("hidden");
  }
}

function showFunctionBody(element) {
  if (isFunctionBody(element)) {
    element.classList.remove("hidden");
  }
}

function toggleFunctionBody(element) {
  if (isFunctionBody(element)) {
    element.classList.toggle("hidden");
  }
}

/****************************************************************/

function hideFunction(element) {
  if (isFunction(element)) {
    for (elt of element.children) {
      hideFunctionBody(elt);
    }
  }
}

function showFunction(element) {
  if (isFunction(element)) {
    for (elt of element.children) {
      showFunctionBody(elt);
    }
  }
}

function toggleFunction(element) {
  if (isFunction(element)) {
    for (elt of element.children) {
      toggleFunctionBody(elt);
    }
  }
}

function clickFunction(event) {
  toggleFunction(this);
  if (isFunction(this)) {
    event.stopPropagation();
  }
}

/****************************************************************/

function showClass(event) {
  window.alert(this.getElementsByClassName("function-call").length);
  event.stopPropagation()
}

for (elt of document.getElementsByClassName("function")) {
  elt.addEventListener("click", clickFunction);
}

