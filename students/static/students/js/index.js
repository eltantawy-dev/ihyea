


const get = document.getElementById("progress-num");
if (get) {
    const percent = parseInt(get.innerHTML);
    document.getElementById("progress-circular").style.background =
  `conic-gradient(#16a14e  ${percent}%, #4eda6f40 0)`;
}








if (window.innerWidth < 768) {
    const tajweed = document.getElementsByClassName("tajweed")
    const memorization = document.getElementsByClassName("memorization")
    for (let i of tajweed ) {
        i.prepend("تجويد: ")
    }

    for (let i of memorization) {
        i.prepend("حفظ: ")
    }

}