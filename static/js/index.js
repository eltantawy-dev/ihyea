const i = document.getElementById("menu-nav-i");
const menu = document.getElementById("menu-nav");
const triangle = document.getElementById("profile-triangle");

if (i){
    i.addEventListener("click", (e) => {
    const clickedInsideButton = i.contains(e.target);
    const menuVisible = window.getComputedStyle(menu).display === "block";

    if (clickedInsideButton) {
        if (menuVisible) {
            menu.style.display = "none";
            triangle.style.display = "none";
            i.className = "fa-solid fa-bars"
        } else {
            menu.style.display = "block";
            triangle.style.display = "block";
            i.className = "fa-solid fa-xmark";
        }
    } else {
        if (menuVisible) {
            menu.style.display = "none";
            triangle.style.display = "none";
        }
    }
});
}


const noteI = document.getElementById("note-i");
const noteMenu = document.getElementById("note-ul");
const noteTriangle = document.getElementById("note-triangle");

if (noteI){
    noteI.addEventListener("click", (e) => {
        const isClicked = noteI.contains(e.target)
        const isVisibleMenu = window.getComputedStyle(noteMenu).display === "block";

        if (isClicked) {
            if (isVisibleMenu) {
                noteMenu.style.display = "none"
                noteTriangle.style.display = "none"
            }
            else {
                noteMenu.style.display = "block"
                noteTriangle.style.display = "block"
            }
        } else {
        if (isVisibleMenu) {
            noteMenu.style.display = "none";
            noteTriangle.style.display = "none";
        }
    }

    });

}




function markAsRead(noteId, callback) {
    fetch(`/student_dash/notifications/mark-read/${noteId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (response.ok) {
            const note = document.getElementById(`note-${noteId}`);
            note.className = "li-True-read-note";
            note.style.opacity = '0.5'; 
             if (callback) callback();
        } else {
            console.error('فشل تحديث حالة الإشعار');
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}








const notes = document.getElementsByClassName("li-True-read-note");
Array.from(notes).forEach(note => {
    note.style.opacity = 0.5;
}
)

function noteIFun(){
    const newNotes = document.getElementsByClassName("li-False-read-note");
    if (newNotes.length > 0) {
        const i = document.getElementById("note-i");
        i.classList.add("show-after");
    } else {
        const i = document.getElementById("note-i");
        if (i){
            i.classList.remove("show-after");

        }
    }
}



function readAndI(noteId){
    markAsRead(noteId, () => {
        noteIFun()
    })

}

noteIFun()


setTimeout(function() {
    const msg = document.getElementById("message-container");
    if (msg) {
      msg.style.display = "none";
    }
  }, 4000);

    document.getElementById("year").textContent = new Date().getFullYear();