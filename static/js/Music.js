waitForElementPresence("#music-player", () => {
    waitForElementPresence("#music-tray-categories", (allCategoriesDiv) => {
        fetch("/music-categories").then((response) => {
            response.json().then((streams) => {
                knownStreams = streams
                knownStreams.forEach((cat)=>{
                    let _split = cat.split("_")
                    let mainCat = _split[0]
                    let subCat = _split[1]
                    if (document.getElementById(mainCat + "-music-category") === null) {
                        let mainCategoryDiv = document.createElement('div');
                        let subCategoryDiv = document.createElement('div');
                        mainCategoryDiv.className = "music-tray-category-grp py-1"
                        mainCategoryDiv.id = mainCat + "-music-category";
                        mainCategoryDiv.innerHTML = mainCat;
                        mainCategoryDiv.style.color = "rgba(255, 255, 255, 0.4)"
                        subCategoryDiv.className = "music-tray-sub-category-grp"
                        subCategoryDiv.id = mainCat + "-music-subcategory"
                        mainCategoryDiv.append(subCategoryDiv);
                        allCategoriesDiv.appendChild(mainCategoryDiv);
                    }
                    let subCatButton = document.createElement('button');
                    subCatButton.className = "music-tray-button-global music-tray-sub-category-button"
                    subCatButton.id = cat
                    subCatButton.innerHTML = subCat
                    subCatButton.style.color = "rgba(255, 255, 255, 0.4)"
                    subCatButton.onclick = () => {playMusicCategory(cat, mainCat).then()}
                    document.getElementById(mainCat + "-music-subcategory").append(subCatButton);
                })
            })
        })
    })
})
waitForElementPresence("#music-tray-toggle-btn", (toggleButton) => {
    toggleButton.addEventListener('click', toggleMusicTray)
})
waitForElementPresence("#music-pp-btn", (playPauseButton) => {
    playPauseButton.addEventListener('click', () => {
        if (window.lastMusicCategory === null) {
            openMusicTray()
        } else {
            toggleMusicMute()
        }
    })
})


let knownStreams = []
window.currentlyPlaying = false
window.lastMusicCategory = null
window.lastMusicMainCategory = null
window.lastMusicSubCategory = null
async function playMusicCategory(category, mainCategory) {
    if (!knownStreams.includes(category)) return null
    if (window.lastMusicCategory === null || category!==window.lastMusicCategory) {
        muteMusic()
        if (window.lastMusicCategory !== null) document.getElementById(window.lastMusicCategory).style.color = "rgba(255, 255, 255, 0.2)";
        if (window.lastMusicMainCategory !== null) document.getElementById(window.lastMusicMainCategory+"-music-category").style.color = "rgba(255, 255, 255, 0.2)";
        document.getElementById(category).style.color = "rgba(255, 255, 255, 1)";
        document.getElementById(mainCategory+"-music-category").style.color = "rgba(255, 255, 255, 1)";
        window.lastMusicCategory = category
        window.lastMusicMainCategory = mainCategory
        document.getElementById('music-player').children[0].src = "/music/" + category
        await document.getElementById('music-player').load()
        unmuteMusic()
        await document.getElementById('music-player').play()
    }
}


function unmuteMusic() {
    if (window.lastMusicCategory === null || document.getElementById('music-player').muted === true) {
        document.getElementById('music-player').volume = 0.08;
        document.getElementById('music-player').muted = false
        document.getElementById('music-pp-btn').querySelector('img').src = '/cd?type=image&name=music-tray-pause.png';
        document.getElementById('music-pp-btn').querySelector('img').alt = 'Pause';
        return true
    }
    return null
}


function muteMusic() {
    if (document.getElementById('music-player').muted === false) {
        document.getElementById('music-player').muted = true
        document.getElementById('music-pp-btn').querySelector('img').src = '/cd?type=image&name=music-tray-resume.png';
        document.getElementById('music-pp-btn').querySelector('img').alt = 'Play';
        return false
    }
    return null
}


function toggleMusicMute() {
    if (!(unmuteMusic() === true)) muteMusic()
}


function openMusicTray() {
    if (document.getElementById('music-tray').classList.contains('collapsed')) {
        document.getElementById('music-tray').classList.toggle('collapsed');
        document.getElementById('music-tray-toggle-btn').querySelector('img').src = '/cd?type=image&name=music-tray-down.png';
        return true
    }
    return null
}


function closeMusicTray() {
    if (!document.getElementById('music-tray').classList.contains('collapsed')) {
        document.getElementById('music-tray').classList.toggle('collapsed');
        document.getElementById('music-tray-toggle-btn').querySelector('img').src = '/cd?type=image&name=music-tray-up.png';
        return false
    }
    return null
}


function toggleMusicTray() {
    if (!(openMusicTray() === true)) closeMusicTray()
}

