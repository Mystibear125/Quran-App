// API URLs
const SURAH_API = `https://quranapi.pages.dev/api/${SURAH_NUMBER}.json`;
const AUDIO_API = `https://cdn.islamic.network/quran/audio/128/ar.alafasy/${SURAH_NUMBER}.mp3`;

// DOM Elements
const loading = document.getElementById('loading');
const surahContent = document.getElementById('surahContent');
const errorState = document.getElementById('errorState');
const audioPlayer = document.getElementById('audioPlayer');
const playPauseBtn = document.getElementById('playPauseBtn');
const progressBar = document.querySelector('.progress-bar');
const progressFill = document.getElementById('progress');
const currentTimeEl = document.getElementById('currentTime');
const durationEl = document.getElementById('duration');
const volumeSlider = document.getElementById('volumeSlider');

// State
let isPlaying = false;
let surahData = null;

// Fetch Surah Data
async function fetchSurahData() {
    try {
        const response = await fetch(SURAH_API);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        surahData = await response.json();
        displaySurahData();
        setupAudio();
        
    } catch (error) {
        console.error('Error fetching surah:', error);
        showError();
    }
}

// Display Surah Data
function displaySurahData() {
    // Update header
    document.getElementById('surahName').textContent = surahData.surahName;
    document.getElementById('surahTranslation').textContent = surahData.surahNameTranslation;
    document.getElementById('surahType').textContent = surahData.revelationType;
    document.getElementById('surahAyahs').textContent = `${surahData.totalAyah} Verses`;
    
    // Update page title
    document.title = `${surahData.surahName} - Al-Qur'an`;
    
    // Display verses
    const versesList = document.getElementById('versesList');
    versesList.innerHTML = '';
    
    surahData.ayahs.forEach((ayah, index) => {
        const verseItem = createVerseElement(ayah, index + 1);
        versesList.appendChild(verseItem);
    });
    
    // Hide loading, show content
    loading.style.display = 'none';
    surahContent.style.display = 'block';
}

// Create Verse Element
function createVerseElement(ayah, number) {
    const div = document.createElement('div');
    div.className = 'verse-item';
    div.innerHTML = `
        <span class="verse-number">Verse ${number}</span>
        <p class="verse-arabic">${ayah.ayahText}</p>
        <p class="verse-translation">${ayah.ayahTextTranslation || 'Translation not available'}</p>
    `;
    return div;
}

// Setup Audio
function setupAudio() {
    audioPlayer.src = AUDIO_API;
    audioPlayer.volume = volumeSlider.value / 100;
    
    // Audio event listeners
    audioPlayer.addEventListener('loadedmetadata', () => {
        durationEl.textContent = formatTime(audioPlayer.duration);
    });
    
    audioPlayer.addEventListener('timeupdate', updateProgress);
    audioPlayer.addEventListener('ended', () => {
        isPlaying = false;
        updatePlayButton();
    });
    
    audioPlayer.addEventListener('error', (e) => {
        console.error('Audio error:', e);
        alert('Failed to load audio. Please try again later.');
    });
}

// Play/Pause Toggle
playPauseBtn.addEventListener('click', togglePlayPause);

function togglePlayPause() {
    if (isPlaying) {
        audioPlayer.pause();
    } else {
        audioPlayer.play();
    }
    isPlaying = !isPlaying;
    updatePlayButton();
}

function updatePlayButton() {
    const icon = playPauseBtn.querySelector('i');
    if (isPlaying) {
        icon.className = 'fa-solid fa-pause';
        playPauseBtn.setAttribute('aria-label', 'Pause');
    } else {
        icon.className = 'fa-solid fa-play';
        playPauseBtn.setAttribute('aria-label', 'Play');
    }
}

// Progress Bar
function updateProgress() {
    const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
    progressFill.style.width = `${progress}%`;
    currentTimeEl.textContent = formatTime(audioPlayer.currentTime);
}

progressBar.addEventListener('click', (e) => {
    const rect = progressBar.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    audioPlayer.currentTime = percent * audioPlayer.duration;
});

// Volume Control
volumeSlider.addEventListener('input', (e) => {
    audioPlayer.volume = e.target.value / 100;
    updateVolumeIcon(e.target.value);
});

function updateVolumeIcon(value) {
    const icon = document.querySelector('.volume-control i');
    if (value == 0) {
        icon.className = 'fa-solid fa-volume-xmark';
    } else if (value < 50) {
        icon.className = 'fa-solid fa-volume-low';
    } else {
        icon.className = 'fa-solid fa-volume-high';
    }
}

// Format Time
function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Show Error
function showError() {
    loading.style.display = 'none';
    errorState.style.display = 'flex';
}

// Keyboard Controls
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && surahContent.style.display !== 'none') {
        e.preventDefault();
        togglePlayPause();
    }
});

// Initialize
fetchSurahData();